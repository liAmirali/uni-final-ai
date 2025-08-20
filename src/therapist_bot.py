from typing import List, Dict, TypedDict
from langchain.output_parsers import PydanticOutputParser
import json
from langchain_google_genai import ChatGoogleGenerativeAI
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


class TherapistBot:
    def __init__(self):
        self.chat = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_output_tokens=9999999,
        )

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
            "به نظر شما مهم‌ترین چالش و رنج دوران سالمندی چیه؟"
            "چی شده که به نظرتون فقرو نداری مهمه؟",
            "به نظرتون ریشه و دلیل ایجاد این رنج چیه؟",
            "چه احساسی نسبت به این مساله دارید؟",
            "برای این مسئله چه کار کردید؟",
            " در این دوره سنی توانمندی‌های انسان کاهش پیدا می‌کند. مثلاً سلامت جسمی نسبت به جوانی کمتر می‌شود. برای شما این اتفاق افتاده؟  چه احساسی نسبت به این فقدان دارید؟",
            "بعضی از افراد در دوره سالمندی توانایی‌های شناختی و ذهنی شان کاهش پیدا می‌کند. مثلاً ممکن است احساس گیج شدن یا کاهش حافظه و تمرکز داشته باشند آیا شما این اتفاق را تجربه کرده اید؟",
            "آیا از دوستان و هم سن و سالان در اقوام کسی رو از دست داده ‌اید؟",
            "شما احتمالاً بازنشسته شده اید درست است؟ برای شما این فاصله گرفتن از فضای شغلی چه طور بوده؟",
            "آیا در این دوره سنی رفت و آمدها و ارتباطات اجتماعی شما نسبت به دوران جوانی کاهش یافته؟ ",
            "آیا سبک کلی زندگی شما در این دوره از زندگی  نسبت به دوره‌های قبل تغییر کرده؟ خب یه چیزهایی خوب شده یه چیزهایی بد. قبلا خیلی پابند خانواده نبودم پی دوست و رفیق بودم که چه قدرم اشتباه بود کجان الان اون رفیق ها که همه چی به پاشون ریختم؟",
            "در مورد گذشته و مسیری که در زندگی طی کرده اید چه احساسی دارید؟ اگر به گذشته برمی‌گشتید همین مسیر را پیش می گرفتید؟",
            "با چه انگیزه و امیدی صبح‌ها از خواب بیدار می‌شوید؟",
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
        گام به گام جواب های کاربر را تحلیل کنید و نشانگرهای سلامت روان را شناسایی کنید.
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
