# ComfyUI-Inochi2d 🎭

Este repositorio contiene una extensión de nodos personalizados para [ComfyUI](https://github.com/comfyanonymous/ComfyUI) que permite el renderizado y la manipulación nativa de modelos de **Inochi2D**.

Inochi2D es un estándar abierto para animación de marionetas 2D en tiempo real, y esta extensión aprovecha el núcleo de [Inox2D](https://github.com/Inochi2D/inox2d) para ofrecer una integración fluida dentro de los flujos de trabajo de ComfyUI.

## 🚀 Características

- Carga nativa de modelos Inochi2D (`.inp`, `.inx`).
- Control detallado de parámetros de rigging (cabeza, ojos, boca, etc.).
- Soporte para parámetros personalizados mediante diccionarios.
- Inyección dinámica de accesorios (assets) en slots del rig.
- Renderizado de alta calidad con soporte para máscaras y anti-aliasing.

## 📦 Instalación

1. Clona este repositorio en tu carpeta `custom_nodes` de ComfyUI:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/Jules/ComfyUI-Inochi2d
   ```
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## 📂 Estructura de Archivos

Para que los nodos funcionen correctamente, organiza tus archivos en la carpeta `assets` del plugin:

- `assets/characters/`: Coloca aquí tus modelos de Inochi2D (`.inp` o `.inx`).
- `assets/props/`: Coloca aquí tus accesorios en formato `.png`. Puedes organizarlos en subcarpetas (categorías).

## 🧩 Nodos

### 📥 Inochi2D Loader
Este nodo carga un modelo de Inochi2D desde la carpeta `assets/characters`.
- **model_file**: Lista desplegable con los modelos detectados.
- **Salida**: `INOCHI_MODEL` - El objeto del modelo cargado listo para ser manipulado o renderizado.

### 👗 Inochi2D Asset Prop
Permite inyectar texturas externas en partes específicas del rig del modelo. Muy útil para cambiar ropa o añadir objetos.
- **inochi_model**: El modelo cargado.
- **category**: Subcarpeta dentro de `assets/props`.
- **asset_name**: Nombre del archivo `.png` (sin extensión).
- **target_slot**: El nombre del "slot" o parte del rig donde se inyectará la textura (ej: `Hand_Slot`).
- **Salida**: `INOCHI_MODEL` - El modelo con el accesorio aplicado.

### 🎛️ Inochi2D Parameter Control
Permite controlar los parámetros de animación definidos en el modelo.
- **inochi_model**: El modelo a controlar.
- **head_x / head_y**: Control de movimiento de la cabeza (rango sugerido: -1.0 a 1.0).
- **eye_open**: Apertura de ojos (0.0 a 1.0).
- **mouth_open**: Apertura de boca (0.0 a 1.0).
- **custom_params**: (Opcional) Un diccionario para controlar parámetros adicionales definidos en el rig.
- **Salida**: `INOCHI_MODEL` - El modelo con los parámetros actualizados.

### 🖼️ Inochi2D Renderer
Renderiza el estado actual del modelo a una imagen y una máscara.
- **inochi_model**: El modelo a renderizar.
- **width / height**: Dimensiones de la imagen de salida.
- **aa_level**: Nivel de anti-aliasing (1 a 8). Un valor más alto mejora la calidad pero aumenta el tiempo de procesamiento.
- **Salida**:
  - `IMAGE`: La imagen renderizada (formato compatible con ComfyUI).
  - `MASK`: La máscara alfa del modelo, útil para post-procesamiento.

## 🚀 Ejemplo de Flujo Completo

Para empezar a usar estos nodos, puedes seguir este flujo típico:

1. **Inochi2D Loader**: Carga tu modelo `.inp` o `.inx` desde `assets/characters`.
2. **Inochi2D Asset Prop** (Opcional): Añade accesorios o cambia texturas en slots específicos del rig.
3. **Inochi2D Parameter Control**: Ajusta la expresión (ojos, boca) y posición de la cabeza.
4. **Inochi2D Renderer**: Genera la imagen final y su correspondiente máscara.

### 📥 Importar Ejemplo
Puedes encontrar un ejemplo de flujo de trabajo listo para usar en `examples/workflow.json`. Para cargarlo:
- Arrastra el archivo JSON directamente a la interfaz de ComfyUI.
- O utiliza el botón "Load" en el panel lateral de ComfyUI.

> **Nota**: Asegúrate de tener al menos un modelo en `assets/characters/` para que el flujo cargue correctamente.

## 🔗 Referencias Originales

Este proyecto no sería posible sin el increíble trabajo de la comunidad de Inochi2D:

- **[Inochi2D](https://github.com/Inochi2D/inochi2d)**: El estándar y SDK original.
- **[Inox2D](https://github.com/Inochi2D/inox2d)**: La implementación nativa en Rust utilizada para el renderizado.
- **[Inochi Creator](https://github.com/Inochi2D/inochi-creator)**: La herramienta oficial para crear y riggear modelos Inochi2D.
- **[pyo3-inox2d]**: Los bindings de Python que permiten la comunicación entre ComfyUI e Inox2D.

## ⚖️ Licencia

Este proyecto está bajo la licencia especificada en el archivo LICENSE. Asegúrate de revisar también las licencias de Inochi2D e Inox2D para uso comercial.
