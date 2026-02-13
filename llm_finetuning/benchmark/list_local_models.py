#!/usr/bin/env python3
"""List locally available models."""

from pathlib import Path
import os

def list_local_models():
    """List models available locally."""
    print("\n" + "="*80)
    print("📦 LOCALLY AVAILABLE MODELS")
    print("="*80 + "\n")

    # Check HuggingFace cache
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub"

    if hf_cache.exists():
        print("🤗 HuggingFace Cached Models:")
        print("-" * 80)

        models = []
        for item in hf_cache.iterdir():
            if item.is_dir() and item.name.startswith("models--"):
                # Convert models--org--name to org/name
                model_name = item.name.replace("models--", "").replace("--", "/")

                # Check if model files exist
                snapshots = item / "snapshots"
                if snapshots.exists() and any(snapshots.iterdir()):
                    models.append(model_name)

        # Sort and display
        models.sort()
        for i, model in enumerate(models, 1):
            print(f"   {i:2d}. {model}")

        print(f"\n   Total: {len(models)} models")
    else:
        print("   No HuggingFace cache found")

    # Check for local LLM server
    print("\n🌐 Local LLM Server:")
    print("-" * 80)
    try:
        import requests
        response = requests.get("http://127.0.0.1:1234/v1/models", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print("   ✅ Server running at http://127.0.0.1:1234")
                print(f"   Available models: {len(data['data'])}")
                for model in data['data']:
                    print(f"      - {model.get('id', 'unknown')}")
        else:
            print("   ⚠️  Server responded with error")
    except:
        print("   ❌ No server running at http://127.0.0.1:1234")

    print("\n" + "="*80)
    print("\n💡 Usage:")
    print("   python benchmark.py <model_name>")
    print("\nExamples:")
    print("   python benchmark.py gpt2")
    print("   python benchmark.py distilbert-base-uncased")
    print("   python benchmark.py keeper-security/risk-classifier-v2")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    list_local_models()
