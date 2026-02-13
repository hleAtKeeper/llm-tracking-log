#!/usr/bin/env python3
"""
Unified monitoring system using Watchdog (files) and AppKit (apps).
"""

import sys
import os
import json
import time
import platform
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

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

# Import LLM client for analysis
try:
    from llm_client import LLMClient
except ImportError:
    print('Warning: LLM client not available')
    LLMClient = None


# Programming file extensions
PROGRAMMING_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
    '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
    '.sh', '.bash', '.zsh', '.sql', '.r', '.m', '.html', '.css',
    '.vue', '.svelte', '.yaml', '.yml', '.json', '.xml', '.md'
}

SKIP_DIRS = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'logs', 'pids'}
MIN_FILE_SIZE = 10  # Skip files smaller than 10 bytes
MAX_FILE_SIZE = 1024 * 1024  # 1MB


class FileMonitor(FileSystemEventHandler):
    """Monitor file system changes using Watchdog."""

    def __init__(self, log_file: Path, llm_client=None):
        self.log_file = log_file
        self.log_handle = open(log_file, 'a')
        self.llm_client = llm_client
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

        # Send to LLM for analysis
        if self.llm_client:
            self.llm_client.analyze_event(log_entry)

    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory or self.should_skip(event.src_path):
            return

        if self.is_programming_file(event.src_path):
            print(f'\n✨ [FILE CREATED] {event.src_path}')

            try:
                # Read content
                file_path = Path(event.src_path)
                file_size = file_path.stat().st_size

                # Skip very small or very large files
                if file_size < MIN_FILE_SIZE:
                    print(f'   Skipped: file too small ({file_size} bytes)')
                    return

                if file_size <= MAX_FILE_SIZE:
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
                file_size = file_path.stat().st_size

                # Skip very small or very large files
                if file_size < MIN_FILE_SIZE:
                    print(f'   Skipped: file too small ({file_size} bytes)')
                    return

                if file_size <= MAX_FILE_SIZE:
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

    def __init__(self, log_file: Path, check_interval: float = 2.0, llm_client=None):
        self.log_file = log_file
        self.log_handle = open(log_file, 'a')
        self.check_interval = check_interval
        self.last_app = None
        self.llm_client = llm_client
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

        # Send to LLM for analysis
        if self.llm_client:
            self.llm_client.analyze_event(log_entry)

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


def validate_requirements(watch_paths: List[str] = None) -> Dict[str, bool]:
    """
    Validate all requirements before starting monitor.

    Returns:
        Dict with validation results for each component
    """
    print('\n' + '='*80)
    print('🔍 VALIDATING REQUIREMENTS')
    print('='*80 + '\n')

    results = {}

    # 1. Check Platform (macOS required for AppKit)
    print('📱 Platform Check...')
    is_macos = platform.system() == 'Darwin'
    if is_macos:
        print('   ✅ macOS detected')
        results['platform'] = True
    else:
        print('   ⚠️  Warning: Not running on macOS - app monitoring may not work')
        results['platform'] = False
    print()

    # 2. Check Python Packages
    print('📦 Python Packages...')
    packages = {
        'watchdog': 'File monitoring',
        'AppKit': 'Application monitoring (macOS)',
        'requests': 'HTTP requests',
        'transformers': 'HuggingFace models',
        'torch': 'PyTorch for models'
    }

    all_packages_ok = True
    for package, description in packages.items():
        try:
            __import__(package)
            print(f'   ✅ {package:15s} - {description}')
            results[f'package_{package}'] = True
        except ImportError:
            print(f'   ❌ {package:15s} - Missing! ({description})')
            all_packages_ok = False
            results[f'package_{package}'] = False

    if all_packages_ok:
        print('   All required packages installed')
    else:
        print('   ⚠️  Some packages missing - install with: pip install -e .')
    print()

    # 3. Check LLM Server
    print('🤖 LLM Server Check...')
    llm_url = 'http://127.0.0.1:1234'
    try:
        response = requests.get(f'{llm_url}/v1/models', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f'   ✅ LLM server running at {llm_url}')
            if 'data' in models and len(models['data']) > 0:
                print(f'   📋 Available models: {len(models["data"])}')
                for model in models['data'][:3]:  # Show first 3
                    print(f'      - {model.get("id", "unknown")}')
            results['llm_server'] = True
        else:
            print(f'   ❌ LLM server returned status {response.status_code}')
            results['llm_server'] = False
    except requests.exceptions.ConnectionError:
        print(f'   ❌ Cannot connect to LLM server at {llm_url}')
        print('      Start your LLM server first!')
        results['llm_server'] = False
    except Exception as e:
        print(f'   ❌ LLM server check failed: {e}')
        results['llm_server'] = False
    print()

    # 4. Check Risk Classifier Model
    print('🔴 Risk Classifier Check...')
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        model_name = 'keeper-security/risk-classifier-v2'

        # Try to load tokenizer (fast check)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(f'   ✅ Risk classifier model available')
        print(f'      Model: {model_name}')
        results['risk_classifier'] = True
    except Exception as e:
        print(f'   ❌ Risk classifier not available: {e}')
        print('      Model will be downloaded on first use')
        results['risk_classifier'] = False
    print()

    # 5. Check Log Directory
    print('📝 Log Directory Check...')
    log_dir = Path.home() / '.llm-tracking-log' / 'logs'
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        test_file = log_dir / '.test_write'
        test_file.write_text('test')
        test_file.unlink()
        print(f'   ✅ Log directory writable: {log_dir}')
        results['log_directory'] = True
    except Exception as e:
        print(f'   ❌ Cannot write to log directory: {e}')
        results['log_directory'] = False
    print()

    # 6. Check Monitored Paths
    if watch_paths:
        print('📁 Monitored Paths Check...')
        all_paths_ok = True
        for path_str in watch_paths:
            path = Path(path_str)
            if path.exists() and path.is_dir():
                if os.access(path, os.R_OK):
                    print(f'   ✅ {path}')
                    results[f'path_{path_str}'] = True
                else:
                    print(f'   ⚠️  {path} - Not readable!')
                    all_paths_ok = False
                    results[f'path_{path_str}'] = False
            else:
                print(f'   ❌ {path} - Does not exist or not a directory!')
                all_paths_ok = False
                results[f'path_{path_str}'] = False

        if not all_paths_ok:
            print('   ⚠️  Some paths have issues')
        print()

    # Summary
    print('='*80)
    print('📊 VALIDATION SUMMARY')
    print('='*80 + '\n')

    critical_checks = {
        'Platform': results.get('platform', False),
        'Log Directory': results.get('log_directory', False),
    }

    feature_checks = {
        'LLM Server': results.get('llm_server', False),
        'Risk Classifier': results.get('risk_classifier', False),
    }

    print('Critical Components:')
    for name, status in critical_checks.items():
        icon = '✅' if status else '❌'
        print(f'   {icon} {name}')

    print('\nOptional Features:')
    for name, status in feature_checks.items():
        icon = '✅' if status else '⚠️ '
        status_text = 'Available' if status else 'Unavailable (will run in degraded mode)'
        print(f'   {icon} {name}: {status_text}')

    # Determine what will work
    print('\n' + '='*80)
    print('🚀 MONITOR CAPABILITIES')
    print('='*80 + '\n')

    capabilities = []
    if results.get('package_watchdog', False):
        capabilities.append('✅ File monitoring')
    else:
        capabilities.append('❌ File monitoring (watchdog missing)')

    if results.get('platform', False) and results.get('package_AppKit', False):
        capabilities.append('✅ Application monitoring')
    else:
        capabilities.append('⚠️  Application monitoring (may not work)')

    if results.get('llm_server', False):
        capabilities.append('✅ LLM code analysis')
    else:
        capabilities.append('❌ LLM code analysis (server offline)')

    if results.get('risk_classifier', False):
        capabilities.append('✅ Security risk classification')
    else:
        capabilities.append('⚠️  Security risk classification (model loading...)')

    for capability in capabilities:
        print(f'   {capability}')

    print('\n' + '='*80 + '\n')

    return results


def main():
    """Start monitoring system."""
    import sys
    import argparse

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='LLM Tracking the Log - Monitor code changes with AI analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  llm-monitor                                    # Monitor default folders
  llm-monitor ~/Projects                         # Monitor single custom folder
  llm-monitor ~/Projects ~/Work ~/Code           # Monitor multiple folders
  llm-monitor --path ~/Projects --path ~/Work    # Alternative syntax

Logs stored in: ~/.llm-tracking-log/logs/
        """
    )
    parser.add_argument(
        'paths',
        nargs='*',
        help='Paths to monitor (default: Documents, Desktop, Downloads)'
    )
    parser.add_argument(
        '--path',
        action='append',
        dest='extra_paths',
        help='Additional path to monitor (can be used multiple times)'
    )

    args = parser.parse_args()

    # Collect all paths
    custom_paths = []
    if args.paths:
        custom_paths.extend(args.paths)
    if args.extra_paths:
        custom_paths.extend(args.extra_paths)

    # Expand user paths (~/...)
    if custom_paths:
        custom_paths = [str(Path(p).expanduser().resolve()) for p in custom_paths]

    # Determine watch paths early for validation
    if custom_paths:
        watch_paths_to_validate = custom_paths
    else:
        watch_paths_to_validate = [
            str(Path.home() / 'Documents'),
            str(Path.home() / 'Desktop'),
            str(Path.home() / 'Downloads'),
        ]

    # Validate all requirements before starting
    validation_results = validate_requirements(watch_paths_to_validate)

    print('=' * 80)
    print('UNIFIED MONITORING SYSTEM')
    print('Watchdog (Files) + AppKit (Apps)')
    print('=' * 80)

    # Setup paths - use home directory for installed package
    log_dir = Path.home() / '.llm-tracking-log' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    file_log = log_dir / 'files.log'
    app_log = log_dir / 'apps.log'

    # Watch paths - use custom paths or defaults
    if custom_paths:
        watch_paths = custom_paths
        print(f'\n[SETUP] Custom monitoring paths: {len(watch_paths)} folder(s)')
    else:
        watch_paths = [
            str(Path.home() / 'Documents'),
            str(Path.home() / 'Desktop'),
            str(Path.home() / 'Downloads'),
        ]
        print(f'\n[SETUP] Using default monitoring paths')

    print(f'[SETUP] Log directory: {log_dir}')
    print(f'[SETUP] File log: {file_log.name}')
    print(f'[SETUP] App log: {app_log.name}')

    # Setup LLM client
    llm_client = None
    if LLMClient:
        try:
            llm_log = log_dir / 'llm_analysis.log'
            llm_client = LLMClient(
                base_url="http://127.0.0.1:1234",
                model="deepseek/deepseek-r1-0528-qwen3-8b",
                log_file=llm_log,
            )
            print(f'[SETUP] LLM analysis enabled')
        except Exception as e:
            print(f'[SETUP] LLM not available: {e}')

    # Setup file monitoring (Watchdog)
    print(f'\n[FILE MONITOR] Setting up Watchdog...')
    file_monitor = FileMonitor(file_log, llm_client=llm_client)
    observer = Observer()

    for watch_path in watch_paths:
        if Path(watch_path).exists():
            observer.schedule(file_monitor, watch_path, recursive=True)
            print(f'[FILE MONITOR] Watching: {watch_path}')

    observer.start()
    print('[FILE MONITOR] ✓ Started')

    # Setup app monitoring (AppKit)
    print(f'\n[APP MONITOR] Setting up AppKit...')
    app_monitor = AppMonitor(app_log, check_interval=2.0, llm_client=llm_client)
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
        if llm_client:
            llm_client.close()
        print('[SHUTDOWN] ✓ Shutdown complete\n')


if __name__ == '__main__':
    main()
