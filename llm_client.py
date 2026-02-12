#!/usr/bin/env python3
"""LLM client to analyze monitoring events."""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import risk classifier
try:
    from risk_classifier import RiskClassifier
except ImportError:
    print('[WARNING] Risk classifier not available')
    RiskClassifier = None


class LLMClient:
    """Client for local LLM analysis."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:1234",
        model: str = "deepseek/deepseek-r1-0528-qwen3-8b",
        log_file: Path = None,
        use_risk_classifier: bool = True,
    ):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.log_file = log_file
        self.log_handle = None

        if log_file:
            self.log_handle = open(log_file, 'a')

        # Initialize risk classifier
        self.risk_classifier = None
        if use_risk_classifier and RiskClassifier:
            try:
                self.risk_classifier = RiskClassifier()
            except Exception as e:
                print(f'[WARNING] Could not initialize risk classifier: {e}')

        print(f'[LLM CLIENT] Initialized')
        print(f'[LLM CLIENT] URL: {self.base_url}')
        print(f'[LLM CLIENT] Model: {self.model}')
        if self.risk_classifier:
            print(f'[LLM CLIENT] Risk classifier: enabled')

    def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a monitoring event to the LLM for analysis.

        Args:
            event: Event data (file or app event)

        Returns:
            LLM response with analysis
        """
        # Create prompt messages for the LLM
        messages = self._create_prompt(event)

        try:
            # Call local LLM API (OpenAI-compatible)
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,  # Lower temperature for consistent analysis
                    "max_tokens": 300,   # Concise output
                },
                timeout=120,  # Longer timeout for reasoning models like deepseek-r1
            )

            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"]

                # Run risk classification for code events
                risk_result = None
                if self.risk_classifier and event.get('event') == 'file_event':
                    content = event.get('data', {}).get('content', '')
                    if content:
                        try:
                            risk_result = self.risk_classifier.classify(content)
                        except Exception as e:
                            print(f'⚠️  Risk classification error: {e}')

                # Log the analysis
                analysis_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "event": event,
                    "analysis": analysis,
                }

                if risk_result:
                    analysis_entry["risk_classification"] = risk_result

                if self.log_handle:
                    self.log_handle.write(json.dumps(analysis_entry) + '\n')
                    self.log_handle.flush()

                # Print LLM analysis first
                print(f'\n🤖 [LLM ANALYSIS]')
                print(f'{analysis}\n')

                # Then print risk level if available
                if risk_result:
                    risk_emoji = {
                        'Critical': '🔴',
                        'High': '🟠',
                        'Medium': '🟡',
                        'Low': '🟢'
                    }
                    emoji = risk_emoji.get(risk_result['risk_level'], '⚪')
                    print(f'{emoji} [RISK LEVEL: {risk_result["risk_level"]}] (Confidence: {risk_result["confidence"]:.1%})\n')

                return analysis_entry

            else:
                print(f'⚠️  LLM API error: {response.status_code}')
                return None

        except requests.exceptions.ConnectionError:
            print(f'⚠️  Cannot connect to LLM at {self.base_url}')
            return None
        except requests.exceptions.Timeout:
            print(f'⚠️  LLM request timed out')
            return None
        except Exception as e:
            print(f'⚠️  LLM error: {e}')
            return None

    def _create_prompt(self, event: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create a prompt messages list for the LLM based on the event type."""
        event_type = event.get('event')

        # System message - expert persona and principles
        system_message = {
            "role": "system",
            "content": """You are an expert code analyst specializing in understanding code logic, patterns, and developer intent.

**YOUR ROLE:**
- Analyze code to understand the reasoning and logic behind implementation choices
- Identify programming patterns, techniques, and architectural decisions
- Explain WHY code was written the way it was, not just what it does
- Provide clear insights into developer intent and thought process

**ANALYSIS PRINCIPLES:**
- Logic First: Focus on the reasoning and logical flow of the code
- Pattern Recognition: Identify common patterns, anti-patterns, and design choices
- Intent Discovery: Understand what problem the code is solving and why this approach was chosen
- Clarity: Provide clear, specific observations about code structure and logic
- Conciseness: Keep analysis brief (3-4 sentences max)

**OUTPUT REQUIREMENTS:**
- Explain the purpose and intent of the code
- Identify key programming patterns or techniques used
- Describe the logical flow and reasoning
- Note why the developer might have structured it this way"""
        }

        # User message - specific event analysis
        if event_type == 'file_event':
            data = event['data']
            file_type = data.get('type')
            path = Path(data.get('path', ''))
            content = data.get('content', '')

            if file_type == 'created':
                user_content = f"""**NEW CODE FILE CREATED:**

File: {path.name}
Path: {path}
Type: {path.suffix}

Code content (first 500 chars):
```
{content[:500]}
```

**CODE REASONING ANALYSIS:**
Analyze this code and explain:
1. What is the purpose and intent of this code?
2. What programming patterns, techniques, or structures are being used?
3. What is the logical flow and why might the developer have structured it this way?
4. What problem is this code designed to solve?"""

            elif file_type == 'modified':
                user_content = f"""**CODE FILE MODIFIED:**

File: {path.name}
Path: {path}
Type: {path.suffix}

Updated code content (first 500 chars):
```
{content[:500]}
```

**CODE REASONING ANALYSIS:**
Analyze this modified code and explain:
1. What is the logical structure and reasoning behind this code?
2. What programming patterns or techniques are implemented?
3. What is the code trying to accomplish and why was it written this way?
4. What design decisions or trade-offs are evident in the implementation?"""

            elif file_type == 'deleted':
                user_content = f"""**FILE DELETED EVENT:**

File: {path.name}
Path: {path}

**ANALYSIS TASK:**
Based on this file deletion, identify:
1. Why might the user have deleted this file?
2. What cleanup or refactoring activity does this suggest?"""

            else:
                user_content = f"File event: {file_type} on {path}"

        elif event_type == 'app_event':
            data = event['data']
            app_name = data.get('name', 'Unknown')
            event_subtype = data.get('type')

            if event_subtype == 'switch':
                user_content = f"""**APPLICATION SWITCH EVENT:**

Application: {app_name}
Bundle ID: {data.get('bundle_id', 'N/A')}

**ANALYSIS TASK:**
Based on this app switch, identify:
1. What activity is the user likely performing?
2. What does this suggest about their current workflow?
3. What task or context switch does this indicate?"""

            else:
                user_content = f"""**CURRENT APPLICATION:**

Application: {app_name}

**ANALYSIS TASK:**
What activity does this application suggest the user is performing?"""

        else:
            user_content = f"Activity event:\n{json.dumps(event, indent=2)}"

        user_message = {"role": "user", "content": user_content}

        return [system_message, user_message]

    def close(self):
        """Close log file."""
        if self.log_handle:
            self.log_handle.close()


if __name__ == '__main__':
    # Test the LLM client
    client = LLMClient()

    # Test with a file event
    test_event = {
        'event': 'file_event',
        'data': {
            'type': 'created',
            'path': '/Users/test/script.py',
            'content': 'print("Hello World")\n',
            'timestamp': datetime.now().isoformat(),
        },
    }

    print('Testing LLM client...')
    result = client.analyze_event(test_event)

    if result:
        print('\n✓ LLM client working!')
    else:
        print('\n⚠️  LLM client test failed')

    client.close()
