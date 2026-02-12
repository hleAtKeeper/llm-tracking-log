# LLM Tracking the Log

Monitor code changes with AI analysis and security risk classification.

## Features

- 📁 **File Monitoring**: Watches for code file changes (`.py`, `.js`, `.ts`, etc.)
- 🤖 **LLM Analysis**: Analyzes code reasoning with local LLM
- 🔴 **Risk Classification**: Classifies security risk levels (Critical/High/Medium/Low)
- 🖥️ **App Monitoring**: Tracks application switches

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Monitor default folders (Documents, Desktop, Downloads)
llm-monitor

# Monitor specific folder
llm-monitor ~/Projects

# Monitor multiple folders
llm-monitor ~/Projects ~/Work ~/Code
```

## Requirements

- macOS 10.13+
- Python 3.8+
- Local LLM server at `http://127.0.0.1:1234`

## Logs

All logs are stored in `~/.llm-tracking-log/logs/`:
- `files.log` - File change events
- `apps.log` - Application switches
- `llm_analysis.log` - LLM analysis with risk classifications

## View Risk Analysis

```bash
# Show risk classifications with colors
python3 << 'EOF'
import json
with open('/Users/hoangle/.llm-tracking-log/logs/llm_analysis.log') as f:
    for line in f:
        data = json.loads(line)
        if 'risk_classification' in data:
            risk = data['risk_classification']
            print(f"{risk['risk_level']:8s} {risk['confidence']:.1%} - {data['event']['data']['path'].split('/')[-1]}")
EOF
```

## Stop Monitor

```bash
pkill -f llm-monitor
```
