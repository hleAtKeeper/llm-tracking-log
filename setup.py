#!/usr/bin/env python3
"""Setup script for LLM Tracking the Log."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='llm-tracking-log',
    version='1.0.0',
    description='Monitor MacBook activity (files + apps) for LLM analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/llm-tracking-log',
    packages=find_packages(),
    py_modules=['monitor', 'llm_client', 'risk_classifier'],
    install_requires=[
        'watchdog>=3.0.0',
        'pyobjc-framework-Cocoa>=9.0',
        'requests>=2.31.0',
        'torch>=2.0.0',
        'transformers>=4.30.0',
    ],
    entry_points={
        'console_scripts': [
            'llm-monitor=monitor:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    platforms=['darwin'],
)
