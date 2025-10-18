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
Here’s the translation of your variables and values into **English**:

### 1. **Demographic Information**

* **Age**: integer
* **Gender**: ["Male", "Female", "Non-binary", "Other"]
* **Marital Status**: ["Single", "Married", "Widowed", "Divorced", "Separated"]
* **Children**: number or description (e.g., "None", "1", "2-3", "4+")
* **Living Situation**: ["Living with Family", "Living Alone", "Shared Housing"]

### 2. **Biological Component**

* **General Health**: ["Good", "Average", "Poor"]
* **Chronic Disease**: [None, "High Blood Pressure", "Cardiovascular Diseases", "Type 2 Diabetes", "Arthritis and Joint Pain", "Osteoporosis", "Alzheimer's and Dementia", "Chronic Kidney Disease", "Chronic Obstructive Pulmonary Disease", "Chronic Depression and Anxiety", "Vision and Hearing Problems", "Chronic Liver Failure", "Parkinson's", "Chronic Sleep Disorders", "Chronic Gastrointestinal Issues"]
* **Mobility**: ["Independent", "With Cane or Walker", "In Wheelchair", "Dependent"]
* **Hearing Senses**: ["Good", "Average", "Poor"]
* **Vision Senses**: ["Good", "Average", "Poor"]
* **Daily Energy**: ["High", "Average", "Low"]

### 3. **Psychological Component**

* **Personality Type**: ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
* **Cognitive Status**: ["Healthy Memory", "Mild Forgetfulness", "Alzheimer's"]
* **Dominant Emotion**: ["Happy", "Sad", "Anxious", "Calm"]
* **Emotional Intelligence**: ["Low", "Average", "High"]
* **IQ**: ["Low", "Average", "High"]
* **Attitude Toward Aging**: ["Acceptance", "Resistance", "Meaning-Seeking", "Denial"]

### 4. **Social Component**

* **Main Social Role**: ["Grandfather", "Grandmother", "Retired", "Social Activist"]
* **Social Support**: ["Large Family", "Alone", "Supportive Friends", "Government Support"]
* **Social Participation**: ["Active", "Inactive"]

### 5. **Economic Component**

* **Income**: ["Independent", "Retirement Pension", "Dependent on Children", "No Income"]
* **Economic Decile**: integer 1–10
* **Housing**: ["Own Home", "Rented", "Nursing Home"]

### 6. **Cultural-Value Component**

* **Religion & Sect**: ["Shia Muslim", "Sunni Muslim", "Christian", "Zoroastrian", "Jewish"]
* **Internalized Moral Traits**: list of 2–4 traits (positive or negative)
* **Religiosity Level**: ["Low", "Average", "High"]
* **Ethnicity**: ["Persian", "Azeri", "Kurdish", "Lur", "Baloch", "Arab", "Turkmen", "Gilaki", "Mazandarani", "Qashqai"]
* **Language**: ["Persian", "Azeri", "Kurdish", "Luri", "Balochi", "Arabic", "Turkmen", "Gilaki", "Mazandarani", "Qashqai"]

### 7. **Contextual Component**

* **Important Personal Experiences**: ["Immigration", "Career Success", "Loss of Loved Ones", "War Experience", "Economic Hardship", "Educational Achievement", "Battle with Serious Illness (e.g., Cancer, Chronic Disease)"]
* **Life Satisfaction**: ["Satisfied", "Dissatisfied", "Neutral"]
* **Meaning and Purpose in Old Age**: ["Helping Family", "Spiritual Activities", "Waiting for Death", "Pleasure-Seeking"]


JSON Format:
[
{
  "age": "",
  "gender": "",
  "marital_status": "",
  "children": "",
  "living_situation": "",
  "general_health": "",
  "chronic_disease": "",
  "mobility": "",
  "hearing_senses": "",
  "vision_senses": "",
  "daily_energy": "",
  "personality_type": "",
  "cognitive_status": "",
  "dominant_emotion": "",
  "emotional_intelligence": "",
  "iq": "",
  "attitude_toward_aging": "",
  "main_social_role": "",
  "social_support": "",
  "social_participation": "",
  "income": "",
  "economic_decile": "",
  "housing": "",
  "religion_and_sect": "",
  "internalized_moral_traits": "",
  "religiosity_level": "",
  "ethnicity": "",
  "language": "",
  "important_personal_experiences": "",
  "life_satisfaction": "",
  "meaning_and_purpose_in_old_age": ""
},
...
]
"""
