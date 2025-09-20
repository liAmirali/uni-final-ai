import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from therapist_bot import TherapistBot, LLMCaller
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from dotenv import load_dotenv
from interviews import INTERVIEWS
import time

load_dotenv()

class BatchInterviewProcessor:
    def __init__(self, output_dir: str = "analysis_results", max_retries: int = 3):
        self.therapist_bot = TherapistBot()
        self.output_dir = output_dir
        self.max_retries = max_retries
        
        # Statistics tracking
        self.stats = {
            "total_questions": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "retry_attempts": 0,
            "errors_by_type": {}
        }
        
        # Initialize Aval AI client for direct API calls
        AVALAI_BASE_URL = os.getenv("AVALAI_BASE_URL", "https://api.avalai.ir/v1")
        AVALAI_MODEL = os.getenv("AVALAI_MODEL", "gpt-4o")
        
        self.client = OpenAI(
            api_key=os.getenv("AVALAI_API_KEY"),
            base_url=AVALAI_BASE_URL,
        )
        self.model = AVALAI_MODEL
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def process_interview(self, questions: List[str], answers: List[str], interview_id: Optional[str] = None) -> Dict:
        """
        Process a single interview with separate question and answer lists
        
        Args:
            questions: List of questions
            answers: List of answers (must be same length as questions)
            interview_id: Optional identifier for the interview
            
        Returns:
            Dictionary containing all analysis results
        """
        if interview_id is None:
            interview_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Validate that questions and answers have the same length
        if len(questions) != len(answers):
            raise ValueError(f"Questions list ({len(questions)}) and answers list ({len(answers)}) must have the same length")
        
        print(f"🔄 Processing Interview: {interview_id}")
        print("=" * 50)
        
        # Initialize conversation state
        state = {
            "messages": [],
            "current_question_index": 0,
            "user_responses": [],
            "questions": questions,
            "mindmap": self.therapist_bot.mindmap,
            "mental_health_subjects": self.therapist_bot.mental_health_subjects,
            "analysis": None,
        }
        
        all_analyses = []
        
        # Process each question-answer pair
        for i, (question, answer) in enumerate(zip(questions, answers)):
            print(f"\n📝 Question {i+1}/{len(questions)}: {question}")
            print(f"💬 Answer: {answer}")
            
            # Update statistics
            self.stats["total_questions"] += 1
            
            # Update state for current question
            state["current_question_index"] = i
            state["user_responses"].append(answer)
            state["messages"].append(AIMessage(content=question))
            state["messages"].append(HumanMessage(content=answer))
            
            # Analyze the answer
            analysis = self._analyze_single_answer(state, question, answer)
            if analysis:
                all_analyses.append({
                    "question_number": i + 1,
                    "question": question,
                    "answer": answer,
                    "analysis": analysis
                })
            

            # Sleep for 5 seconds
            time.sleep(5)
        
        # Compile final results
        results = {
            "interview_id": interview_id,
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(questions),
            "analyses": all_analyses,
            "processing_stats": self.stats.copy()
        }
        
        # Save results to file
        self._save_results(results, interview_id)
        
        print(f"\n✅ Interview {interview_id} processed successfully!")
        print(f"📁 Results saved to: {self.output_dir}/{interview_id}_analysis.json")
        
        return results
    
    def _analyze_single_answer(self, state: Dict, question: str, answer: str) -> Dict:
        """
        Analyze a single question-answer pair with retry logic
        """
        print("🔍 Analyzing answer...")
        
        system_prompt = """
        شما یک روانشناس متخصص سالمندان هستید. لطفاً پاسخ زیر را تحلیل کنید و نشانگرهای سلامت روان را شناسایی کنید.

        برای هر نشانگر شناسایی شده، موارد زیر را مشخص کنید:
        - aspect: "emotion" (هیجان)، "belief" (باور)، یا "behavior" (رفتار)
        - subject: موضوع دقیق از نقشه ذهنی
        - based_on_answer: بخشی از پاسخ کاربر که این شناسایی بر اساس آن انجام شده
        - reasoning: توضیح اینکه چرا این نشانگر انتخاب شده از منظر روانشناسی

        به عنوان یک روانشناس متخصص سالمندان، پاسخ های کاربر را به صورت جامع و دقیق تحلیل کنید و نشانگرهای سلامت روان را شناسایی کنید.
        """

        analysis_prompt = f"""
            سوال: {question}
            پاسخ کاربر: {answer}

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

        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Analysis attempt {attempt + 1}/{self.max_retries}")
                
                # Use Aval AI client directly with proper message types
                messages = [
                    ChatCompletionSystemMessageParam(role="system", content=system_prompt),
                    ChatCompletionUserMessageParam(role="user", content=analysis_prompt)
                ]
                
                # Adjust parameters based on retry attempt
                temperature = 0.7 + (attempt * 0.1)  # Increase temperature slightly on retries
                top_p = 0.9 - (attempt * 0.05)  # Decrease top_p slightly on retries
                
                print(f"📊 Using temperature: {min(temperature, 1.0):.2f}, top_p: {max(top_p, 0.5):.2f}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=min(temperature, 1.0),  # Cap at 1.0
                    top_p=max(top_p, 0.5),  # Cap at 0.5
                    messages=messages,
                )

                # Handle response content
                content = response.choices[0].message.content
                analysis_text = content.strip() if content else ""
                
                if not analysis_text:
                    print(f"⚠️ Empty response on attempt {attempt + 1}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        return {"error": "Empty response after all retries"}
                
                # Try to parse JSON from the response
                try:
                    # Extract JSON from the response if it's wrapped in markdown or other text
                    if "```json" in analysis_text:
                        json_start = analysis_text.find("```json") + 7
                        json_end = analysis_text.find("```", json_start)
                        analysis_text = analysis_text[json_start:json_end].strip()
                    elif "```" in analysis_text:
                        json_start = analysis_text.find("```") + 3
                        json_end = analysis_text.find("```", json_start)
                        analysis_text = analysis_text[json_start:json_end].strip()
                    
                    analysis_data = json.loads(analysis_text)
                    print("✅ Analysis completed successfully")
                    self.stats["successful_analyses"] += 1
                    return analysis_data
                    
                except json.JSONDecodeError as je:
                    print(f"⚠️ JSON parsing error on attempt {attempt + 1}: {je}")
                    print(f"Raw response: {analysis_text}")
                    
                    if attempt < self.max_retries - 1:
                        print("🔄 Retrying with different parameters...")
                        self.stats["retry_attempts"] += 1
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        self.stats["failed_analyses"] += 1
                        self.stats["errors_by_type"]["JSON parsing"] = self.stats["errors_by_type"].get("JSON parsing", 0) + 1
                        return {
                            "error": "JSON parsing failed after all retries",
                            "raw_response": analysis_text
                        }

            except Exception as e:
                error_type = type(e).__name__
                print(f"⚠️ Analysis error on attempt {attempt + 1} ({error_type}): {e}")
                
                if attempt < self.max_retries - 1:
                    # Different wait times based on error type
                    if "rate" in str(e).lower() or "limit" in str(e).lower():
                        wait_time = 5 + (attempt * 2)  # Longer wait for rate limits
                        print(f"🔄 Rate limit detected, waiting {wait_time} seconds before retry...")
                    else:
                        wait_time = 2 + attempt  # Progressive backoff for other errors
                        print(f"🔄 Retrying in {wait_time} seconds...")
                    
                    self.stats["retry_attempts"] += 1
                    time.sleep(wait_time)
                    continue
                else:
                    self.stats["failed_analyses"] += 1
                    self.stats["errors_by_type"][error_type] = self.stats["errors_by_type"].get(error_type, 0) + 1
                    return {
                        "error": f"Analysis failed after {self.max_retries} attempts: {error_type}: {str(e)}",
                        "error_type": error_type,
                        "attempts": self.max_retries
                    }
        
        # This should never be reached, but just in case
        return {"error": "Unexpected error in retry logic"}
    
    def _save_results(self, results: Dict, interview_id: str):
        """
        Save analysis results to a JSON file
        """
        filename = f"{interview_id}_analysis.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def process_multiple_interviews(self, interviews_data: List[Dict[str, List[str]]]) -> List[Dict]:
        """
        Process multiple interviews
        
        Args:
            interviews_data: List of interviews, each containing dict with 'questions' and 'answers' keys
                            Format: [{'questions': [...], 'answers': [...]}, ...]
            
        Returns:
            List of analysis results for each interview
        """
        all_results = []
        
        for i, interview_data in enumerate(interviews_data):
            interview_id = f"interview_{interview_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            questions = interview_data['questions']
            answers = interview_data['answers']
            results = self.process_interview(questions, answers, interview_id)
            all_results.append(results)
            
            print(f"\n{'='*50}")
        
        return all_results
    
    def print_statistics(self):
        """Print processing statistics"""
        print("\n📊 Processing Statistics:")
        print("=" * 40)
        print(f"Total questions processed: {self.stats['total_questions']}")
        print(f"Successful analyses: {self.stats['successful_analyses']}")
        print(f"Failed analyses: {self.stats['failed_analyses']}")
        print(f"Total retry attempts: {self.stats['retry_attempts']}")
        
        if self.stats['errors_by_type']:
            print("\nErrors by type:")
            for error_type, count in self.stats['errors_by_type'].items():
                print(f"  - {error_type}: {count}")
        
        success_rate = (self.stats['successful_analyses'] / self.stats['total_questions'] * 100) if self.stats['total_questions'] > 0 else 0
        print(f"\nSuccess rate: {success_rate:.1f}%")


def main():
    """
    Main function to run the batch processor
    
    Example usage for single interview:
        processor = BatchInterviewProcessor()
        questions = ["Question 1", "Question 2"]
        answers = ["Answer 1", "Answer 2"] 
        results = processor.process_interview(questions, answers)
    
    Example usage for multiple interviews:
        interviews = [
            {"questions": [...], "answers": [...]},
            {"questions": [...], "answers": [...]}
        ]
        results = processor.process_multiple_interviews(interviews)
    """
    processor = BatchInterviewProcessor()
    
    print("🚀 Starting Batch Interview Processing")
    print("=" * 60)
    
    # Process all interviews
    results = processor.process_multiple_interviews(INTERVIEWS[7:])
    
    print(f"\n🎉 All interviews processed!")
    print(f"📊 Total interviews: {len(results)}")
    print(f"📁 Results saved in: {processor.output_dir}/")
    
    # Print final statistics
    processor.print_statistics()


if __name__ == "__main__":
    main()
