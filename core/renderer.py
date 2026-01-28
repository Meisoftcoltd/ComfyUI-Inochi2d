# -*- coding: utf-8 -*-
import numpy as np
import torch
import logging

# CORRECCIÓN: Usar nombre correcto del paquete (inox2d en lugar de pyo3_inox2d)
try:
    import inox2d as inox
except ImportError:
    HAS_INOX2D = True
    logging.info(f"Inox2D loaded successfully! Spec: {getattr(inox, 'INOCHI2D_SPEC_VERSION', 'unknown')}")
except ImportError as e:
    inox = None
    HAS_INOX2D = False
    logging.warning(f"inox2d not found: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Inochi2D-Renderer")

class InochiRendererWrapper:
    def __init__(self):
        if inox is None:
            logger.warning("inox2d not found. Renderer will operate in mock mode.")
            logger.warning("="*70)
            logger.warning("inox2d not found. Renderer will operate in mock mode.")
            logger.warning("")
            logger.warning("To install inox2d:")
            logger.warning("1. Install Rust: https://rustup.rs/")
            logger.warning("2. pip install maturin")
            logger.warning("3. git clone https://github.com/Inochi2D/inox2d")
            logger.warning("4. cd inox2d && pip install .")
            logger.warning("5. Restart ComfyUI")
            logger.warning("="*70)
            self.context = None
        else:
            try:
                # La API puede variar según la versión de desarrollo
                # Probar diferentes nombres de constructores conocidos
                if hasattr(inox, 'InoxContext'):
                    self.context = inox.InoxContext()
                elif hasattr(inox, 'Context'):
                    self.context = inox.Context()
                elif hasattr(inox, 'Renderer'):
                    self.context = inox.Renderer()
                else:
                    logger.error(f"Unknown inox2d API. Available attributes: {dir(inox)}")
                    self.context = None

                if self.context:
                    logger.info("Inox2D context initialized successfully!")

            except Exception as e:
                logger.error(f"Failed to initialize inox2d context: {e}")
                logger.error(f"Available attributes: {dir(inox)}")
                self.context = None

    def load_model(self, model_path):
        """Loads an Inochi2D puppet (.inp or .inx)"""
        if self.context is None:
            return f"MockPuppet({model_path})"

        # Attempt to find the loading method
        load_method = getattr(self.context, 'load_puppet', None) or \
                      getattr(self.context, 'load_model', None) or \
                      getattr(self.context, 'load', None)

        if load_method:
            return load_method(str(model_path))
        else:
            raise RuntimeError(f"Inox context has no recognized model loading method. API: {dir(self.context)}")

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
            if get_renderer:
                renderer = get_renderer()
            else:
                # Some versions might have the context itself act as the renderer or have a direct 'renderer' attr
                renderer = getattr(self.context, 'renderer', self.context)

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
            if hasattr(renderer, 'clear'): renderer.clear()
            if hasattr(renderer, 'draw'): renderer.draw(puppet)

            # Retrieve buffer
            read_pixels = getattr(renderer, 'read_pixels', None) or \
                          getattr(renderer, 'get_pixels', None) or \
                          getattr(renderer, 'pixels', None)

            if not read_pixels:
                raise RuntimeError("Renderer has no pixel retrieval method.")

            # If it's a property, don't call it
            rgba = read_pixels() if callable(read_pixels) else read_pixels

            if rgba is None or (isinstance(rgba, np.ndarray) and rgba.size == 0):
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
