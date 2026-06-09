"""Multi-candidate Tanglish translation generation with Gemma-2."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from src.config import load_config
from src.rag.retriever import SlangRetriever


TRANSLATION_SYSTEM = """You are a Tamil-English (Tanglish) colloquial translator.
Translate the given English sentence into natural spoken Tanglish — mixing Tamil script
with common English words the way young urban Tamilians actually talk in Chennai/Madurai.
Avoid robotic literal translations. Keep it casual and conversational."""


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

        model_name = gen_cfg["model"]
        load_4bit = gen_cfg.get("load_in_4bit", True)

        if load_4bit:
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quant_config,
                device_map="auto",
                torch_dtype=torch.float16,
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
            )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def _generate_one(self, prompt: str, temperature: float) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=self.top_p,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        generated = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1] :],
            skip_special_tokens=True,
        )
        return generated.strip().split("\n")[0].strip()

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

    def generate_batch_to_file(
        self,
        english_inputs: List[str],
        output_path: str | Path,
    ) -> int:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0

        with output_path.open("w", encoding="utf-8") as f:
            for eng in english_inputs:
                for cand in self.generate(eng):
                    record = {
                        "english": cand.english,
                        "tanglish": cand.tanglish,
                        "temperature": cand.temperature,
                        "retrieved_context": cand.retrieved_context,
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1
        return count
