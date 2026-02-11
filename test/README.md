# Test Files for Monitoring

This folder contains test files to verify the monitoring system.

## Files

- **main.py** - Main script that imports utils and config
- **utils.py** - Utility functions (imported by main.py)
- **config.py** - Configuration settings (imported by main.py)

## Testing the Monitor

1. **Start monitoring**:
   ```bash
   cd /Users/hoangle/Documents/work/ai-factory/projects/LLM_tracking_the_log
   ./start_monitoring.sh
   ```

2. **Run the test script**:
   ```bash
   python3 test/main.py
   ```

3. **Create a new file** (to test file creation monitoring):
   ```bash
   echo "print('test')" > test/new_script.py
   ```

4. **Modify a file** (to test modification monitoring):
   ```bash
   echo "# New comment" >> test/utils.py
   ```

5. **Check the logs**:
   ```bash
   # View combined log
   tail -f logs/combined.log

   # View file monitor log
   tail -f logs/monitors/files.log

   # Search for dependencies
   cat logs/monitors/files.log | grep dependency
   ```

## What Should Happen

When you create/modify files in this test folder:
- Main file content is logged
- Dependencies (utils.py, config.py) are automatically detected and logged
- Full content of each file is captured in JSON format
