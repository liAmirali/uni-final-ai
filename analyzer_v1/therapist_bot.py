from typing import List, Dict, TypedDict
from langchain.output_parsers import PydanticOutputParser
import json
import os
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from graph.output.models import MentalHealthAnalysis, MentalHealthIndicator

load_dotenv()


class ConversationState(TypedDict):
    messages: List
    current_question_index: int
    user_responses: List[str]
    questions: List[str]
    mindmap: Dict
    mental_health_subjects: Dict
    analysis: MentalHealthAnalysis | None


class LLMCaller:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

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

    def _build_payload(self, messages: List) -> List[ChatCompletionMessageParam]:
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

    def invoke(self, messages: List, model: str | None = None):
        payload: List[ChatCompletionMessageParam] = self._build_payload(messages)
        model_to_use = model or self.model
        resp = self.client.chat.completions.create(
            model=model_to_use,
            temperature=0.7,
            top_p=0.9,
            messages=payload,
        )
        # Return a response object that mimics langchain's response
        class Response:
            def __init__(self, content):
                self.content = content
        return Response(resp.choices[0].message.content)


class TherapistBot:
    def __init__(self):
        # Initialize Aval AI client
        AVALAI_BASE_URL = os.getenv("AVALAI_BASE_URL", "https://api.avalai.ir/v1")
        AVALAI_MODEL = os.getenv("AVALAI_MODEL", "gpt-4o")
        
        client = OpenAI(
            api_key=os.getenv("AVALAI_API_KEY"),
            base_url=AVALAI_BASE_URL,
        )
        
        self.chat = LLMCaller(client, AVALAI_MODEL)

        # Load mental health indicators from mindmap.json
        with open("knowledge_base/mindmap.json", "r", encoding="utf-8") as f:
            self.mindmap = json.load(f)

        # Load mental health indicators description
        with open("knowledge_base/mental_health_subjects.json", "r", encoding="utf-8") as f:
            self.mental_health_subjects = json.load(f)

        # self.questions = [
        #     "از مسیری که در زندگی طی کرده اید و مرور گذشته چه احساسی دارید؟",
        #     "دوره سالمندی را توصیف کنید",
        #     "راضی هستید از این دوره از زندگی تون؟",
        #     "بزرگترین رنج و چالش سالمندی برای شما چی بوده؟",
        #     "در رابطه با کاهش توانمندی های دوره سالمندی چه احساسی داشته اید و چه کار کردید؟",
        #     "شده از دوستان و همسن و سالان شما کسی فوت کنه و شما خیلی اذیت بشید؟",
        #     "بازنشستگی برای شما چه تجربه ای داشته؟",
        #     "در این دوره به دلیل کاهش فعالیت شغلی مشکل اقتصادی پیش نیامده برای شما؟",
        #     "اینکه سبک زندگی تغییر کرده در سالمندی چه تجربه ای داشته برای شما؟",
        # ]
        
        self.questions = [
            "مهم‌ترین چالش‌تون در این دوران چیه؟",
            "به نظرتون اگر وضعیت مالی به گونه‌ای بود که مجبور نبودید کار کنید، چه می‌شد؟",
            "به نظرتون چرا این اتفاق می‌افته؟",
            "احساس شما نسبت به این شرایط مالی چیست؟",
            "آیا کسی از دوستان یا اقوام شما را طی این سال‌ها از دست داده‌اید؟",
            "نظر شما درباره هزینه‌های پزشکی چیست؟",
            "حالا در این سن و سال، بچه‌ها ازدواج کرده‌اند و خودتان و همسرتان تنها هستید؟",
            "آیا ارتباطات اجتماعی‌تان کمرنگ‌تر شده؟",
            "با این حال، چطور می‌گذرانید؟",
            "در آخر، چه پیامی برای جوان‌ها دارید؟"
        ]

        # Create the graph
        self.graph = self._create_graph()

    def _create_graph(self):
        """Create the conversation graph"""
        workflow = StateGraph(ConversationState)

        # Add nodes
        workflow.add_node("greet", self._greet_user)
        workflow.add_node("ask_question", self._ask_question)
        workflow.add_node("get_answer", self._get_answer)
        workflow.add_node("analyze_answer", self._analyze_answer)

        # Add edges
        workflow.set_entry_point("greet")
        workflow.add_edge("greet", "ask_question")
        workflow.add_edge("ask_question", "get_answer")
        workflow.add_edge("get_answer", "analyze_answer")
        workflow.add_conditional_edges(
            "analyze_answer",
            self._should_continue_questions,
            {
                "continue": "ask_question",
                "finish": END,
            },
        )

        return workflow.compile()

    def _greet_user(self, state: ConversationState) -> ConversationState:
        """Greet the user and initialize the conversation"""
        print("🌸 خوش آمدید به سیستم ارزیابی سلامت روان 🌸")
        print("=" * 50)
        print()

        greeting = f"سلام! من {len(self.questions)} سوال از شما خواهم پرسید تا وضعیت سلامت روان شما را ارزیابی کنم. آیا آماده هستید؟"
        print(f"🤖 {greeting}")

        state["messages"] = [AIMessage(content=greeting)]
        state["current_question_index"] = 0
        state["user_responses"] = []
        state["questions"] = self.questions
        state["mindmap"] = self.mindmap
        state["mental_health_subjects"] = self.mental_health_subjects
        state["analysis"] = None

        return state

    def _ask_question(self, state: ConversationState) -> ConversationState:
        """Ask the current question"""
        current_index = state["current_question_index"]
        question = state["questions"][current_index]

        question_text = (
            f"سوال {current_index+1} از {len(state['questions'])}:\n{question}"
        )
        print(f"🤖 {question_text}")

        state["messages"].append(AIMessage(content=question_text))
        return state

    def _get_answer(self, state: ConversationState) -> ConversationState:
        """Get user's answer"""
        print()
        response = input("شما: ")

        if response.lower() in ["خروج", "exit", "quit"]:
            print("خداحافظ!")
            state["current_question_index"] = len(state["questions"])  # Force end
            return state

        state["messages"].append(HumanMessage(content=response))
        state["user_responses"].append(response)
        print()
        return state

    def _analyze_answer(self, state: ConversationState) -> ConversationState:
        """Analyze the current answer using LLM"""
        current_index = state["current_question_index"]
        current_response = state["user_responses"][-1]
        current_question = state["questions"][current_index]

        print("🔍 در حال تحلیل پاسخ...")

        system_prompt = """
        شما یک روانشناس متخصص سالمندان هستید. لطفاً پاسخ زیر را تحلیل کنید و نشانگرهای سلامت روان را شناسایی کنید.

        برای هر نشانگر شناسایی شده، موارد زیر را مشخص کنید:
        - aspect: "emotion" (هیجان)، "belief" (باور)، یا "behavior" (رفتار)
        - subject: موضوع دقیق از نقشه ذهنی
        - based_on_answer: بخشی از پاسخ کاربر که این شناسایی بر اساس آن انجام شده
        - reasoning: توضیح اینکه چرا این نشانگر انتخاب شده از منظق و تحلیل گام به گام پاسخ کاربر

        به عنوان یک روانشناس متخصص سالمندان، پاسخ های کاربر را به صورت جامع و دقیق تحلیل کنید و نشانگرهای سلامت روان را شناسایی کنید.
        گام به گام جواب های کاربر را تحلیل کنید و دلایل منطقی انتخاب را بیان کنید.
        """

        analysis_prompt = f"""
            سوال: {current_question}
            پاسخ کاربر: {current_response}

            نشانگرهای سلامت روان:
            {json.dumps(state["mindmap"], ensure_ascii=False, indent=2)}

            توضیحات موضوعات سلامت روان:
            {json.dumps(state["mental_health_subjects"], ensure_ascii=False, indent=2)}

            لطفاً نشانگرهای سلامت روان را در این پاسخ شناسایی کنید. یک پاسخ می‌تواند چندین نشانگر سالم و یا ناسالم داشته باشد.


            لطفاً پاسخ را در قالب JSON زیر ارائه دهید:
            {{
                "unhealthy": [
                    {{
                        "aspect": "emotion/belief/behavior",
                        "subject": "موضوع از نقشه ذهنی",
                        "based_on_answer": "بخشی از پاسخ کاربر",
                        "reasoning": "توضیح انتخاب"
                    }}
                ],
                "healthy": [
                    {{
                        "aspect": "emotion/belief/behavior", 
                        "subject": "موضوع از نقشه ذهنی",
                        "based_on_answer": "بخشی از پاسخ کاربر",
                        "reasoning": "توضیح انتخاب"
                    }}
                ]
            }}
            """

        try:
            response = self.chat.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=analysis_prompt),
                ]
            )

            analysis_data = response.content

            if not analysis_data or analysis_data == "":
                print(f"⚠️ خطا در تحلیل: {response.content}")
                return state

            print(f"🔍 تحلیل: {analysis_data}")

        except Exception as e:
            print(f"⚠️ خطا در تحلیل: {e}")

        # Move to next question
        state["current_question_index"] += 1
        return state

    def _should_continue_questions(self, state: ConversationState) -> str:
        """Determine if we should continue asking questions"""
        current_index = state["current_question_index"]
        if current_index < len(state["questions"]):
            return "continue"
        else:
            return "finish"

    def run(self):
        """Run the graph-based conversation"""
        initial_state = {
            "messages": [],
            "current_question_index": 0,
            "user_responses": [],
            "questions": self.questions,
            "mindmap": self.mindmap,
            "mental_health_subjects": self.mental_health_subjects,
            "analysis": None,
        }

        # Run the graph
        for event in self.graph.stream(initial_state):
            # The graph handles the flow automatically
            pass
