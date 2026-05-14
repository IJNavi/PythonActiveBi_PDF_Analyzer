#!/usr/bin/env python3
"""Script para executar o Analisador de Documentos"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import main

if __name__ == "__main__":
    main()