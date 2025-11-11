
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from questions import INTERVIEW_QUESTIONS

import os

# Ensure API key is present
assert os.getenv("METIS_API_KEY"), "Please set METIS_API_KEY in your environment or .env file."
openai_wrapper_api_key = os.getenv("METIS_API_KEY")
openai_wrapper_base_url = "https://api.tapsage.com/openai/v1"


SEED = 42
VERSION = "v2.0"

import os
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple

from dotenv import load_dotenv

random.seed(SEED)

ROOT_DIR = Path("./")
KB_DIR = ROOT_DIR / "knowledge_base"
OUT_DIR = ROOT_DIR  / "data" / VERSION

load_dotenv()

print("Env ready for OpenAI-compatible client")

print(f"ROOT_DIR:{ROOT_DIR}")
print(f"KB_DIR:{KB_DIR}")
print(f"OUT_DIR:{OUT_DIR}")

assert os.path.exists(KB_DIR), "KB_DIR must exists"
assert os.path.exists(OUT_DIR), "OUT_DIR must exists"


persona_file = KB_DIR / "personas.json"

with open(persona_file, "r", encoding="utf-8") as f:
    PERSONAS = json.load(f)

print("Loaded personas: ", len(PERSONAS))

SYSTEM_PROMPT_TEMPLATE = (
    """
    شما یک مدل زبانی هستید که باید نقش یک «سالمند ایرانی» را ایفا کنید و به پرسش‌ها به زبان فارسی پاسخ دهید.
    حتماً لحن و ویژگی‌های شخصیتی داده‌شده را رعایت کنید و پاسخ‌ها را طبیعی، منسجم و چندپاراگرافی بنویسید.
    شما باید در این مکالمه نقش زیر را بازی کنید و به همه پرسش‌ها و درخواست‌ها با حفظ کامل شخصیت، لحن، و جهان‌بینی این فرد پاسخ دهید.
    تاریخچه گفتگو داده شده است.
    
    [اطلاعات شخصیت]
    سن: {age}
    جنسیت: {gender}
    تحصیلات: {level_of_education}
    شغل سابق: {occupation}
    وضعیت مالی: {financial_status}
    وضعیت تاهل: {marital_status}
    صفات شخصیتی: {personality_traits}
    پیشینه و سبک زندگی: {background}
    مذهب: {religion}
    سلامت معنوی در موقعیت کاهش استقلال: {spiritual_health_loss_of_independence}
    سلامت معنوی در موقعیت کاهش کنشگری اجتماعی: {spiritual_health_loss_of_social_activity}
    سلامت معنوی با وجود کاهش سلامت جسمی و مشکلات جنسی: {spiritual_health_physical_health_and_sexual_issues}
    سلامت معنوی هنگام مرگ نزدیکان و ترس از مرگ: {spiritual_health_loss_of_close_ones_and_fear_of_death}
    سلامت معنوی در موقعیت کاهش ارتباطات خانوادگی: {spiritual_health_loss_of_family_connections}
    سلامت معنوی در شرایط تغییر سبک زندگی: {spiritual_health_lifestyle_changes}
    سلامت معنوی در موقعیت کاهش درآمد مالی: {spiritual_health_loss_of_income}
    سلامت معنوی در موقعیت بیآرمانی: {spiritual_health_loss_of_aspiration}
    سلامت معنوی در مواجهه با نیاز به یکپارچگی زندگی: {spiritual_health_life_integrity}

    [دستورالعمل‌ها]
    - فقط به فارسی پاسخ بده و اصلا از اصطلاحات و کلمات انگلیسی استفاده نکن
    - از اصطلاحات و لحن متناسب با شخصیت استفاده کن
    - نیازی نیست شخصیت اول صحبت خود سلام یا احوال پرسی کند. شما در میانه یک مصاحبه هستید.
    - از کلمات، اصطلاحات، و مثال‌هایی استفاده کن که با سن، تجربه، و فرهنگ این شخصیت هماهنگ باشد.
    - شخصیت باید در طول مکالمه ثابت بماند و تغییر نکند.
    - اگر کاربر سوالی خارج از تخصص یا تجربه شخصیت پرسید، با توجه به محدودیت‌های دانشی و دیدگاه‌های او پاسخ بده.
    - در لحن نوشتار، سبک گفتاری شخصیت را حفظ کن.
    - پاسخ‌ها باید در یک پاراگراف و ۲ الی ۱۰ جمله باشد.
    """
)


ANSWER_PROMPT = (
    """
    پرسش: {question}

    پاسخ خود را مانند شخصیت تعریف شده بنویس.
    """
)

def build_messages(persona: Dict, history: List[Dict], question: str) -> List:
    system_content = SYSTEM_PROMPT_TEMPLATE.format(**persona)

    history_content = build_history(history)

    human_content = ANSWER_PROMPT.format(question=question)

    messages = [
        SystemMessage(content=system_content),
        *history_content,
        HumanMessage(content=human_content)
    ]

    return messages

def build_history(history: List[Dict]) -> List[BaseMessage]:
    history_messages = []
    for msg in history:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history_messages.append(AIMessage(content=msg["content"]))
    return history_messages
    

# OpenAI-compatible client
TEMPERATURE = 1
TOP_P = 0.9
PRESENCE_PENALTY = 0.3
FREQUENCY_PENALTY = 0.4

class LLMCaller:
    def __init__(self, client: OpenAI):
        self.client = client

    def _role(self, m):
        return "assistant" if m.type == "ai" else "user" if m.type == "human" else "system"
    
    def _text(self, content) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict):
                    parts.append(p.get("text") or p.get("content") or "")
                else:
                    parts.append(str(p))
            return "\n".join(x for x in parts if x)
        return str(content)

    def _build_payload(self, messages: List[BaseMessage]) -> List[ChatCompletionMessageParam]:
        payload = []
        for m in messages:
            if isinstance(m, SystemMessage):
                payload.append(ChatCompletionSystemMessageParam(
                    role="system",
                    content=self._text(m),
                ))
            elif isinstance(m, HumanMessage):
                payload.append(ChatCompletionUserMessageParam(
                    role="user",
                    content=self._text(m),
                ))
            elif isinstance(m, AIMessage):
                payload.append(ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=self._text(m),
                ))
        return payload

    def generate(self, messages: List[BaseMessage], model: str | None = None):
        payload: List[ChatCompletionMessageParam] = self._build_payload(messages)
        model_to_use = model
        resp = self.client.chat.completions.create(
            model=model_to_use,
            temperature=TEMPERATURE,
            # top_p=TOP_P,
            messages=payload,
        )
        return resp

client = OpenAI(
    api_key=openai_wrapper_api_key,
    base_url=openai_wrapper_base_url,
)

llm = LLMCaller(client)

def generate_one(persona: Dict, history: List[Dict], question: str, model: str) -> Dict:
    messages = build_messages(persona, history, question)
    resp = llm.generate(messages, model=model)
    answer = resp.choices[0].message.content
    return {
        "model": model,
        "persona": persona,
        "question": question,
        "answer": answer
    }

# Quick smoke test single call with explicit model
generate_one(PERSONAS[2], [], INTERVIEW_QUESTIONS[1]["main_question"], model="gpt-5-nano")

import itertools
import time
import uuid
from datetime import datetime

SESSION_PREFIX = datetime.now().strftime("%Y%m%d_%H%M%S")


MODELS = [
    # "gpt-5",
    # "grok-3",
    "gpt-5-nano",
    # "gpt-4o",
    # "gemini-2.5-pro-preview-06-05",
]


class DatasetGenerator:
    def __init__(self, personas: List[Dict], interview_questions: List[Dict], models: List[str]):
        self.SAMPLES_PER_COMBO = 1

        self.personas = personas
        self.interview_questions = interview_questions
        self.models = models

        self.all_rows: List[Dict] = []
        self.batch_buffer: List[Dict] = []
        self.error_count = 0

        self.interview_history = []
        self.batch_buffer = []
        self.all_rows = []

    def write_batch(self, batch_rows: List[Dict], model: str, persona_id: int) -> None:
        """Write a batch to a JSONL file."""
        batch_path = OUT_DIR / f"synthetic_elder_fa_{SESSION_PREFIX}_{model}_{persona_id}.jsonl"
        try:
            with open(batch_path, "w", encoding="utf-8") as f:
                for r in batch_rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        except Exception as e:
            print("Write failed:", e)
            raise SystemExit(1)


    def generate_sample(self, model, persona, question):
        for _ in range(self.SAMPLES_PER_COMBO):
            try:
                row = generate_one(persona, self.interview_history, question, model)
                row["id"] = str(uuid.uuid4())

                question_data = {
                    "content": row["question"],
                    "role": "user"
                }
                answer_data = {
                    "content": row["answer"],
                    "role": "assistant"
                }

                # Update interview history
                self.interview_history.append(question_data)
                self.interview_history.append(answer_data)

                # Collect globally and in current batch
                self.all_rows.append(row)
                self.batch_buffer.append(row)

                # Log progress
                print(f"Generated {len(self.batch_buffer)} rows for {model} and {persona['id']}")

                time.sleep(5) # be polite
            except Exception as e:
                print("Generation error:", e)
                self.error_count += 1
                if self.error_count > 10:
                    raise Exception("Too many errors")

    def generate_dataset(self) -> List[Dict]:
        for persona, model in itertools.product(self.personas, self.models):

            # Reset history and batch buffer for each persona-model combo
            self.batch_buffer = []
            self.interview_history = []

            for question in self.interview_questions:
                main_question = question["main_question"]
                follow_ups = question["follow_ups"]

                self.generate_sample(model, persona, main_question)
                for q in follow_ups:
                    self.generate_sample(model, persona, q)

            self.write_batch(self.batch_buffer, model, persona["id"])

        return self.all_rows


start_time = time.time()

dataset_generator = DatasetGenerator(PERSONAS, INTERVIEW_QUESTIONS, MODELS)
rows = dataset_generator.generate_dataset()

print(f"Generated {len(rows)} rows in {time.time() - start_time:.2f} seconds.")

# List saved files for this session by persona-model
saved_files = sorted(
    str(p) for p in OUT_DIR.glob(f"synthetic_elder_fa_{SESSION_PREFIX}_*.jsonl")
)
len(saved_files), saved_files[:10]





