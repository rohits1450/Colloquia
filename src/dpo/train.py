"""DPO fine-tuning with LoRA on Gemma-2."""

from __future__ import annotations

import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import DPOConfig, DPOTrainer

from src.config import load_config


def _load_dpo_dataset(path: str | Path) -> Dataset:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                records.append(
                    {
                        "prompt": rec["prompt"],
                        "chosen": rec["chosen"],
                        "rejected": rec["rejected"],
                    }
                )
    return Dataset.from_list(records)


def train_dpo(
    dpo_dataset_path: str | Path | None = None,
    config: dict | None = None,
) -> str:
    cfg = config or load_config()
    dpo_cfg = cfg["dpo"]
    gen_cfg = cfg["generation"]
    paths = cfg["paths"]

    dataset_path = dpo_dataset_path or paths["dpo_dataset"]
    output_dir = dpo_cfg["output_dir"]
    model_name = gen_cfg["model"]

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quant_config,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=dpo_cfg["lora_r"],
        lora_alpha=dpo_cfg["lora_alpha"],
        lora_dropout=dpo_cfg["lora_dropout"],
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        task_type="CAUSAL_LM",
        bias="none",
    )
    model = get_peft_model(model, lora_config)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    ref_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quant_config,
        device_map="auto",
        torch_dtype=torch.float16,
    )

    train_dataset = _load_dpo_dataset(dataset_path)

    training_args = DPOConfig(
        output_dir=output_dir,
        per_device_train_batch_size=dpo_cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=dpo_cfg["gradient_accumulation_steps"],
        learning_rate=dpo_cfg["learning_rate"],
        num_train_epochs=dpo_cfg["num_train_epochs"],
        logging_steps=10,
        save_steps=100,
        beta=dpo_cfg["beta"],
        max_length=dpo_cfg["max_length"],
        remove_unused_columns=False,
        fp16=False,
        bf16=False,
        report_to="none",
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=ref_model,
        args=training_args,
        train_dataset=train_dataset,
        processing_class=tokenizer,
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    print(f"DPO LoRA adapter saved to {output_dir}")
    return output_dir
