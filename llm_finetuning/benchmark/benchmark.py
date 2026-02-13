#!/usr/bin/env python3
"""
LLM Benchmarking Script

Evaluates model performance on various tasks to measure fine-tuning improvements.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LLMBenchmark:
    """Benchmark LLM performance on various tasks."""

    def __init__(self, model_name_or_path: str, output_dir: str = "results"):
        """
        Initialize benchmark.

        Args:
            model_name_or_path: HuggingFace model name or local path
            output_dir: Directory to save results
        """
        print(f"Loading model: {model_name_or_path}")
        self.model_name = model_name_or_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        self.model.eval()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"✅ Model loaded: {model_name_or_path}")
        print(f"   Parameters: {self.count_parameters():,}")
        print(f"   Device: {next(self.model.parameters()).device}")

    def count_parameters(self) -> int:
        """Count total model parameters."""
        return sum(p.numel() for p in self.model.parameters())

    def generate_response(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Generate response for a prompt."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from response
        response = response[len(prompt):].strip()
        return response

    def calculate_perplexity(self, texts: List[str]) -> float:
        """Calculate average perplexity on a list of texts."""
        total_loss = 0
        total_tokens = 0

        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
                total_loss += loss.item() * inputs["input_ids"].size(1)
                total_tokens += inputs["input_ids"].size(1)

        avg_loss = total_loss / total_tokens
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        return perplexity

    def benchmark_qa(self, qa_pairs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Benchmark on question-answering tasks."""
        print("\n📋 Running Q&A Benchmark...")

        results = []
        for i, qa in enumerate(qa_pairs):
            question = qa["question"]
            expected = qa.get("answer", "")

            start_time = time.time()
            response = self.generate_response(question, max_new_tokens=150)
            latency = time.time() - start_time

            results.append({
                "question": question,
                "expected": expected,
                "response": response,
                "latency": latency,
            })

            print(f"   {i+1}/{len(qa_pairs)}: {latency:.2f}s")

        avg_latency = sum(r["latency"] for r in results) / len(results)
        print(f"   ✅ Avg latency: {avg_latency:.2f}s")

        return {
            "task": "qa",
            "avg_latency": avg_latency,
            "results": results,
        }

    def benchmark_perplexity(self, texts: List[str]) -> Dict[str, Any]:
        """Benchmark perplexity on test texts."""
        print("\n📊 Running Perplexity Benchmark...")

        perplexity = self.calculate_perplexity(texts)
        print(f"   ✅ Perplexity: {perplexity:.2f}")

        return {
            "task": "perplexity",
            "perplexity": perplexity,
            "num_samples": len(texts),
        }

    def benchmark_instruction_following(
        self, instructions: List[str]
    ) -> Dict[str, Any]:
        """Benchmark instruction following ability."""
        print("\n🎯 Running Instruction Following Benchmark...")

        results = []
        for i, instruction in enumerate(instructions):
            start_time = time.time()
            response = self.generate_response(instruction, max_new_tokens=200)
            latency = time.time() - start_time

            results.append({
                "instruction": instruction,
                "response": response,
                "latency": latency,
            })

            print(f"   {i+1}/{len(instructions)}: {latency:.2f}s")

        avg_latency = sum(r["latency"] for r in results) / len(results)
        print(f"   ✅ Avg latency: {avg_latency:.2f}s")

        return {
            "task": "instruction_following",
            "avg_latency": avg_latency,
            "results": results,
        }

    def run_full_benchmark(
        self,
        qa_pairs: List[Dict[str, str]] = None,
        perplexity_texts: List[str] = None,
        instructions: List[str] = None,
    ) -> Dict[str, Any]:
        """Run complete benchmark suite."""
        print("\n" + "=" * 80)
        print("🔍 STARTING BENCHMARK")
        print("=" * 80)
        print(f"Model: {self.model_name}")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 80)

        benchmark_results = {
            "model": self.model_name,
            "timestamp": datetime.now().isoformat(),
            "parameters": self.count_parameters(),
            "tasks": {},
        }

        # Run each benchmark if data provided
        if qa_pairs:
            benchmark_results["tasks"]["qa"] = self.benchmark_qa(qa_pairs)

        if perplexity_texts:
            benchmark_results["tasks"]["perplexity"] = self.benchmark_perplexity(
                perplexity_texts
            )

        if instructions:
            benchmark_results["tasks"]["instruction_following"] = (
                self.benchmark_instruction_following(instructions)
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


def load_test_data(test_data_dir: str = "test_data") -> Dict[str, Any]:
    """Load test data from files."""
    test_dir = Path(test_data_dir)
    data = {}

    # Load Q&A pairs
    qa_file = test_dir / "qa_pairs.json"
    if qa_file.exists():
        with open(qa_file) as f:
            data["qa_pairs"] = json.load(f)

    # Load perplexity texts
    perplexity_file = test_dir / "perplexity_texts.json"
    if perplexity_file.exists():
        with open(perplexity_file) as f:
            data["perplexity_texts"] = json.load(f)

    # Load instructions
    instructions_file = test_dir / "instructions.json"
    if instructions_file.exists():
        with open(instructions_file) as f:
            data["instructions"] = json.load(f)

    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <model_name_or_path>")
        print("\nExample:")
        print("  python benchmark.py meta-llama/Llama-2-7b-hf")
        print("  python benchmark.py ./models/my-finetuned-model")
        sys.exit(1)

    model_name = sys.argv[1]

    # Load test data
    test_data = load_test_data()

    if not test_data:
        print("⚠️  No test data found. Creating sample data...")
        # Create sample test data
        test_data = {
            "qa_pairs": [
                {
                    "question": "What is the capital of France?",
                    "answer": "Paris",
                },
                {
                    "question": "Explain what machine learning is in one sentence.",
                    "answer": "Machine learning is...",
                },
            ],
            "perplexity_texts": [
                "The quick brown fox jumps over the lazy dog.",
                "Machine learning is a subset of artificial intelligence.",
            ],
            "instructions": [
                "Write a haiku about technology.",
                "Explain recursion to a 5-year-old.",
            ],
        }

    # Run benchmark
    benchmark = LLMBenchmark(model_name, output_dir="results")
    results = benchmark.run_full_benchmark(
        qa_pairs=test_data.get("qa_pairs"),
        perplexity_texts=test_data.get("perplexity_texts"),
        instructions=test_data.get("instructions"),
    )
