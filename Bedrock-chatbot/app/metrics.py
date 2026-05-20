import time
from dataclasses import dataclass

@dataclass
class CallStats:
    latency_ms: float
    tokens: int
    cost_usd: float


def estimate_cost(tokens: int, price_per_1k_tokens: float = 0.003) -> float:
    """
    Rough cost estimate; replace price with real per-model price.
    """
    return (tokens / 1000.0) * price_per_1k_tokens


def timed_call(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    latency_ms = (end - start) * 1000
    # For now, pretend response tokens ~ MAX_TOKENS; later parse actual metadata
    tokens = kwargs.get("max_tokens", 512)
    cost = estimate_cost(tokens)
    return result, CallStats(latency_ms=latency_ms, tokens=tokens, cost_usd=cost)