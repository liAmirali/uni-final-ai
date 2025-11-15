"""
Interview generation logic for elderly personas.
"""

import uuid
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from prompts.interview_prompts import format_system_prompt, format_answer_prompt
from utils import LLMClient, save_to_csv
from config import DEFAULT_MODEL


class InterviewGenerator:
    """Generator for creating interview responses from personas."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize interview generator.

        Args:
            llm_client: LLM client for generation
        """
        self.llm_client = llm_client

    def _build_history(self, history: List[Dict]) -> List:
        """
        Convert history dicts to langchain messages.

        Args:
            history: List of history dictionaries with 'role' and 'content'

        Returns:
            List of langchain messages
        """
        history_messages = []
        for msg in history:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history_messages.append(AIMessage(content=msg["content"]))
        return history_messages

    def generate_response(
        self,
        persona: Dict,
        question: str,
        history: Optional[List[Dict]] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Generate a response to a question as the given persona.

        Args:
            persona: Persona dictionary
            question: Interview question
            history: Conversation history (optional)
            model: Model to use (defaults to config)

        Returns:
            Generated response text
        """
        history = history or []

        # Build messages
        system_content = format_system_prompt(persona)
        history_messages = self._build_history(history)
        human_content = format_answer_prompt(question)

        messages = [
            SystemMessage(content=system_content),
            *history_messages,
            HumanMessage(content=human_content),
        ]

        # Generate response
        response = self.llm_client.generate(messages, model=model)
        return response.choices[0].message.content

    def generate_full_interview(
        self,
        persona: Dict,
        questions: List[Dict],
        model: Optional[str] = None,
        delay: float = 1.0,
    ) -> List[Dict]:
        """
        Generate a full interview with a persona.

        Args:
            persona: Persona dictionary
            questions: List of question dictionaries with 'main_question' and 'follow_ups'
            model: Model to use (defaults to config)
            delay: Delay between API calls in seconds

        Returns:
            List of interaction dictionaries
        """
        history = []
        interactions = []

        for q in questions:
            main_question = q["main_question"]
            follow_ups = q.get("follow_ups", [])

            # Generate response to main question
            answer = self.generate_response(persona, main_question, history, model)

            interaction = {
                "id": str(uuid.uuid4()),
                "question_id": q.get("id"),
                "question_type": "main",
                "subject": q.get("subject"),
                "question": main_question,
                "answer": answer,
                "model": model or DEFAULT_MODEL,
            }
            interactions.append(interaction)

            # Update history
            history.append({"role": "user", "content": main_question})
            history.append({"role": "assistant", "content": answer})

            time.sleep(delay)

            # Generate responses to follow-up questions
            for follow_up in follow_ups:
                answer = self.generate_response(persona, follow_up, history, model)

                interaction = {
                    "id": str(uuid.uuid4()),
                    "question_id": q.get("id"),
                    "question_type": "follow_up",
                    "subject": q.get("subject"),
                    "question": follow_up,
                    "answer": answer,
                    "model": model or DEFAULT_MODEL,
                }
                interactions.append(interaction)

                # Update history
                history.append({"role": "user", "content": follow_up})
                history.append({"role": "assistant", "content": answer})

                time.sleep(delay)

        return interactions


class DatasetGenerator:
    """Generate complete dataset from personas and questions."""

    def __init__(
        self,
        personas: List[Dict],
        interview_questions: List[Dict],
        models: List[str],
        llm_client: LLMClient,
        output_dir: str = "data/output",
    ):
        """
        Initialize dataset generator.

        Args:
            personas: List of persona dictionaries
            interview_questions: List of interview question dictionaries
            models: List of model names to use
            llm_client: LLM client for generation
            output_dir: Directory to save output files
        """
        self.personas = personas
        self.interview_questions = interview_questions
        self.models = models
        self.llm_client = llm_client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.interview_generator = InterviewGenerator(llm_client)
        self.session_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.all_rows = []
        self.error_count = 0

    def write_batch(self, batch_rows: List[Dict], model: str, persona_id: str) -> None:
        """
        Write a batch of interactions to a CSV file.

        Args:
            batch_rows: List of interaction dictionaries
            model: Model name
            persona_id: Persona identifier
        """
        batch_path = (
            self.output_dir
            / f"synthetic_elder_fa_{self.session_prefix}_{model}_{persona_id}.csv"
        )
        try:
            save_to_csv(batch_rows, str(batch_path))
            print(f"Saved {len(batch_rows)} rows to {batch_path}")
        except Exception as e:
            print(f"Write failed: {e}")
            raise

    def generate_dataset(self, delay: float = 5.0) -> List[Dict]:
        """
        Generate complete dataset for all personas and models.

        Args:
            delay: Delay between API calls in seconds

        Returns:
            List of all interaction dictionaries
        """
        total_combos = len(self.personas) * len(self.models)
        current = 0

        for persona in self.personas:
            for model in self.models:
                current += 1
                print(f"\n{'='*80}")
                print(
                    f"Processing combo {current}/{total_combos}: Persona {persona.get('id', '?')} with {model}"
                )
                print(f"{'='*80}\n")

                try:
                    # Generate full interview
                    interactions = self.interview_generator.generate_full_interview(
                        persona, self.interview_questions, model=model, delay=delay
                    )

                    # Add persona info to each interaction
                    for interaction in interactions:
                        interaction["persona_id"] = persona.get("id")

                    # Write batch
                    self.write_batch(
                        interactions, model, persona.get("id", "unknown_id")
                    )

                    # Collect globally
                    self.all_rows.extend(interactions)

                except Exception as e:
                    print(
                        f"Error processing persona {persona.get('id')} with {model}: {e}"
                    )
                    self.error_count += 1
                    if self.error_count > 10:
                        raise Exception("Too many errors, stopping")

        print(f"\n{'='*80}")
        print(f"Dataset generation complete!")
        print(f"Total interactions: {len(self.all_rows)}")
        print(f"Errors: {self.error_count}")
        print(f"{'='*80}\n")

        return self.all_rows
