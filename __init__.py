"""
@author: Jules
@title: ComfyUI-Inochi2d
@nickname: Inochi2D
@description: Native Inochi2D rendering and manipulation for ComfyUI
"""

import logging

VERSION = "0.1.1"

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

try:
    from .nodes import Inochi2DLoader, Inochi2DAssetProp, Inochi2DParameterControl, Inochi2DRenderer

    NODE_CLASS_MAPPINGS = {
        "Inochi2DLoader": Inochi2DLoader,
        "Inochi2DAssetProp": Inochi2DAssetProp,
        "Inochi2DParameterControl": Inochi2DParameterControl,
        "Inochi2DRenderer": Inochi2DRenderer
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "Inochi2DLoader": "📥 Inochi2D Loader",
        "Inochi2DAssetProp": "👗 Inochi2D Asset Prop",
        "Inochi2DParameterControl": "🎛️ Inochi2D Parameter Control",
        "Inochi2DRenderer": "🖼️ Inochi2D Renderer"
    }
except ImportError as e:
    logging.error(f"Failed to load Inochi2D nodes: {e}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'VERSION']
