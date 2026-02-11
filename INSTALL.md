# Installation Guide

## Install from GitHub (Recommended)

```bash
pip install git+https://github.com/YOUR_USERNAME/llm-tracking-log.git
```

## Local Development Install

```bash
cd /Users/hoangle/Documents/work/ai-factory/projects/LLM_tracking_the_log
pip install -e .
```

## Usage After Installation

```bash
# Start monitoring
llm-monitor

# Run demo
llm-watchdog-demo ~/Documents

# View logs
tail -f ~/.llm-tracking-log/logs/files.log
tail -f ~/.llm-tracking-log/logs/apps.log
```

## Uninstall

```bash
pip uninstall llm-tracking-log
```

## Requirements

- macOS 10.13 or later
- Python 3.8 or later
- Accessibility permissions (for app monitoring)
