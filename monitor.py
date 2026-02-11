#!/usr/bin/env python3
"""
Unified monitoring system using Watchdog (files) and AppKit (apps).
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List

# Watchdog for file monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print('ERROR: watchdog not installed')
    print('Install: pip install watchdog')
    sys.exit(1)

# AppKit for application monitoring
try:
    from AppKit import NSWorkspace
except ImportError:
    print('ERROR: AppKit not installed')
    print('Install: pip install pyobjc-framework-Cocoa')
    sys.exit(1)

# No external dependencies - just Watchdog and AppKit!


# Programming file extensions
PROGRAMMING_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
    '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
    '.sh', '.bash', '.zsh', '.sql', '.r', '.m', '.html', '.css',
    '.vue', '.svelte', '.yaml', '.yml', '.json', '.xml', '.md'
}

SKIP_DIRS = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'logs', 'pids'}
MAX_FILE_SIZE = 1024 * 1024  # 1MB


class FileMonitor(FileSystemEventHandler):
    """Monitor file system changes using Watchdog."""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_handle = open(log_file, 'a')
        print('[FILE MONITOR] Initialized')

    def is_programming_file(self, path: str) -> bool:
        """Check if file is a programming file."""
        return Path(path).suffix.lower() in PROGRAMMING_EXTENSIONS

    def should_skip(self, path: str) -> bool:
        """Check if file should be skipped."""
        path_parts = Path(path).parts
        return any(skip_dir in path_parts for skip_dir in SKIP_DIRS)

    def log_event(self, event_type: str, path: str, content: str = None):
        """Log a file event."""
        log_entry = {
            'event': 'file_event',
            'data': {
                'type': event_type,
                'path': path,
                'timestamp': datetime.now().isoformat(),
            },
        }

        if content:
            log_entry['data']['content'] = content

        self.log_handle.write(json.dumps(log_entry) + '\n')
        self.log_handle.flush()

        print(f'[FILE] {event_type}: {Path(path).name}')

    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory or self.should_skip(event.src_path):
            return

        if self.is_programming_file(event.src_path):
            print(f'\n✨ [FILE CREATED] {event.src_path}')

            try:
                # Read content
                file_path = Path(event.src_path)
                if file_path.stat().st_size <= MAX_FILE_SIZE:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    self.log_event('created', event.src_path, content=content)
                    print(f'   Size: {len(content)} bytes')

            except Exception as e:
                print(f'   Error: {e}')

    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory or self.should_skip(event.src_path):
            return

        if self.is_programming_file(event.src_path):
            print(f'\n📝 [FILE MODIFIED] {event.src_path}')

            try:
                file_path = Path(event.src_path)
                if file_path.stat().st_size <= MAX_FILE_SIZE:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    self.log_event('modified', event.src_path, content=content)
                    print(f'   Size: {len(content)} bytes')

            except Exception as e:
                print(f'   Error: {e}')

    def on_deleted(self, event):
        """Handle file deletion."""
        if not event.is_directory and not self.should_skip(event.src_path):
            print(f'\n🗑️  [FILE DELETED] {event.src_path}')
            self.log_event('deleted', event.src_path)

    def close(self):
        """Close log file."""
        self.log_handle.close()


class AppMonitor:
    """Monitor application switches using AppKit."""

    def __init__(self, log_file: Path, check_interval: float = 2.0):
        self.log_file = log_file
        self.log_handle = open(log_file, 'a')
        self.check_interval = check_interval
        self.last_app = None
        print('[APP MONITOR] Initialized')

    def get_active_app(self):
        """Get currently active application."""
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.activeApplication()
        return {
            'name': active_app['NSApplicationName'],
            'bundle_id': active_app['NSApplicationBundleIdentifier'],
            'path': active_app['NSApplicationPath'],
            'timestamp': datetime.now().isoformat(),
        }

    def log_event(self, event_type: str, app_data: dict):
        """Log an app event."""
        log_entry = {
            'event': 'app_event',
            'data': {
                'type': event_type,
                **app_data,
            },
        }

        self.log_handle.write(json.dumps(log_entry) + '\n')
        self.log_handle.flush()

        print(f'[APP] {event_type}: {app_data["name"]}')

    def monitor(self):
        """Monitor app switches."""
        while True:
            try:
                current_app = self.get_active_app()

                if self.last_app is None:
                    print(f'\n🖥️  [APP CURRENT] {current_app["name"]}')
                    self.log_event('current', current_app)
                elif current_app['bundle_id'] != self.last_app['bundle_id']:
                    print(f'\n🔄 [APP SWITCH] {self.last_app["name"]} → {current_app["name"]}')
                    self.log_event('switch', current_app)

                self.last_app = current_app
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f'[APP ERROR] {e}')
                time.sleep(self.check_interval)

    def close(self):
        """Close log file."""
        self.log_handle.close()


def main():
    """Start monitoring system."""
    import sys

    # Parse arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print('LLM Tracking the Log - Monitor MacBook activity')
        print()
        print('Usage:')
        print('  llm-monitor              Start monitoring')
        print('  llm-monitor --help       Show this help')
        print()
        print('Monitors:')
        print('  - Documents, Desktop, Downloads folders')
        print('  - Programming files (.py, .js, .ts, etc.)')
        print('  - Application switches')
        print()
        print('Logs stored in: ~/.llm-tracking-log/logs/')
        return

    print('=' * 80)
    print('UNIFIED MONITORING SYSTEM')
    print('Watchdog (Files) + AppKit (Apps)')
    print('=' * 80)

    # Setup paths - use home directory for installed package
    log_dir = Path.home() / '.llm-tracking-log' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    file_log = log_dir / 'files.log'
    app_log = log_dir / 'apps.log'

    # Watch paths
    watch_paths = [
        str(Path.home() / 'Documents'),
        str(Path.home() / 'Desktop'),
        str(Path.home() / 'Downloads'),
    ]

    print(f'\n[SETUP] Log directory: {log_dir}')
    print(f'[SETUP] File log: {file_log.name}')
    print(f'[SETUP] App log: {app_log.name}')

    # Setup file monitoring (Watchdog)
    print(f'\n[FILE MONITOR] Setting up Watchdog...')
    file_monitor = FileMonitor(file_log)
    observer = Observer()

    for watch_path in watch_paths:
        if Path(watch_path).exists():
            observer.schedule(file_monitor, watch_path, recursive=True)
            print(f'[FILE MONITOR] Watching: {watch_path}')

    observer.start()
    print('[FILE MONITOR] ✓ Started')

    # Setup app monitoring (AppKit)
    print(f'\n[APP MONITOR] Setting up AppKit...')
    app_monitor = AppMonitor(app_log, check_interval=2.0)
    print('[APP MONITOR] ✓ Started')

    print('\n' + '=' * 80)
    print('🔍 MONITORING ACTIVE')
    print('=' * 80)
    print('\nPress Ctrl+C to stop...\n')

    try:
        # Run app monitor (blocking)
        app_monitor.monitor()

    except KeyboardInterrupt:
        print('\n\n[SHUTDOWN] Stopping monitors...')

    finally:
        observer.stop()
        observer.join()
        file_monitor.close()
        app_monitor.close()
        print('[SHUTDOWN] ✓ Shutdown complete\n')


if __name__ == '__main__':
    main()
