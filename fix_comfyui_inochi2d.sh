#!/bin/bash
# fix_comfyui_inochi2d.sh - Repair script for ComfyUI-Inochi2d

echo "### [Inochi2D] Starting Repair Script..."

# 1. Fix core/__init__.py
if [ ! -s "core/__init__.py" ] || ! grep -q "InochiRendererWrapper" "core/__init__.py"; then
    echo "### [Inochi2D] Repairing core/__init__.py..."
    cat > core/__init__.py <<EOF
# -*- coding: utf-8 -*-
"""
Core module for Inochi2D rendering and manipulation
"""

from .renderer import InochiRendererWrapper
from .assets_manager import AssetsManager
from .parameters import ParameterController

__all__ = [
    'InochiRendererWrapper',
    'AssetsManager',
    'ParameterController',
]
EOF
else
    echo "✓ core/__init__.py seems OK"
fi

# 2. Fix nodes.py encoding
if ! head -n 1 nodes.py | grep -q "utf-8"; then
    echo "### [Inochi2D] Adding UTF-8 header to nodes.py..."
    sed -i '1i# -*- coding: utf-8 -*-' nodes.py
else
    echo "✓ nodes.py has UTF-8 header"
fi

# 3. Verify nodes.py lazy initialization
if grep -q "_renderer_wrapper = InochiRendererWrapper()" nodes.py; then
    echo "### [Inochi2D] WARNING: nodes.py still uses eager initialization. Consider manual update if tests fail."
else
    echo "✓ nodes.py seems to use lazy initialization"
fi

# 4. Run tests
if [ -f "test_comfyui_inochi2d.py" ]; then
    echo "### [Inochi2D] Running tests..."
    python3 test_comfyui_inochi2d.py
else
    echo "⚠ test_comfyui_inochi2d.py not found"
fi

echo "### [Inochi2D] Repair process finished."
