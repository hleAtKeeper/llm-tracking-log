# LLM Tracking the Log

Ultra-simple MacBook activity monitoring using **Watchdog** (files) and **AppKit** (apps).

## What It Does

**Watchdog monitors files:**
- Documents, Desktop, Downloads folders
- Programming files (.py, .js, .ts, .java, etc.)
- Captures full file content in real-time

**AppKit monitors apps:**
- Detects active application switches
- Logs app name, bundle ID, and path

## Quick Start

```bash
# Install dependencies
pip install watchdog pyobjc-framework-Cocoa

# Start monitoring
./start.sh
```

That's it! Events are logged in real-time to `logs/` folder.

## File Structure

```
LLM_tracking_the_log/
├── monitor.py        ← Main monitoring script
├── start.sh         ← Start script
├── watchdog_demo.py ← Educational demo
├── logs/
│   ├── files.log    ← File events with content
│   └── apps.log     ← App switch events
└── test/            ← Test files
```

## Output Examples

**File Created:**
```json
{
  "event": "file_event",
  "data": {
    "type": "created",
    "path": "/Users/.../script.py",
    "content": "print('hello')\n",
    "timestamp": "2026-02-11T..."
  }
}
```

**App Switch:**
```json
{
  "event": "app_event",
  "data": {
    "type": "switch",
    "name": "Chrome",
    "bundle_id": "com.google.Chrome",
    "timestamp": "2026-02-11T..."
  }
}
```

## Learn Watchdog

Run the educational demo with detailed explanations:
```bash
python3 watchdog_demo.py test/
```

## Configuration

Edit `monitor.py` to customize:
- **Watch paths**: Line ~245 - `watch_paths` list
- **File extensions**: Line ~20 - `PROGRAMMING_EXTENSIONS`
- **Skip directories**: Line ~28 - `SKIP_DIRS`
- **App check interval**: Line ~197 - `check_interval`

## Privacy

- All data stays local
- No network transmission
- Logs in `logs/` directory only
