"""Multi-candidate Tanglish translation generation with Gemma-2."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from tenacity import retry, stop_after_attempt, wait_random_exponential
from dotenv import load_dotenv
from groq import Groq

from src.config import load_config
from src.rag.retriever import SlangRetriever

load_dotenv()


TRANSLATION_SYSTEM = """You are a Tamil-English (Tanglish) colloquial translator.
Translate the given English sentence into natural spoken Tanglish code-mixing the way young urban Tamilians actually talk in Chennai/Madurai.
Avoid robotic literal translations. Keep it casual and conversational.

CRITICAL CONSTRAINTS:
1. Output ONLY the final Tanglish translation. Do not include any explanations, breakdowns, formatting notes, or introductory text.
2. Write the Tanglish output using ONLY the Latin/English alphabet. Do not use Tamil script characters."""


def build_translation_prompt(english_input: str, slang_context: str) -> str:
    return f"""{TRANSLATION_SYSTEM}

{slang_context}

English input: {english_input}

Tanglish translation:"""


@dataclass
class TranslationCandidate:
    english: str
    tanglish: str
    temperature: float
    retrieved_context: str


class MultiCandidateGenerator:
    """Generate multiple Tanglish translation variations using Gemma-2."""

    def __init__(self, config: dict | None = None, retriever: SlangRetriever | None = None):
        cfg = config or load_config()
        self.cfg = cfg
        gen_cfg = cfg["generation"]

        self.num_candidates = gen_cfg["num_candidates"]
        temps = gen_cfg.get("temperature_range", [0.5, 0.8, 1.0, 1.2])
        self.temperatures = temps[: self.num_candidates]
        while len(self.temperatures) < self.num_candidates:
            self.temperatures.append(self.temperatures[-1] + 0.2)

        self.max_new_tokens = gen_cfg["max_new_tokens"]
        self.top_p = gen_cfg.get("top_p", 0.9)
        self.retriever = retriever or SlangRetriever(cfg)

        self.model_name = gen_cfg.get("model", "llama3-70b-8192")
        self.client = Groq()

    def _generate_one(self, prompt: str, temperature: float) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": TRANSLATION_SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=self.max_new_tokens
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def generate(self, english_input: str) -> List[TranslationCandidate]:
        slang_context = self.retriever.format_context(english_input)
        prompt = build_translation_prompt(english_input, slang_context)

        candidates = []
        for temp in self.temperatures:
            tanglish = self._generate_one(prompt, temperature=temp)
            candidates.append(
                TranslationCandidate(
                    english=english_input,
                    tanglish=tanglish,
                    temperature=temp,
                    retrieved_context=slang_context,
                )
            )
        return candidates

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def _generate_one_safe(self, prompt: str, temperature: float) -> str:
        """Wrapper with exponential backoff retry to handle Groq 429 Rate Limits."""
        return self._generate_one(prompt, temperature)

    def process_single_input(self, eng: str) -> List[dict]:
        """Processes a single string and prepares candidate json records."""
        slang_context = self.retriever.format_context(eng)
        prompt = build_translation_prompt(eng, slang_context)
        
        records = []
        for temp in self.temperatures:
            # Call the safe rate-limit guarded function
            tanglish = self._generate_one_safe(prompt, temperature=temp)
            records.append({
                "english": eng,
                "tanglish": tanglish,
                "temperature": temp,
                "retrieved_context": slang_context,
            })
        return records

    def generate_batch_to_file(
        self,
        english_inputs: List[str],
        output_path: str | Path,
    ) -> int:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        
        # Dynamic max_workers based on config
        max_workers = self.cfg["generation"].get("max_workers", 4)

        # Open file in streaming append mode
        with output_path.open("w", encoding="utf-8") as f:
            # Execute API paths in parallel threads
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self.process_single_input, eng): eng for eng in english_inputs}
                
                for future in as_completed(futures):
                    try:
                        records = future.result()
                        for record in records:
                            f.write(json.dumps(record, ensure_ascii=False) + "\n")
                            count += 1
                    except Exception as e:
                        print(f"Failed processing sentence: {str(e)}")
                        
        return count
