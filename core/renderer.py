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

        load_method = getattr(self.context, 'load_puppet', None) or getattr(self.context, 'load_model', None)
        if load_method:
            return load_method(str(model_path))
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
            get_renderer = getattr(self.context, 'get_renderer', None)
            if not get_renderer:
                raise RuntimeError("InoxContext does not provide a renderer.")

            renderer = get_renderer()

            # Robust configuration calls
            if hasattr(renderer, 'resize'): renderer.resize(width, height)
            if hasattr(renderer, 'set_antialiasing'): renderer.set_antialiasing(aa_level)

            # Ensure puppet state is updated (crucial for .inx models and parameter changes)
            if hasattr(puppet, 'update'):
                puppet.update()
            elif hasattr(puppet, 'update_mesh'):
                puppet.update_mesh()

            # Attempt to center camera on the puppet to avoid black renders from off-center models
            if hasattr(renderer, 'camera'):
                cam = renderer.camera
                if hasattr(cam, 'center_on'):
                    cam.center_on(puppet)
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
            if hasattr(renderer, 'clear'): renderer.clear()
            if hasattr(renderer, 'draw'): renderer.draw(puppet)
            logger.info(f"Render draw call completed")

            # Retrieve buffer - robust lookup of various possible API names
            read_pixels = (
                getattr(renderer, 'read_pixels', None) or
                getattr(renderer, 'get_pixels', None) or
                getattr(renderer, 'get_rgba', None) or
                getattr(renderer, 'capture', None)
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
