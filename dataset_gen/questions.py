from utils import SUBJECTS

INTERVIEW_QUESTIONS = [
    {
        "id": "starter",
        "type": "starter",
        "subject": None,
        "main_question": "به نظر شما مهمترین چالش و رنج دوران سالمندی چیه؟",
        "follow_ups": [
            "چی شده که این مساله به نظرتون مهمه؟ (بررسی شناخت)",
            "به نظرتون ریشه و دلیل ایجاد این رنج چیه؟ (بررسی اسناد دهی)",
            "چه احساسی نسبت به این مساله دارید؟ (بررسی هیجان)",
            "با این مسئله چه کار کردید؟ (بررسی رفتار)",
        ],
    },
    {
        "id": "q1",
        "type": "main",
        "subject": SUBJECTS.PHYSICAL_HEALTH_AND_SEXUAL_ISSUES.value,
        "main_question": "در این دوره سنی توانمندی های انسان کاهش پیدا می کند. مثلا سلامت جسمی نسبت به جوانی کمتر میشود. برای شما این اتفاق افتاده؟",
        "follow_ups": [
            "چه احساسی نسبت به این فقدان دارید؟",
            "نظرتون در مورد این کاهش سلامتی چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
    {
        "id": "q2",
        "type": "main",
        "subject": SUBJECTS.LOSS_OF_INDEPENDENCE.value,
        "main_question": " بعضی از افراد در دوره سالمندی به دلیل کاهش توانمندی ها احساس می کنند استقلال کمتری دارند. نظر شما در این باره چیست؟",
        "follow_ups": [
            "چه احساسی نسبت به این مساله دارید؟ ",
            "نظرتون در مورد این مساله چیست؟ ",
            "در این رابطه کاری هم انجام داده اید؟ ",
        ],
    },
    {
        "id": "q3",
        "type": "main",
        "subject": SUBJECTS.LOSS_OF_CLOSE_ONES_AND_FEAR_OF_DEATH.value,
        "main_question": "آیا از دوستان و هم سن و سالان در اقوام کسی رو از دست داده اید؟",
        "follow_ups": [
            "چه احساسی نسبت به این فقدان دارید؟",
            "نظرتون در مورد مرگ چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
    {
        "id": "q4",
        "type": "main",
        "subject": SUBJECTS.LOSS_OF_SOCIAL_ACTIVITY.value,
        "main_question": "شما احتمالا بازنشسته شده اید درست است؟ برای شما این فاصله گرفتن از فضای شغلی و اجتماعی چه طور بوده؟",
        "follow_ups": [
            "چه احساسی نسبت به بازنشستگی دارید؟",
            "نظرتون در مورد بازنشستگی چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
    {
        "id": "q5",
        "type": "main",
        "subject": SUBJECTS.LOSS_OF_INCOME.value,
        "main_question": "ایا به دلیل بازنشستگی و به دنبال کاهش فعالیت های شغلی با مشکلات اقتصادی هم مواجه شده اید؟ چالش های مالی هم داشته اید؟",
        "follow_ups": [
            "چه احساسی نسبت به این مساله دارید؟",
            "نظرتون در مورد این مساله چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
    {
        "id": "q6",
        "type": "main",
        "subject": SUBJECTS.LOSS_OF_FAMILY_CONNECTIONS.value,
        "main_question": "آیا در این دوره سنی رفت و آمدها و ارتباطات خانوادگی و اجتماعی شما نسبت به دوران جوانی کاهش یافته؟",
        "follow_ups": [
            "چه احساسی نسبت به این مساله دارید؟",
            "نظرتون در مورد این مساله چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
    {
        "id": "q7",
        "type": "main",
        "subject": SUBJECTS.LIFESTYLE_CHANGES.value,
        "main_question": "ایا سبک کلی زندگی شما در این دوره از زندگی نسبت به دوره های قبل تغییر کرده؟",
        "follow_ups": [
            "چه احساسی نسبت به این مساله دارید؟",
            "نظرتون در مورد این مساله چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
    {
        "id": "q8",
        "type": "main",
        "subject": SUBJECTS.LIFE_INTEGRITY.value,
        "main_question": "در مورد گذشته و مسیری که در زندگی طی کرده اید چه احساسی دارید؟ اگر به گذشته برمی گشتید همین مسیر را پیش می گرفتید؟",
        "follow_ups": [
            "چه احساسی نسبت به این مساله دارید؟",
            "نظرتون در مورد این مساله چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
    {
        "id": "q9",
        "type": "main",
        "subject": SUBJECTS.LOSS_OF_ASPIRATION.value,
        "main_question": "با چه انگیزه و امیدی صبح ها از خواب بیدار می شوید؟",
        "follow_ups": [
            "چه احساسی نسبت به این مساله دارید؟",
            "نظرتون در مورد این مساله چیست؟",
            "در این رابطه کاری هم انجام داده اید؟",
        ],
    },
]


# Helper functions to work with the questions
def get_starter_question():
    """Return the starter question"""
    return next(q for q in INTERVIEW_QUESTIONS if q["type"] == "starter")


def get_main_questions():
    """Return all main questions (excluding starter)"""
    return [q for q in INTERVIEW_QUESTIONS if q["type"] == "main"]


def get_question_by_id(question_id):
    """Return a specific question by its ID"""
    return next((q for q in INTERVIEW_QUESTIONS if q["id"] == question_id), None)


def get_all_questions():
    """Return all questions including starter and main questions"""
    return INTERVIEW_QUESTIONS


def count_total_questions():
    """Return total number of questions and follow-ups"""
    total_main = len(INTERVIEW_QUESTIONS)
    total_followups = sum(len(q["follow_ups"]) for q in INTERVIEW_QUESTIONS)
    return {
        "main_questions": total_main,
        "follow_up_questions": total_followups,
        "total": total_main + total_followups,
    }
