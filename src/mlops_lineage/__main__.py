"""
Main entry point for mlops_lineage package

Allows running the CLI via: python -m mlops_lineage

Author: MLOps Team
Date: January 2026
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
