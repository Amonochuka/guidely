import unittest

from services import metrics


class MetricsTests(unittest.TestCase):
    def setUp(self):
        metrics.query_count = 0
        metrics.cache_hits = 0
        metrics.cache_misses = 0
        metrics.embeddings_generated = 0
        metrics.latencies = []
        metrics.failure_counts.clear()

    def test_reports_latency_cache_and_failure_metrics(self):
        metrics.record_query(1.0)
        metrics.record_query(2.0)
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        metrics.record_embeddings_generated(3)
        metrics.record_failure("empty_query")

        result = metrics.get_metrics()

        self.assertEqual(result["queries_served"], 2)
        self.assertEqual(result["median_latency"], 1.5)
        self.assertEqual(result["p95_latency"], 2.0)
        self.assertEqual(result["cache_hit_rate"], 0.5)
        self.assertEqual(result["embeddings_generated"], 3)
        self.assertEqual(result["failure_counts"], {"empty_query": 1})
