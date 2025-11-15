"""
Interview generation logic for elderly personas.
"""

import uuid
import json
import time
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from prompts.interview_prompts import format_system_prompt, format_answer_prompt
from utils import LLMClient, save_to_csv
from config import DEFAULT_MODEL

# Get logger for this module
logger = logging.getLogger(__name__)


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
        model_name = model or DEFAULT_MODEL
        persona_id = persona.get("id", "unknown")

        logger.debug(f"Generating response for persona {persona_id} using model '{model_name}'")
        logger.debug(f"Question: {question[:100]}...")
        logger.debug(f"History length: {len(history)} messages")

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
        logger.debug(f"Sending request to model '{model_name}'...")
        response = self.llm_client.generate(messages, model=model)
        answer = response.choices[0].message.content
        
        logger.debug(f"Received response from '{model_name}' ({len(answer)} characters)")
        logger.debug(f"Answer preview: {answer[:150]}...")
        
        return answer

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
        model_name = model or DEFAULT_MODEL
        persona_id = persona.get("id", "unknown")
        logger.info(f"Starting interview generation for persona {persona_id} with {len(questions)} questions")
        
        history = []
        interactions = []

        for idx, q in enumerate(questions, 1):
            main_question = q["main_question"]
            follow_ups = q.get("follow_ups", [])
            subject = q.get("subject", "unknown")

            logger.info(f"Processing question {idx}/{len(questions)}: {subject}")
            logger.debug(f"Main question: {main_question[:100]}...")

            # Generate response to main question
            answer = self.generate_response(persona, main_question, history, model)

            interaction = {
                "id": str(uuid.uuid4()),
                "question_id": q.get("id"),
                "question_type": "main",
                "subject": subject,
                "question": main_question,
                "answer": answer,
                "model": model_name,
            }
            interactions.append(interaction)
            logger.debug(f"Added main question interaction (total: {len(interactions)})")

            # Update history
            history.append({"role": "user", "content": main_question})
            history.append({"role": "assistant", "content": answer})

            if delay > 0:
                logger.debug(f"Waiting {delay}s before next API call...")
                time.sleep(delay)

            # Generate responses to follow-up questions
            if follow_ups:
                logger.debug(f"Processing {len(follow_ups)} follow-up question(s)")
            for follow_idx, follow_up in enumerate(follow_ups, 1):
                logger.debug(f"Follow-up {follow_idx}/{len(follow_ups)}: {follow_up[:80]}...")
                answer = self.generate_response(persona, follow_up, history, model)

                interaction = {
                    "id": str(uuid.uuid4()),
                    "question_id": q.get("id"),
                    "question_type": "follow_up",
                    "subject": subject,
                    "question": follow_up,
                    "answer": answer,
                    "model": model_name,
                }
                interactions.append(interaction)
                logger.debug(f"Added follow-up interaction (total: {len(interactions)})")

                # Update history
                history.append({"role": "user", "content": follow_up})
                history.append({"role": "assistant", "content": answer})

                if delay > 0:
                    logger.debug(f"Waiting {delay}s before next API call...")
                    time.sleep(delay)

        logger.info(f"Completed interview for persona {persona_id}: {len(interactions)} interactions generated")
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
        logger.info(f"Saving {len(batch_rows)} interactions to {batch_path.name}...")
        try:
            save_to_csv(batch_rows, str(batch_path))
            logger.info(f"✓ Saved {len(batch_rows)} rows to {batch_path}")
        except Exception as e:
            logger.error(f"Write failed: {e}", exc_info=True)
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
                persona_id = persona.get('id', '?')
                logger.info(f"\n{'='*80}")
                logger.info(f"Processing combo {current}/{total_combos}: Persona {persona_id} with {model}")
                logger.info(f"{'='*80}")

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
                    logger.info(f"✓ Completed combo {current}/{total_combos}: {len(interactions)} interactions")

                except Exception as e:
                    logger.error(f"Error processing persona {persona_id} with {model}: {e}", exc_info=True)
                    self.error_count += 1
                    if self.error_count > 10:
                        logger.error("Too many errors, stopping generation")
                        raise Exception("Too many errors, stopping")

        logger.info(f"\n{'='*80}")
        logger.info(f"Dataset generation complete!")
        logger.info(f"Total interactions: {len(self.all_rows)}")
        logger.info(f"Errors: {self.error_count}")
        logger.info(f"{'='*80}\n")

        return self.all_rows
