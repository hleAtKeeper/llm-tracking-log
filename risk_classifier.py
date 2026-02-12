#!/usr/bin/env python3
"""Risk classifier using keeper-security/risk-classifier-v2 model."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import Dict, Any


class RiskClassifier:
    """Classify code risk level using HuggingFace model."""

    def __init__(self, model_name: str = "keeper-security/risk-classifier-v2"):
        print(f'[RISK CLASSIFIER] Loading model: {model_name}')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

        # Risk level mappings
        self.id2label = self.model.config.id2label
        print(f'[RISK CLASSIFIER] Initialized with labels: {self.id2label}')

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify risk level of given text (code).

        Args:
            text: Code or text to classify

        Returns:
            Dict with risk_level, confidence, and all scores
        """
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)

        # Get predicted class and confidence
        predicted_class = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][predicted_class].item()

        # Get all risk scores
        risk_scores = {
            self.id2label[i]: probabilities[0][i].item()
            for i in range(len(self.id2label))
        }

        return {
            'risk_level': self.id2label[predicted_class],
            'confidence': confidence,
            'scores': risk_scores
        }

    def classify_code_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify risk for a file event.

        Args:
            event: Event dict with code content

        Returns:
            Risk classification result
        """
        if event.get('event') != 'file_event':
            return None

        content = event.get('data', {}).get('content', '')
        if not content:
            return None

        result = self.classify(content)

        # Add file info
        result['file_path'] = event.get('data', {}).get('path', '')
        result['event_type'] = event.get('data', {}).get('type', '')

        return result


if __name__ == '__main__':
    # Test the classifier
    classifier = RiskClassifier()

    # Test with sample code
    test_code = """
import os
import subprocess

def execute_command(user_input):
    # Potentially dangerous - executes user input directly
    subprocess.call(user_input, shell=True)

def read_file(filename):
    # Reading arbitrary files
    with open(filename, 'r') as f:
        return f.read()
"""

    print('\n' + '='*80)
    print('Testing Risk Classifier')
    print('='*80)
    print(f'\nCode:\n{test_code[:200]}...\n')

    result = classifier.classify(test_code)

    print(f"🚨 RISK LEVEL: {result['risk_level']}")
    print(f"📊 Confidence: {result['confidence']:.2%}")
    print(f"\n📈 All Risk Scores:")
    for level, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {level}: {score:.2%}")
