import statistics

query_count = 0
cache_hits = 0
latencies = []

def record_query(latency: float) -> None:
    global query_count

    query_count += 1 
    latencies.append(latency)

def record_cache_hit() -> None:
    global cache_hits

    cache_hits += 1

def get_metrics() -> dict[str, int | float]:
    if latencies:
        median_latency = statistics.median(latencies)

    else:
        median_latency = 0.0

    return{
        "queries_served":query_count,
        "cache_hits":cache_hits,
        "median_latency":median_latency
    }



