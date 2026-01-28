# -*- coding: utf-8 -*-
import sys
import os
import importlib

def test_imports():
    print("Test 1: Core Imports")
    try:
        # Add current directory to path so 'core' can be imported as a top-level package
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        from core import InochiRendererWrapper, AssetsManager, ParameterController
        print("✓ OK")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    return True

def test_renderer_mock():
    print("\nTest 2: Renderer Mock")
    try:
        from core.renderer import InochiRendererWrapper
        renderer = InochiRendererWrapper()
        puppet = renderer.load_model("/fake/test.inp")
        img, mask = renderer.render_frame(puppet, 512, 512, 1)
        print(f"✓ Image shape: {img.shape}")
        print(f"✓ Mask shape: {mask.shape}")
        if img.shape == (1, 512, 512, 3) and mask.shape == (1, 512, 512):
            print("✓ OK")
        else:
            print("✗ Unexpected shapes")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    return True

def test_nodes_import():
    print("\nTest 3: Nodes Import")
    try:
        # The NODE_CLASS_MAPPINGS are defined in the root __init__.py
        # We need to load the current directory as a package.

        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        package_name = os.path.basename(current_dir)

        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Import the package itself (which executes __init__.py)
        pkg = importlib.import_module(f"{package_name}")

        if hasattr(pkg, 'NODE_CLASS_MAPPINGS'):
            print(f"✓ Found {len(pkg.NODE_CLASS_MAPPINGS)} nodes in NODE_CLASS_MAPPINGS:")
            for name in pkg.NODE_CLASS_MAPPINGS:
                print(f"  - {name}")
            if len(pkg.NODE_CLASS_MAPPINGS) >= 4:
                print("✓ OK")
                return True
            else:
                print(f"✗ Found only {len(pkg.NODE_CLASS_MAPPINGS)} nodes, expected at least 4")
                return False
        else:
            print("✗ pkg has no attribute 'NODE_CLASS_MAPPINGS'")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = True
    success &= test_imports()
    success &= test_renderer_mock()
    success &= test_nodes_import()

    if success:
        print("\n✨ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
