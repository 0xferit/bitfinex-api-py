#!/usr/bin/env python3
"""Test that the installed package enforces POST_ONLY correctly."""

import sys
import tempfile
import subprocess
import os

def test_package():
    # Create temp venv
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_path = os.path.join(tmpdir, "test_venv")
        
        # Create virtual environment
        print("Creating test virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        
        # Get pip and python paths
        pip_path = os.path.join(venv_path, "bin", "pip")
        python_path = os.path.join(venv_path, "bin", "python")
        
        # Install the package
        print("Installing package...")
        wheel_file = "dist/bitfinex_api_py_postonly-3.0.5.post1-py3-none-any.whl"
        subprocess.run([pip_path, "install", wheel_file], check=True, capture_output=True)
        
        # Test import and POST_ONLY enforcement
        test_code = """
from bfxapi._utils.post_only_enforcement import enforce_post_only
from bfxapi.constants.order_flags import POST_ONLY

# Test enforcement
result = enforce_post_only(0)
assert result == 4096, f"Expected 4096, got {result}"
print("✓ POST_ONLY enforcement works")

# Test enforcement with existing flags
result = enforce_post_only(64)  # HIDDEN flag
assert result == 4160, f"Expected 4160, got {result}"
print("✓ Flag preservation works")

# Test import
from bfxapi import Client
print("✓ Package imports correctly")

print("\\n✅ All package tests passed!")
"""
        
        print("Running tests...")
        result = subprocess.run(
            [python_path, "-c", test_code],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"✗ Test failed:\n{result.stderr}")
            sys.exit(1)
        
        print(result.stdout)

if __name__ == "__main__":
    test_package()