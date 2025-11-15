# Knowledge Base Module

## Business Logic & Purpose

The `knowledge_base` directory contains reference data, statistical information, and domain knowledge used to inform persona generation and ensure cultural authenticity.

## Research Context

This knowledge base supports the research goal of creating **realistic and representative** Iranian elderly personas by providing:

1. **Statistical Data**: Population distributions for demographics
2. **Cultural Knowledge**: Iranian cultural context and norms
3. **Reference Personas**: Example personas for guidance
4. **Subject Matter**: Mental health and spiritual health domain knowledge

## Directory Contents

### `personas.json`

**Purpose**: Reference personas used for testing and as examples.

**Business Logic**:
- Provides examples of complete personas
- Used for testing interview generation
- Serves as template for expected persona structure
- May be used as seed data for variations

### `mental_health_subjects.py`

**Purpose**: Defines mental health and spiritual health subject categories.

**Business Logic**:
- Maps to the 9 spiritual health challenge areas
- Provides structured subject definitions
- Ensures consistency in research categorization

### `mindmap.json`

**Purpose**: Conceptual mapping of spiritual health domains and relationships.

**Business Logic**:
- Visualizes relationships between different spiritual health aspects
- May inform prompt engineering
- Helps understand research domain structure

## Statistical Data

The knowledge base should contain (or reference) Iranian population statistics for:

- **Age Distribution**: Elderly population by age group
- **Gender Distribution**: Male/Female ratios in elderly population
- **Ethnicity Distribution**: Representation of different Iranian ethnic groups
- **Religious Distribution**: Shia/Sunni/other religious affiliations by ethnicity
- **Geographic Distribution**: Regional variations in demographics

**Note**: Some statistical PDFs are stored in `داده‌های آماری جمعتی/` directory.

## Usage in Generation

The knowledge base informs:

1. **Base Persona Generation**: Statistical distributions used in `generate_base_persona()`
2. **Prompt Engineering**: Cultural context in prompts
3. **Validation**: Reference for expected persona structure
4. **Research Design**: Subject categories for interview questions

## Design Principles

1. **Cultural Authenticity**: All data respects Iranian cultural context
2. **Statistical Accuracy**: Demographics reflect real population data
3. **Research Validity**: Supports scientific rigor in persona creation
4. **Completeness**: Covers all relevant demographic and cultural dimensions

