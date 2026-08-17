import math
import statistics
from collections import Counter


query_count = 0
cache_hits = 0
cache_misses = 0
embeddings_generated = 0
latencies: list[float] = []
failure_counts: Counter[str] = Counter()


def record_query(latency: float) -> None:
    global query_count

    query_count += 1
    latencies.append(latency)


def record_cache_hit() -> None:
    global cache_hits

    cache_hits += 1


def record_cache_miss() -> None:
    global cache_misses

    cache_misses += 1


def record_embeddings_generated(count: int) -> None:
    global embeddings_generated

    embeddings_generated += count


def record_failure(error_type: str) -> None:
    failure_counts[error_type] += 1


def get_metrics() -> dict:
    cache_attempts = cache_hits + cache_misses
    cache_hit_rate = (
        cache_hits / cache_attempts
        if cache_attempts
        else 0.0
    )

    sorted_latencies = sorted(latencies)
    p95_latency = (
        sorted_latencies[math.ceil(len(sorted_latencies) * 0.95) - 1]
        if sorted_latencies
        else 0.0
    )

    return {
        "queries_served": query_count,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_hit_rate": cache_hit_rate,
        "embeddings_generated": embeddings_generated,
        "median_latency": (
            statistics.median(latencies)
            if latencies
            else 0.0
        ),
        "p95_latency": p95_latency,
        "failure_counts": dict(failure_counts),
    }


