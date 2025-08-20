from pydantic import BaseModel, Field
from typing import List

class MentalHealthIndicator(BaseModel):
    aspect: str = Field(description="The aspect of mental health: 'emotion', 'belief', or 'behavior'")
    subject: str = Field(description="The specific subject from the mind map that was identified")
    based_on_answer: str = Field(description="The specific part of the user's answer that led to this identification")
    reasoning: str = Field(description="Explanation of why this indicator was selected based on the user's response")

class MentalHealthAnalysis(BaseModel):
    unhealthy: List[MentalHealthIndicator] = Field(description="List of unhealthy mental health indicators identified")
    healthy: List[MentalHealthIndicator] = Field(description="List of healthy mental health indicators identified")
    overall_assessment: str = Field(description="Overall assessment of the user's mental health status")
    recommendations: List[str] = Field(description="Practical recommendations for improvement")
