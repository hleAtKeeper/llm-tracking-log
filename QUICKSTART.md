# Quick Start - Install from GitHub

## Step 1: Push to GitHub

```bash
cd /Users/hoangle/Documents/work/ai-factory/projects/LLM_tracking_the_log

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: LLM tracking monitor"

# Create GitHub repo and push
gh repo create llm-tracking-log --public --source=. --push

# Or manually:
git remote add origin https://github.com/YOUR_USERNAME/llm-tracking-log.git
git push -u origin main
```

## Step 2: Install via Pip

```bash
pip install git+https://github.com/YOUR_USERNAME/llm-tracking-log.git
```

## Step 3: Use it!

```bash
# Start monitoring
llm-monitor

# View logs
tail -f ~/.llm-tracking-log/logs/files.log
tail -f ~/.llm-tracking-log/logs/apps.log
```

## Update After Changes

```bash
# Reinstall latest version
pip install --upgrade --force-reinstall git+https://github.com/YOUR_USERNAME/llm-tracking-log.git
```

That's it! Simple pip installation from GitHub.
