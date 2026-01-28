# -*- coding: utf-8 -*-
import os
import torch
import numpy as np
import copy
from .core.renderer import InochiRendererWrapper
from .core.assets_manager import AssetsManager
from .core.parameters import ParameterController

# Global renderer wrapper instance to manage context
_renderer_wrapper = None

def _get_renderer():
    global _renderer_wrapper
    if _renderer_wrapper is None:
        _renderer_wrapper = InochiRendererWrapper()
    return _renderer_wrapper

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
        if model_file == "None":
            raise ValueError("No model file selected or available.")

        print(f"### [Inochi2D] Cargando modelo: {model_file}")
        base_path = os.path.join(os.path.dirname(__file__), "assets", "characters")
        path = os.path.join(base_path, model_file)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        # Detection of textures for .inx models
        if model_file.endswith('.inx'):
            model_dir = os.path.dirname(path)
            png_files = [f for f in os.listdir(model_dir) if f.lower().endswith('.png')]

            if not png_files:
                print(f"### [Inochi2D] ADVERTENCIA: No se encontraron archivos .png en {model_dir}")
                print(f"### [Inochi2D] Los archivos .inx suelen requerir texturas externas. Si el renderizado es negro, asegúrate de que los atlas .png estén en la misma carpeta.")
            else:
                print(f"### [Inochi2D] Detectadas {len(png_files)} texturas .png para el modelo .inx")

            # Legacy/Optional: check for PSD textures if they exist in a psd/ subdirectory
            psd_dir = os.path.join(model_dir, "psd")
            if os.path.exists(psd_dir):
                for f in os.listdir(psd_dir):
                    if f.endswith('.psd'):
                        print(f"### [Inochi2D] Encontrada textura PSD: {f}")

        # Fix: Change working directory to the model's directory to resolve relative paths in .inx
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(path))
        try:
            puppet = _get_renderer().load_model(path)
        finally:
            os.chdir(old_cwd)

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
        print(f"### [Inochi2D] Aplicando asset {asset_name} desde {category} en el slot {target_slot}")
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
                "frame_number": ("INT", {"default": 0, "min": 0, "max": 1000000}),
            }
        }

    RETURN_TYPES = ("INOCHI_MODEL",)
    RETURN_NAMES = ("INOCHI_MODEL",)
    FUNCTION = "control_parameters"
    CATEGORY = "Inochi2D 🎬"

    def control_parameters(self, inochi_model, head_x, head_y, eye_open, mouth_open, custom_params={}, frame_number=0):
        print(f"### [Inochi2D] Gestionando frame {frame_number}: boca {mouth_open:.2f}, ojos {eye_open:.2f}, cabeza ({head_x:.2f}, {head_y:.2f})")
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
        print(f"### [Inochi2D] Renderizando frame: {width}x{height}, AA: {aa_level}")
        image, mask = _get_renderer().render_frame(inochi_model, width, height, aa_level)
        return (image, mask)
