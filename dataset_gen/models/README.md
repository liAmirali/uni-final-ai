# Models Module

## Business Logic & Purpose

The `models` module defines the data structures and enums used throughout the dataset generation system. These models ensure type safety, consistency, and provide a clear schema for persona and interview data.

## Research Context

The models represent the conceptual framework for studying spiritual health in Iranian elderly populations:

- **Persona Model**: Comprehensive representation of an elderly Iranian person
- **Subject Enum**: Categories of spiritual health challenges being studied

## Module Components

### `persona.py`

**Business Purpose**: Defines the complete persona data structure.

**PersonaDetails Class**: A dataclass representing all attributes of an Iranian elderly persona.

**Component Categories**:

1. **Demographic Information**
   - `age`: Integer (65-95)
   - `gender`: "Male" or "Female"
   - `marital_status`: Marital situation
   - `children`: Number of children
   - `living_situation`: Living arrangement

2. **Biological Component**
   - Health status, chronic diseases, mobility, sensory functions
   - Represents physical capabilities and limitations

3. **Psychological Component**
   - Personality type (MBTI), cognitive status, emotional state
   - Represents mental and emotional characteristics

4. **Social Component**
   - Social role, support systems, participation level
   - Represents social connections and engagement

5. **Economic Component**
   - Income sources, economic decile, housing situation
   - Represents financial security and resources

6. **Cultural-Value Component**
   - Religion, religiosity, moral traits, ethnicity, language
   - Represents cultural identity and values

7. **Contextual Component**
   - Life experiences, satisfaction, meaning/purpose
   - Represents life history and current outlook

**Business Logic**:
- Complete persona enables realistic interview responses
- All components influence how persona responds to spiritual health questions
- Cultural component is especially important for Iranian context

**Code Features**:
- `to_dict()`: Convert to dictionary
- `to_json()`: Serialize to JSON
- `from_dict()`: Deserialize from dictionary

### `enums.py`

**Business Purpose**: Defines research subject categories for spiritual health assessment.

**SUBJECTS Enum**: Represents the 9 key areas of spiritual health challenges:

1. **LOSS_OF_INDEPENDENCE**: Reduced autonomy in daily life
2. **LOSS_OF_SOCIAL_ACTIVITY**: Decreased social engagement
3. **PHYSICAL_HEALTH_AND_SEXUAL_ISSUES**: Health and intimacy challenges
4. **LOSS_OF_CLOSE_ONES_AND_FEAR_OF_DEATH**: Grief and mortality concerns
5. **LOSS_OF_FAMILY_CONNECTIONS**: Reduced family relationships
6. **LIFESTYLE_CHANGES**: Adaptations to aging
7. **LOSS_OF_INCOME**: Financial challenges
8. **LOSS_OF_ASPIRATION**: Reduced motivation and purpose
9. **LIFE_INTEGRITY**: Reflection on life path and choices

**Business Logic**:
- These subjects represent common challenges in elderly spiritual health
- Each subject has associated interview questions
- Personas have spiritual health indicators for each subject
- Research analyzes how different personas respond to these challenges

**Usage**:
```python
from models import SUBJECTS

# Access subject values
SUBJECTS.LOSS_OF_INDEPENDENCE.value  # "loss_of_independence"
```

## Data Flow

```
PersonaDetails (Model)
    ↓
Dictionary (Generation)
    ↓
CSV (Storage)
    ↓
Dictionary (Loading)
    ↓
Interview Generation
```

## Type Safety

The models provide:
- **Clear schema**: All fields defined with types
- **Validation**: Dataclass ensures required fields
- **Serialization**: Easy conversion to/from JSON/CSV
- **Documentation**: Field names and structure are self-documenting

## Research Implications

The persona model enables:
1. **Diversity**: Represents various Iranian elderly populations
2. **Consistency**: Same structure across all personas
3. **Analysis**: Structured data enables statistical analysis
4. **Validation**: Can verify data completeness and correctness

