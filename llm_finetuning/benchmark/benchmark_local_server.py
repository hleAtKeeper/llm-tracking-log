#!/usr/bin/env python3
"""
Benchmark LLM using local API server (e.g., LM Studio, Ollama).
For models running at http://127.0.0.1:1234
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class LocalServerBenchmark:
    """Benchmark LLM running on local server."""

    def __init__(
        self,
        model_name: str,
        base_url: str = "http://127.0.0.1:1234",
        output_dir: str = "results"
    ):
        """
        Initialize benchmark for local server.

        Args:
            model_name: Model identifier
            base_url: API base URL
            output_dir: Directory to save results
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Test connection
        print(f"Testing connection to {self.base_url}...")
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                print(f"✅ Connected to local LLM server")
                models = response.json()
                if 'data' in models:
                    print(f"   Available models: {len(models['data'])}")
                    for m in models['data']:
                        print(f"      - {m.get('id', 'unknown')}")
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            raise

    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate response using local server API."""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )

            latency = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return {
                    "response": content,
                    "latency": latency,
                    "success": True,
                }
            else:
                return {
                    "response": f"Error: {response.status_code}",
                    "latency": latency,
                    "success": False,
                }
        except Exception as e:
            latency = time.time() - start_time
            return {
                "response": f"Error: {str(e)}",
                "latency": latency,
                "success": False,
            }

    def benchmark_qa(self, qa_pairs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Benchmark Q&A performance."""
        print("\n📋 Running Q&A Benchmark...")

        results = []
        total_latency = 0
        success_count = 0

        for i, qa in enumerate(qa_pairs):
            question = qa["question"]
            expected = qa.get("answer", "")

            result = self.generate_response(question, max_tokens=150)
            results.append({
                "question": question,
                "expected": expected,
                "response": result["response"],
                "latency": result["latency"],
                "success": result["success"],
            })

            if result["success"]:
                success_count += 1
                total_latency += result["latency"]

            status = "✅" if result["success"] else "❌"
            print(f"   {i+1}/{len(qa_pairs)}: {result['latency']:.2f}s {status}")

        avg_latency = total_latency / success_count if success_count > 0 else 0
        print(f"   ✅ Success: {success_count}/{len(qa_pairs)}")
        print(f"   ⏱️  Avg latency: {avg_latency:.2f}s")

        return {
            "task": "qa",
            "avg_latency": avg_latency,
            "success_rate": success_count / len(qa_pairs),
            "results": results,
        }

    def benchmark_instructions(self, instructions: List[str]) -> Dict[str, Any]:
        """Benchmark instruction following."""
        print("\n🎯 Running Instruction Following Benchmark...")

        results = []
        total_latency = 0
        success_count = 0

        for i, instruction in enumerate(instructions):
            result = self.generate_response(instruction, max_tokens=200)
            results.append({
                "instruction": instruction,
                "response": result["response"],
                "latency": result["latency"],
                "success": result["success"],
            })

            if result["success"]:
                success_count += 1
                total_latency += result["latency"]

            status = "✅" if result["success"] else "❌"
            print(f"   {i+1}/{len(instructions)}: {result['latency']:.2f}s {status}")

        avg_latency = total_latency / success_count if success_count > 0 else 0
        print(f"   ✅ Success: {success_count}/{len(instructions)}")
        print(f"   ⏱️  Avg latency: {avg_latency:.2f}s")

        return {
            "task": "instruction_following",
            "avg_latency": avg_latency,
            "success_rate": success_count / len(instructions),
            "results": results,
        }

    def run_full_benchmark(
        self,
        qa_pairs: List[Dict[str, str]] = None,
        instructions: List[str] = None,
    ) -> Dict[str, Any]:
        """Run complete benchmark suite."""
        print("\n" + "=" * 80)
        print("🔍 STARTING BENCHMARK (Local Server)")
        print("=" * 80)
        print(f"Model: {self.model_name}")
        print(f"Server: {self.base_url}")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 80)

        benchmark_results = {
            "model": self.model_name,
            "server": self.base_url,
            "timestamp": datetime.now().isoformat(),
            "tasks": {},
        }

        if qa_pairs:
            benchmark_results["tasks"]["qa"] = self.benchmark_qa(qa_pairs)

        if instructions:
            benchmark_results["tasks"]["instruction_following"] = (
                self.benchmark_instructions(instructions)
            )

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_safe_name = self.model_name.replace("/", "_")
        output_file = self.output_dir / f"benchmark_{model_safe_name}_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(benchmark_results, f, indent=2)

        print("\n" + "=" * 80)
        print("✅ BENCHMARK COMPLETE")
        print("=" * 80)
        print(f"Results saved to: {output_file}")
        print("=" * 80 + "\n")

        return benchmark_results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python benchmark_local_server.py <model_name>")
        print("\nExample:")
        print("  python benchmark_local_server.py deepseek/deepseek-r1-0528-qwen3-8b")
        print("  python benchmark_local_server.py mistralai/ministral-3-3b")
        sys.exit(1)

    model_name = sys.argv[1]

    # Load test data
    from pathlib import Path
    import json

    test_dir = Path("test_data")
    test_data = {}

    qa_file = test_dir / "qa_pairs.json"
    if qa_file.exists():
        with open(qa_file) as f:
            test_data["qa_pairs"] = json.load(f)

    instructions_file = test_dir / "instructions.json"
    if instructions_file.exists():
        with open(instructions_file) as f:
            test_data["instructions"] = json.load(f)

    if not test_data:
        print("❌ No test data found. Please add test files.")
        sys.exit(1)

    # Run benchmark
    benchmark = LocalServerBenchmark(model_name)
    results = benchmark.run_full_benchmark(
        qa_pairs=test_data.get("qa_pairs"),
        instructions=test_data.get("instructions"),
    )
