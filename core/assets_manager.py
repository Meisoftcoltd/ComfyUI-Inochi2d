from PIL import Image
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger("Inochi2D-Assets")

class AssetsManager:
    def __init__(self, base_props_path):
        self.base_props_path = Path(base_props_path)

    def inject_asset(self, puppet, category, asset_name, target_slot):
        """
        Injects a texture asset into a specific slot of the Inochi2D puppet.
        """
        asset_path = self.base_props_path / category / f"{asset_name}.png"

        if not asset_path.exists():
            logger.error(f"Asset not found: {asset_path}")
            return False

        try:
            # Load and prepare image
            with Image.open(asset_path) as img:
                img = img.convert("RGBA")
                texture_data = np.array(img)

            if isinstance(puppet, str): # Mock
                logger.info(f"Mock: Injecting {asset_path} into {target_slot}")
                return True

            # Robust part lookup
            find_part = getattr(puppet, 'find_part', None) or getattr(puppet, 'get_part', None)
            if not find_part:
                logger.warning("Puppet object has no part lookup method.")
                return False

            part = find_part(target_slot)
            if part:
                set_texture = getattr(part, 'set_texture', None) or getattr(part, 'replace_texture', None)
                if set_texture:
                    set_texture(texture_data)
                    return True
                else:
                    logger.warning(f"Part '{target_slot}' does not support texture replacement.")
            else:
                logger.warning(f"Slot '{target_slot}' not found in puppet rig.")

            return False

        except Exception as e:
            logger.error(f"Error injecting asset: {e}")
            return False

    def list_available_assets(self, category=None):
        path = self.base_props_path
        if category:
            path = path / category

        if not path.exists():
            return []

        return [f.stem for f in path.glob("*.png")]
