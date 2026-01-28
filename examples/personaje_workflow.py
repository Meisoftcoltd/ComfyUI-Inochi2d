import sys
import os
import torch

# Simple mock for ComfyUI environment if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Use a try-except to handle import variations
try:
    from ComfyUI_Inochi2d.nodes import (
        Inochi2DLoader,
        Inochi2DAssetProp,
        Inochi2DRenderer,
        Inochi2DParameterControl
    )
except ImportError:
    # If not installed as a package, try direct import if in same root
    from nodes import (
        Inochi2DLoader,
        Inochi2DAssetProp,
        Inochi2DRenderer,
        Inochi2DParameterControl
    )

def personaje_workflow(prompt):
    """
    Demuestra el flujo de trabajo del 'Personaje'.
    1. Analiza el prompt para extraer el token del asset.
    2. Carga el puppet del Personaje.
    3. Inyecta el asset correspondiente.
    4. Render the frame.
    """
    print(f"--- Procesando Prompt: '{prompt}' ---")

    # 1. Extraction logic
    # In a real scenario, this could use an LLM or regex
    available_assets = ["item1", "item2", "item3"]
    token = next((asset for asset in available_assets if asset in prompt.lower()), "default")

    print(f"Paso 1: Token de asset extraído -> {token}")

    # 2. Node Initialization
    loader = Inochi2DLoader()
    prop_injector = Inochi2DAssetProp()
    param_control = Inochi2DParameterControl()
    renderer = Inochi2DRenderer()

    # 3. Load Puppet
    # Para este ejemplo, asumimos que personaje.inp existe
    model_file = "personaje.inp"
    print(f"Paso 2: Cargando puppet {model_file}...")
    puppet, = loader.load_model(model_file)

    # 4. Inject Asset (Hot-swap texture)
    print(f"Paso 3: Inyectando {token}.png en Hand_Slot...")
    puppet, = prop_injector.inject_asset(
        inochi_model=puppet,
        category="props",
        asset_name=token,
        target_slot="Hand_Slot"
    )

    # 5. Set Animation/Parameters (e.g., Talking pose)
    print(f"Paso 4: Ajustando parámetros para hablar...")
    puppet, = param_control.control_parameters(
        inochi_model=puppet,
        head_x=0.0,
        head_y=0.1,
        eye_open=0.9,
        mouth_open=0.8
    )

    # 6. Render Frame
    print(f"Paso 5: Renderizando frame...")
    image, mask = renderer.render(
        inochi_model=puppet,
        width=1024,
        height=1024,
        aa_level=2
    )

    print(f"Result: Image Tensor {image.shape}, Mask Tensor {mask.shape}")
    print("Flujo de trabajo completo. La salida puede ser enviada a nodos externos de LipSync (ej. LivePortrait).")

    return image, mask

if __name__ == "__main__":
    # Simular el caso de uso
    personaje_workflow("Muestra el item1")
