from dataclasses import dataclass
from typing import Optional


@dataclass
class EngineResponse():
    engine: str
    model: str
    prompt: str
    input: str
    output: str
    input_tokens: int
    output_tokens: int
    temperature: Optional[float]
    top_p: Optional[float]
    top_k: Optional[int]
    max_output_tokens: Optional[int]
    seed: Optional[int]
    context_window: Optional[int]
