"""
Hugging Face Spaces Entry Point
Adaptive Liquidity Provision Engine Dashboard

This is the main entry point for the Hugging Face Space.
It imports and runs the advanced analytics dashboard.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the dashboard
from src.visualization.advanced_dashboard import main

if __name__ == "__main__":
    main()
