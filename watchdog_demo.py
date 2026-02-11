#!/usr/bin/env python3
"""
Educational demo of watchdog file monitoring.
Shows how watchdog detects file system changes in real-time.
"""

import sys
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print('ERROR: watchdog not installed')
    print('Install with: pip install watchdog')
    sys.exit(1)


class FileEventHandler(FileSystemEventHandler):
    """
    This class handles all file system events.
    It inherits from FileSystemEventHandler which provides methods
    for different types of events (created, modified, deleted, moved).
    """

    def __init__(self):
        print('\n[HANDLER] FileEventHandler initialized')
        print('[HANDLER] This handler will receive events from watchdog Observer')
        super().__init__()

    def on_any_event(self, event):
        """
        This method is called for EVERY event.
        Useful for debugging to see all events.
        """
        print(f'\n{"=" * 80}')
        print(f'[EVENT] Type: {event.event_type}')
        print(f'[EVENT] Is Directory: {event.is_directory}')
        print(f'[EVENT] Source Path: {event.src_path}')

        # Some events have a destination path (like move/rename)
        if hasattr(event, 'dest_path'):
            print(f'[EVENT] Destination Path: {event.dest_path}')

        print(f'{"=" * 80}')

    def on_created(self, event):
        """
        Called when a file or directory is created.

        Args:
            event: FileCreatedEvent or DirCreatedEvent
        """
        if not event.is_directory:
            print(f'\n✨ [CREATED] New file detected!')
            print(f'   Path: {event.src_path}')
            print(f'   Filename: {Path(event.src_path).name}')

            # Try to show file size
            try:
                size = Path(event.src_path).stat().st_size
                print(f'   Size: {size} bytes')
            except Exception:
                print(f'   Size: Unable to read')

    def on_modified(self, event):
        """
        Called when a file or directory is modified.
        Note: This can fire multiple times for a single change.

        Args:
            event: FileModifiedEvent or DirModifiedEvent
        """
        if not event.is_directory:
            print(f'\n📝 [MODIFIED] File changed!')
            print(f'   Path: {event.src_path}')
            print(f'   Filename: {Path(event.src_path).name}')

            # Show last modification time
            try:
                mtime = Path(event.src_path).stat().st_mtime
                print(f'   Last modified: {time.ctime(mtime)}')
            except Exception:
                print(f'   Last modified: Unable to read')

    def on_deleted(self, event):
        """
        Called when a file or directory is deleted.

        Args:
            event: FileDeletedEvent or DirDeletedEvent
        """
        if not event.is_directory:
            print(f'\n🗑️  [DELETED] File removed!')
            print(f'   Path: {event.src_path}')
            print(f'   Filename: {Path(event.src_path).name}')

    def on_moved(self, event):
        """
        Called when a file or directory is moved or renamed.

        Args:
            event: FileMovedEvent or DirMovedEvent
        """
        if not event.is_directory:
            print(f'\n📦 [MOVED] File moved/renamed!')
            print(f'   Old path: {event.src_path}')
            print(f'   New path: {event.dest_path}')
            print(f'   Old name: {Path(event.src_path).name}')
            print(f'   New name: {Path(event.dest_path).name}')


def monitor_directory(path: str):
    """
    Start monitoring a directory for file changes.

    Args:
        path: Path to directory to monitor
    """
    watch_path = Path(path).resolve()

    if not watch_path.exists():
        print(f'ERROR: Path does not exist: {path}')
        return

    if not watch_path.is_dir():
        print(f'ERROR: Path is not a directory: {path}')
        return

    print('=' * 80)
    print('WATCHDOG FILE MONITOR - Educational Demo')
    print('=' * 80)
    print(f'\n[SETUP] Monitoring directory: {watch_path}')
    print(f'[SETUP] Watching for: create, modify, delete, move events')
    print(f'[SETUP] Recursive: Yes (includes subdirectories)\n')

    # Step 1: Create the event handler
    print('[STEP 1] Creating event handler...')
    event_handler = FileEventHandler()
    print('[STEP 1] ✓ Event handler created\n')

    # Step 2: Create the observer
    print('[STEP 2] Creating Observer...')
    print('[STEP 2] The Observer runs in a separate thread')
    print('[STEP 2] It watches for file system events and notifies the handler')
    observer = Observer()
    print('[STEP 2] ✓ Observer created\n')

    # Step 3: Schedule the handler to watch the path
    print('[STEP 3] Scheduling handler to watch path...')
    print(f'[STEP 3] Path: {watch_path}')
    print('[STEP 3] Recursive: True')
    observer.schedule(event_handler, str(watch_path), recursive=True)
    print('[STEP 3] ✓ Handler scheduled\n')

    # Step 4: Start the observer
    print('[STEP 4] Starting Observer thread...')
    observer.start()
    print('[STEP 4] ✓ Observer started and running in background\n')

    print('=' * 80)
    print('🔍 MONITORING ACTIVE')
    print('=' * 80)
    print('\nTry these actions to see events:')
    print('  1. Create a file:    echo "test" > test.txt')
    print('  2. Modify a file:    echo "more" >> test.txt')
    print('  3. Move a file:      mv test.txt renamed.txt')
    print('  4. Delete a file:    rm renamed.txt')
    print('\nPress Ctrl+C to stop monitoring...\n')

    try:
        # Keep the main thread running
        # The observer runs in its own thread
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('\n\n[SHUTDOWN] Ctrl+C detected, stopping monitor...')
        observer.stop()
        print('[SHUTDOWN] ✓ Observer stopped')

    # Wait for observer thread to finish
    print('[SHUTDOWN] Waiting for Observer thread to finish...')
    observer.join()
    print('[SHUTDOWN] ✓ Observer thread finished')
    print('\n[SHUTDOWN] Monitor shutdown complete. Goodbye!\n')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python3 watchdog_demo.py <directory_to_watch>')
        print()
        print('Examples:')
        print('  # Watch test folder')
        print('  python3 watchdog_demo.py test/')
        print()
        print('  # Watch current directory')
        print('  python3 watchdog_demo.py .')
        print()
        print('  # Watch Documents folder')
        print('  python3 watchdog_demo.py ~/Documents')
        sys.exit(1)

    watch_path = sys.argv[1]
    monitor_directory(watch_path)
