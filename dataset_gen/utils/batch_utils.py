"""
Utilities for batch processing with OpenAI Batch API.
"""
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
from openai.types import Batch

from config import DEFAULT_MODEL, TEMPERATURE, TOP_P, PRESENCE_PENALTY, FREQUENCY_PENALTY
from .csv_utils import save_to_csv


class BatchProcessor:
    """Handler for OpenAI Batch API operations."""
    
    def __init__(self, client: OpenAI):
        """
        Initialize batch processor.
        
        Args:
            client: OpenAI client instance
        """
        self.client = client
    
    def create_batch(
        self,
        messages_list: List[List[Dict[str, str]]],
        model: str = DEFAULT_MODEL,
        batch_file_path: str = "batch_input.jsonl",
        description: str = "Batch processing"
    ) -> Batch:
        """
        Create a batch job from a list of message sets.
        
        Args:
            messages_list: List of message sets (each is a list of message dicts)
            model: Model to use
            batch_file_path: Path to save batch input file
            description: Description for the batch
        
        Returns:
            Batch object with job information
        """
        # Step 1: Prepare the batch input file
        with open(batch_file_path, "w", encoding="utf-8") as f:
            for i, messages in enumerate(messages_list):
                batch_request = {
                    "custom_id": f"request-{i+1}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model,
                        "messages": messages,
                        "temperature": TEMPERATURE,
                        "top_p": TOP_P,
                        "presence_penalty": PRESENCE_PENALTY,
                        "frequency_penalty": FREQUENCY_PENALTY
                    }
                }
                f.write(json.dumps(batch_request, ensure_ascii=False) + "\n")
        
        # Step 2: Upload the batch input file
        with open(batch_file_path, "rb") as f:
            batch_input_file = self.client.files.create(
                file=f,
                purpose="batch"
            )
        
        # Step 3: Create the batch
        batch = self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": description}
        )
        
        return batch
    
    def poll_batch_status(self, batch: Batch) -> Optional[Any]:
        """
        Poll batch status and return results if completed.
        
        Args:
            batch: Batch object
        
        Returns:
            File response if completed, None otherwise
        """
        resp = self.client.batches.retrieve(batch.id)
        
        if resp.status == "completed":
            if resp.output_file_id:
                return self.client.files.content(resp.output_file_id)
            elif resp.error_file_id:
                return self.client.files.content(resp.error_file_id)
            else:
                print("Batch completed but no output_file_id")
                return None
        else:
            print(f"Batch status: {resp.status}. Not completed yet.")
            return None
    
    def parse_response(self, resp: Any) -> List[str]:
        """
        Parse batch response into list of content strings.
        
        Args:
            resp: Response from batch API
        
        Returns:
            List of response content strings
        """
        contents = []
        if resp:
            answers = resp.text.split("\n")[:-1]
            
            for batch_answer in answers:
                single_batch_resp = json.loads(batch_answer)
                answer = single_batch_resp['response']['body']['choices'][0]['message']['content']
                contents.append(answer)
        
        return contents
    
    def save_batch_output(
        self,
        batch: Batch,
        output_dir: str = "output",
        prefix: str = "batch_output"
    ) -> Optional[str]:
        """
        Save batch output to CSV file.
        
        Args:
            batch: Batch object
            output_dir: Directory to save output
            prefix: Prefix for output filename
        
        Returns:
            Path to saved file, or None if not completed
        """
        timestamp = time.time()
        output_path = Path(output_dir) / f"{prefix}_{timestamp}.csv"
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        result = self.poll_batch_status(batch)
        if not result:
            print("Batch not completed yet or no output available.")
            return None
        
        parsed = self.parse_response(result)
        
        # Parse JSON responses and collect all personas
        all_personas = []
        for p in parsed:
            try:
                personas = json.loads(p)
                # Handle both single persona dict and list of personas
                if isinstance(personas, list):
                    all_personas.extend(personas)
                else:
                    all_personas.append(personas)
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse response: {p[:100]}...")
                continue
        
        if all_personas:
            save_to_csv(all_personas, str(output_path))
        else:
            print("No valid personas found in batch output.")
            return None
        
        return str(output_path)

