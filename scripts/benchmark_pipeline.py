"""
Pipeline Latency and Throughput Benchmarking Utility.
Measures execution time, memory overhead, and throughput across batch order processing.
"""

import os
import sys
import time
import statistics
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

from agents.orchestrator import run_sequential_pipeline


def run_benchmark(iterations: int = 10):
    order_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_supermarket_monthly_restock.txt")
    with open(order_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"[*] Starting FMCG RFP Pipeline Benchmark ({iterations} iterations)...")
    latencies = []

    for i in range(iterations):
        t0 = time.perf_counter()
        result = run_sequential_pipeline(text, use_mock=True)
        duration = time.perf_counter() - t0
        latencies.append(duration)
        assert result["status"] == "COMPLETED", f"Iteration {i} failed: {result.get('errors')}"

    latencies_sorted = sorted(latencies)
    avg_lat = statistics.mean(latencies)
    median_lat = statistics.median(latencies)
    p95_lat = latencies_sorted[int(len(latencies_sorted) * 0.95)]
    min_lat = min(latencies)
    max_lat = max(latencies)
    throughput = iterations / sum(latencies)

    report = {
        "iterations": iterations,
        "throughput_rfps_per_sec": round(throughput, 2),
        "latency_min_sec": round(min_lat, 4),
        "latency_avg_sec": round(avg_lat, 4),
        "latency_median_sec": round(median_lat, 4),
        "latency_p95_sec": round(p95_lat, 4),
        "latency_max_sec": round(max_lat, 4)
    }

    print("\n================ BENCHMARK RESULTS ================")
    for k, v in report.items():
        print(f"  {k:30}: {v}")
    print("===================================================\n")
    return report


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run_benchmark(count)
