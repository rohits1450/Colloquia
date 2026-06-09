from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from src.generation.multi_candidate import MultiCandidateGenerator
from src.config import load_config

app = FastAPI()

# Load project configuration once at startup
cfg = load_config()
generator = MultiCandidateGenerator(config=cfg)

class TranslationRequest(BaseModel):
    english_inputs: List[str]

@app.post("/api/translate-batch")
async def translate_batch(request: TranslationRequest):
    try:
        batch_results = []
        
        # Loop through each sentence submitted from the UI text field
        for sentence in request.english_inputs:
            # Calls your existing multi-candidate logic per sentence
            candidates = generator.generate(sentence)
            
            # Format the structure to match what your UI dashboard expects to render
            sentence_data = {
                "input_text": sentence,
                "candidates": [
                    {
                        "tanglish": cand.tanglish,
                        "temperature": cand.temperature,
                        "retrieved_context": cand.retrieved_context
                    } for cand in candidates
                ]
            }
            batch_results.append(sentence_data)
            
        return {"results": batch_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
