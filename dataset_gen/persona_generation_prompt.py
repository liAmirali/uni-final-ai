PROMPT = """
You must generate a set of fictional but realistic Iranian elderly personas that represent cultural, geographical, and social diversity in Iran.

Rules:
- All personas must be elderly (age 65–90).
- Diversity must be reflected across all components, but keep the integrity and realism of each persona.
- Personas should reflect cultural and social realities of Iran.
- Reactions and attitudes do not need to be "correct" or "moral"; they may be shaped by culture, personal experience, or limitations.
- Personality traits and psychological states should be consistent with the individual’s background.
- Use the JSON format provided below.
- For every variable, use values consistent with Iranian context.
- Do not omit any variable.

Variable definitions and accepted values:

1. Biological Component (مولفه زیستی)
- General Health (سلامت عمومی): ["خوب", "متوسط", "ضعیف"]
- Chronic Disease (بیماری مزمن): [None, "فشار خون بالا", "بیماری‌های قلبی و عروقی", "دیابت نوع ۲", "آرتروز و درد مفاصل", "پوکی استخوان", "آلزایمر و زوال عقل", "بیماری مزمن کلیه", "بیماری انسدادی مزمن ریه", "افسردگی و اضطراب مزمن", "مشکلات بینایی و شنوایی", "نارسایی مزمن کبد", "پارکینسون", "اختلالات خواب مزمن", "مشکلات گوارشی مزمن"]
- Mobility (توانایی حرکتی): ["مستقل", "با عصا یا واکر", "روی ویلچر", "وابسته"]
- Senses (وضعیت حواس): {"بینایی": "خوب/ضعیف/...", "شنوایی": "خوب/ضعیف/..."}
- Daily Energy (انرژی روزانه): ["بالا", "متوسط", "کم"]

2. Psychological Component (مولفه روانشناختی)
- Personality Type (ویژگی های شخصیتی): ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
- Cognitive Status (وضعیت شناختی): ["حافظه سالم", "فراموشی خفیف", "آلزایمر"]
- Dominant Emotion (هیجان غالب): ["شاد", "غمگین", "مضطرب", "آرام"]
- Emotional Intelligence (میزان هوش هیجانی): ["کم", "متوسط", "زیاد"]
- IQ (میزان هوش): ["کم", "متوسط", "زیاد"]
- Attitude Toward Aging (نگرش به پیری): ["پذیرش", "مقاومت", "معناجویی", "انکار"]

3. Social Component (مولفه اجتماعی)
- Main Social Role (نقش اجتماعی اصلی): ["پدربزرگ", "مادربزرگ", "بازنشسته", "فعال اجتماعی"]
- Social Support (حمایت اجتماعی): ["خانواده پرجمعیت", "تنها", "دوستان حامی", "حمایت دولتی"]
- Social Participation (میزان مشارکت اجتماعی): ["فعال", "غیر فعال"]

4. Economic Component (مولفه اقتصادی)
- Income (درآمد): ["مستقل", "حقوق بازنشستگی", "وابسته به فرزندان", "فاقد درآمد"]
- Economic Decile (دهک اقتصادی): integer 1–10
- Housing (مسکن): ["خانه شخصی", "اجاره‌ای", "خانه سالمندان"]

5. Cultural-Value Component (مولفه‌های ارزشی-فرهنگی)
- Religion & Sect (نوع دین و مذهب): ["مسلمان شیعه", "مسلمان سنی", "مسیحی", "زرتشتی", "کلیمی"]
- Internalized Moral Traits (صفات اخلاقی نهادینه شده): list of 2–4 traits (positive or negative)
- Religiosity Level (سطح دینداری): ["کم", "متوسط", "زیاد"]
- Cultural Identity (هویت فرهنگی): {"قومیت": "...", "زبان": "...", "ملیت": "ایرانی"}

6. Contextual Component (مولفه‌های بافت‌محور)
- Important Personal Experiences (تجارب مهم شخصی): ["مهاجرت", "موفقیت شغلی", "از دست دادن عزیزان", ...]
- Major Historical-Social Events (وقایع مهم تاریخی-اجتماعی): ["جنگ", "انقلاب", "کرونا"]
- Life Satisfaction (میزان رضایت از زندگی): ["راضی", "ناراضی", "بینابین"]
- Meaning and Purpose in Old Age (معنا و هدف در سالمندی): ["کمک به خانواده", "فعالیت معنوی", "انتظار مرگ", "لذت‌جویی"]

JSON Format (use English keys, Farsi values):

[
  {
    "id": <unique integer>,
    "age": <integer 65–90>,
    "gender": "M" یا "F",

    "biological_component": {
      "general_health": "...",
      "chronic_disease": "...",
      "mobility": "...",
      "senses": {"بینایی": "خوب/ضعیف/...", "شنوایی": "خوب/ضعیف/..."},
      "daily_energy": "..."
    },

    "psychological_component": {
      "personality_type": "...",
      "cognitive_status": "...",
      "dominant_emotion": "...",
      "emotional_intelligence": "...",
      "iq": ...,
      "attitude_to_aging": "..."
    },

    "social_component": {
      "main_social_role": "...",
      "social_support": "...",
      "social_participation": "..."
    },

    "economic_component": {
      "income": "...",
      "economic_decile": ...,
      "housing": "..."
    },

    "cultural_value_component": {
      "religion": "...",
      "moral_traits": ["...", "..."],
      "religiosity_level": "...",
      "cultural_identity": { "ethnicity": "...", "language": "...", "nationality": "ایرانی" }
    },

    "contextual_component": {
      "personal_experiences": ["...", "..."],
      "historical_events": ["..."],
      "life_satisfaction": "...",
      "meaning_and_purpose": "..."
    }
  }
]
"""
