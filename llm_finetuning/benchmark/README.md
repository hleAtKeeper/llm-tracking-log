# LLM Benchmarking

Measure and compare LLM performance before and after fine-tuning.

## Quick Start

### 1. Benchmark Base Model (Before Fine-tuning)

```bash
cd benchmark
python benchmark.py <model_name>

# Example with HuggingFace model
python benchmark.py meta-llama/Llama-2-7b-hf

# Example with local model
python benchmark.py ../models/base-model
```

### 2. Fine-tune Your Model

```bash
cd ../scripts
python train.py
```

### 3. Benchmark Fine-tuned Model (After Fine-tuning)

```bash
cd ../benchmark
python benchmark.py ../checkpoints/my-finetuned-model
```

### 4. Compare Results

```bash
python compare.py \
    results/benchmark_base_20240213.json \
    results/benchmark_finetuned_20240214.json
```

## What Gets Measured

### 1. **Perplexity**
- Lower is better
- Measures how well the model predicts text
- Good indicator of general language understanding

### 2. **Response Latency**
- Time to generate responses
- Important for production deployments

### 3. **Q&A Performance**
- How well the model answers questions
- Compares responses before/after fine-tuning

### 4. **Instruction Following**
- Ability to follow instructions
- Critical for chat and assistant models

## Test Data

Located in `test_data/`:

- `qa_pairs.json` - Question-answer pairs
- `instructions.json` - Instructions to follow
- `perplexity_texts.json` - Texts for perplexity calculation (optional)

### Customize Test Data

Edit the JSON files to add your own:

```json
// qa_pairs.json
[
  {
    "question": "Your question here",
    "answer": "Expected answer (optional)"
  }
]
```

```json
// instructions.json
[
  "Your instruction here",
  "Another instruction"
]
```

## Results

Results are saved to `results/` as JSON files:

```
results/
├── benchmark_base-model_20240213_143022.json
└── benchmark_finetuned-model_20240214_091544.json
```

## Example Output

```
================================================================================
🔍 STARTING BENCHMARK
================================================================================
Model: meta-llama/Llama-2-7b-hf
Time: 2024-02-13T14:30:22
================================================================================

📋 Running Q&A Benchmark...
   1/5: 2.34s
   2/5: 2.12s
   ✅ Avg latency: 2.23s

📊 Running Perplexity Benchmark...
   ✅ Perplexity: 12.45

🎯 Running Instruction Following Benchmark...
   ✅ Avg latency: 3.11s

================================================================================
✅ BENCHMARK COMPLETE
================================================================================
```

## Comparison Output

```
================================================================================
📊 BENCHMARK COMPARISON
================================================================================

📊 PERPLEXITY
Before: 12.45
After:  8.32
Change: -33.17% ✅ Better

⏱️  QA LATENCY
Before: 2.23s
After:  2.15s
Change: -3.59% ✅ Faster

💬 SAMPLE RESPONSES (First Q&A)
Question: What is Python?
Before: Python is a programming language that...
After:  Python is a high-level, interpreted programming language...
```

## Tips

1. **Run on same hardware** - Compare results from same GPU/CPU
2. **Use consistent test data** - Don't change test data between runs
3. **Multiple runs** - Average results from 3-5 runs for reliability
4. **Save everything** - Keep all benchmark results for tracking progress
