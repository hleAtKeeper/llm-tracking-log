#!/usr/bin/env python3
"""
Compare benchmark results before and after fine-tuning.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


def load_benchmark(filepath: str) -> Dict[str, Any]:
    """Load benchmark results from JSON file."""
    with open(filepath) as f:
        return json.load(f)


def compare_benchmarks(before: Dict, after: Dict) -> None:
    """Compare two benchmark results and print improvements."""
    print("\n" + "=" * 80)
    print("📊 BENCHMARK COMPARISON")
    print("=" * 80)
    print(f"\nBefore: {before['model']}")
    print(f"After:  {after['model']}")
    print(f"\nBefore Time: {before['timestamp']}")
    print(f"After Time:  {after['timestamp']}")
    print("\n" + "=" * 80)

    # Compare perplexity
    if "perplexity" in before["tasks"] and "perplexity" in after["tasks"]:
        before_ppl = before["tasks"]["perplexity"]["perplexity"]
        after_ppl = after["tasks"]["perplexity"]["perplexity"]
        improvement = ((before_ppl - after_ppl) / before_ppl) * 100

        print("\n📊 PERPLEXITY")
        print("-" * 80)
        print(f"Before: {before_ppl:.2f}")
        print(f"After:  {after_ppl:.2f}")
        print(f"Change: {improvement:+.2f}% {'✅ Better' if improvement > 0 else '❌ Worse'}")

    # Compare latency
    tasks_with_latency = ["qa", "instruction_following"]
    for task in tasks_with_latency:
        if task in before["tasks"] and task in after["tasks"]:
            before_lat = before["tasks"][task]["avg_latency"]
            after_lat = after["tasks"][task]["avg_latency"]
            improvement = ((before_lat - after_lat) / before_lat) * 100

            task_name = task.replace("_", " ").title()
            print(f"\n⏱️  {task_name.upper()} LATENCY")
            print("-" * 80)
            print(f"Before: {before_lat:.2f}s")
            print(f"After:  {after_lat:.2f}s")
            print(f"Change: {improvement:+.2f}% {'✅ Faster' if improvement > 0 else '⚠️  Slower'}")

    # Show sample responses
    if "qa" in before["tasks"] and "qa" in after["tasks"]:
        print("\n💬 SAMPLE RESPONSES (First Q&A)")
        print("-" * 80)

        before_qa = before["tasks"]["qa"]["results"][0]
        after_qa = after["tasks"]["qa"]["results"][0]

        print(f"\nQuestion: {before_qa['question']}")
        print(f"\nBefore: {before_qa['response'][:200]}...")
        print(f"\nAfter:  {after_qa['response'][:200]}...")

    print("\n" + "=" * 80)
    print("✅ COMPARISON COMPLETE")
    print("=" * 80 + "\n")


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare.py <before_results.json> <after_results.json>")
        print("\nExample:")
        print("  python compare.py results/benchmark_base_20240213.json results/benchmark_finetuned_20240214.json")
        sys.exit(1)

    before_file = sys.argv[1]
    after_file = sys.argv[2]

    if not Path(before_file).exists():
        print(f"❌ Before file not found: {before_file}")
        sys.exit(1)

    if not Path(after_file).exists():
        print(f"❌ After file not found: {after_file}")
        sys.exit(1)

    before = load_benchmark(before_file)
    after = load_benchmark(after_file)

    compare_benchmarks(before, after)


if __name__ == "__main__":
    main()
