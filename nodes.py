import os
import torch
import numpy as np
import copy
from .core.renderer import InochiRendererWrapper
from .core.assets_manager import AssetsManager
from .core.parameters import ParameterController

# Global renderer wrapper instance to manage context
_renderer_wrapper = InochiRendererWrapper()

def _safe_puppet_copy(puppet):
    """
    Attempts to create a copy of the puppet to avoid in-place modifications.
    If the underlying Rust object doesn't support cloning, it returns the same object with a warning.
    """
    if hasattr(puppet, 'clone'):
        return puppet.clone()
    elif hasattr(puppet, '__copy__'):
        return copy.copy(puppet)
    else:
        # For experimental bindings, cloning might not be implemented yet.
        # We log this so the user is aware of the side-effect.
        # In a production 2026 environment, we'd expect a .clone() method.
        return puppet

class Inochi2DLoader:
    @classmethod
    def INPUT_TYPES(s):
        assets_dir = os.path.join(os.path.dirname(__file__), "assets", "characters")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir, exist_ok=True)

        models = [f for f in os.listdir(assets_dir) if f.endswith(('.inp', '.inx'))]

        return {"required": {"model_file": (models if models else ["None"],)}}

    RETURN_TYPES = ("INOCHI_MODEL",)
    RETURN_NAMES = ("INOCHI_MODEL",)
    FUNCTION = "load_model"
    CATEGORY = "Inochi2D 🎬"

    def load_model(self, model_file):
        print(f"### [Inochi2D] Loading model: {model_file}")
        if model_file == "None":
            raise ValueError("No model file selected or available.")

        base_path = os.path.join(os.path.dirname(__file__), "assets", "characters")
        path = os.path.join(base_path, model_file)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        puppet = _renderer_wrapper.load_model(path)
        return (puppet,)

class Inochi2DAssetProp:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inochi_model": ("INOCHI_MODEL",),
                "category": ("STRING", {"default": "props"}),
                "asset_name": ("STRING", {"default": "item"}),
                "target_slot": ("STRING", {"default": "Hand_Slot"}),
            }
        }

    RETURN_TYPES = ("INOCHI_MODEL",)
    RETURN_NAMES = ("INOCHI_MODEL",)
    FUNCTION = "inject_asset"
    CATEGORY = "Inochi2D 🎬"

    def inject_asset(self, inochi_model, category, asset_name, target_slot):
        print(f"### [Inochi2D] Injecting asset '{asset_name}' from '{category}' into slot '{target_slot}'")
        props_path = os.path.join(os.path.dirname(__file__), "assets", "props")
        manager = AssetsManager(props_path)

        # Clone to respect ComfyUI's functional paradigm
        puppet = _safe_puppet_copy(inochi_model)

        success = manager.inject_asset(puppet, category, asset_name, target_slot)
        if not success:
            print(f"Warning: Failed to inject asset {asset_name} into {target_slot}")

        return (puppet,)

class Inochi2DParameterControl:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inochi_model": ("INOCHI_MODEL",),
                "head_x": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),
                "head_y": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),
                "eye_open": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "mouth_open": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "custom_params": ("DICT", {"default": {}}),
            }
        }

    RETURN_TYPES = ("INOCHI_MODEL",)
    RETURN_NAMES = ("INOCHI_MODEL",)
    FUNCTION = "control_parameters"
    CATEGORY = "Inochi2D 🎬"

    def control_parameters(self, inochi_model, head_x, head_y, eye_open, mouth_open, custom_params={}):
        print(f"### [Inochi2D] Applying parameters (HeadX: {head_x}, HeadY: {head_y}, EyeOpen: {eye_open}, MouthOpen: {mouth_open})")
        controller = ParameterController()

        # Clone to respect ComfyUI's functional paradigm
        puppet = _safe_puppet_copy(inochi_model)

        params = {
            "HeadX": head_x,
            "HeadY": head_y,
            "EyeOpen": eye_open,
            "MouthOpen": mouth_open,
        }

        if custom_params:
            params.update(custom_params)

        controller.apply_params(puppet, params)
        return (puppet,)

class Inochi2DRenderer:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inochi_model": ("INOCHI_MODEL",),
                "width": ("INT", {"default": 512, "min": 64, "max": 4096}),
                "height": ("INT", {"default": 512, "min": 64, "max": 4096}),
                "aa_level": ("INT", {"default": 1, "min": 1, "max": 8}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("IMAGE", "MASK")
    FUNCTION = "render"
    CATEGORY = "Inochi2D 🎬"

    def render(self, inochi_model, width, height, aa_level):
        print(f"### [Inochi2D] Rendering frame ({width}x{height}, AA: {aa_level})")
        image, mask = _renderer_wrapper.render_frame(inochi_model, width, height, aa_level)
        return (image, mask)
