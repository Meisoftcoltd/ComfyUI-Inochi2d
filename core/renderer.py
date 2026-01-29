import numpy as np
import torch
import logging

try:
    import pyo3_inox2d as inox
except ImportError:
    inox = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Inochi2D-Renderer")

class InochiRendererWrapper:
    def __init__(self):
        if inox is None:
            logger.warning("pyo3-inox2d not found. Renderer will operate in mock mode.")
            self.context = None
        else:
            try:
                # Attempt to initialize context, handling potential version variations
                self.context = inox.InoxContext() if hasattr(inox, 'InoxContext') else None
            except Exception as e:
                logger.error(f"Failed to initialize InoxContext: {e}")
                self.context = None

    def load_model(self, model_path):
        """Loads an Inochi2D puppet (.inp or .inx)"""
        if self.context is None:
            return f"MockPuppet({model_path})"

        # Try both common API names for loading
        load_method = (
            getattr(self.context, 'load_puppet', None) or
            getattr(self.context, 'load_model', None) or
            getattr(self.context, 'loadPuppet', None) or
            getattr(self.context, 'loadModel', None)
        )

        if load_method:
            puppet = load_method(str(model_path))
            # If the load method returns None, the model is likely stored in the context itself
            return puppet if puppet is not None else self.context
        else:
            raise RuntimeError("InoxContext has no recognized model loading method.")

    def render_frame(self, puppet, width, height, aa_level=1):
        """Renders a single frame of the puppet and returns (IMAGE, MASK)"""
        if self.context is None or isinstance(puppet, str):
            # Return a mock transparent image and mask
            rgb = torch.zeros((1, height, width, 3))
            mask = torch.zeros((1, height, width))
            return rgb, mask

        try:
            # Configure renderer - using getattr for robustness
            get_renderer = (
                getattr(self.context, 'get_renderer', None) or
                getattr(self.context, 'getRenderer', None)
            )

            if get_renderer:
                renderer = get_renderer()
            else:
                # Fallback: the context itself might act as the renderer in some versions
                renderer = self.context

            # Robust configuration calls - try snake_case and camelCase
            for method in ['resize', 'set_antialiasing', 'setAntialiasing']:
                m = getattr(renderer, method, None)
                if m:
                    if method == 'resize':
                        m(width, height)
                    else:
                        m(aa_level)

            # Ensure puppet state is updated (crucial for .inx models and parameter changes)
            update_method = (
                getattr(puppet, 'update', None) or
                getattr(puppet, 'update_mesh', None) or
                getattr(puppet, 'updateMesh', None)
            )
            if update_method:
                update_method()

            # Attempt to center camera on the puppet to avoid black renders from off-center models
            cam = getattr(renderer, 'camera', None)
            if cam:
                center_on = getattr(cam, 'center_on', None) or getattr(cam, 'centerOn', None)
                if center_on:
                    center_on(puppet)
                elif hasattr(cam, 'position') and hasattr(puppet, 'get_root'):
                    # Fallback for basic camera if center_on is missing
                    try:
                        root = puppet.get_root()
                        if hasattr(root, 'get_transform'):
                            trans = root.get_transform()
                            if hasattr(trans, 'translation'):
                                cam.position = (trans.translation[0], trans.translation[1])
                    except:
                        pass

            # Render cycle
            logger.info(f"Starting render draw call for puppet")
            clear_method = getattr(renderer, 'clear', None) or getattr(renderer, 'Clear', None)
            if clear_method: clear_method()

            draw_method = getattr(renderer, 'draw', None) or getattr(renderer, 'Draw', None)
            if draw_method: draw_method(puppet)
            logger.info(f"Render draw call completed")

            # Retrieve buffer - robust lookup of various possible API names
            read_pixels = (
                getattr(renderer, 'read_pixels', None) or
                getattr(renderer, 'readPixels', None) or
                getattr(renderer, 'get_pixels', None) or
                getattr(renderer, 'getPixels', None) or
                getattr(renderer, 'get_rgba', None) or
                getattr(renderer, 'getRgba', None) or
                getattr(renderer, 'capture', None) or
                getattr(renderer, 'Capture', None) or
                getattr(renderer, 'read', None)
            )

            if not read_pixels:
                raise RuntimeError("Renderer has no pixel retrieval method.")

            rgba = read_pixels()
            if rgba is None or rgba.size == 0:
                logger.error("Renderer returned empty pixel buffer")
                raise RuntimeError("Empty pixel buffer")

            # Convert to PyTorch tensor [B, H, W, C]
            rgba_tensor = torch.from_numpy(rgba).float() / 255.0

            rgb = rgba_tensor[:, :, :3].unsqueeze(0)
            mask = rgba_tensor[:, :, 3].unsqueeze(0)

            return rgb, mask
        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            return torch.zeros((1, height, width, 3)), torch.zeros((1, height, width))
