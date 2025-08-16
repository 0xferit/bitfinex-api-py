# Publishing to PyPI - Quick Guide

## Option 1: Use the publish script (Recommended)

1. **Get your PyPI API token:**
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Name: "bitfinex-api-py-postonly"
   - Scope: "Entire account" (or project-specific if it exists)
   - Copy the token (starts with `pypi-`)

2. **Run the publish script:**
   ```bash
   PYPI_TOKEN=pypi-your-token-here ./publish.sh
   ```

## Option 2: Manual upload

1. **Set environment variables:**
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-token-here
   ```

2. **Upload:**
   ```bash
   twine upload dist/*
   ```

## Option 3: Use .pypirc file

1. **Create ~/.pypirc:**
   ```ini
   [distutils]
   index-servers = pypi

   [pypi]
   username = __token__
   password = pypi-your-token-here
   ```

2. **Secure the file:**
   ```bash
   chmod 600 ~/.pypirc
   ```

3. **Upload:**
   ```bash
   twine upload dist/*
   ```

## After Publishing

1. **Verify on PyPI:**
   - Visit https://pypi.org/project/bitfinex-api-py-postonly/
   - Check that description renders correctly

2. **Test installation:**
   ```bash
   pip install bitfinex-api-py-postonly
   python -c "from bfxapi import Client; print('Success!')"
   ```

3. **Create GitHub release:**
   ```bash
   git tag v3.0.5.post1
   git push origin v3.0.5.post1
   ```

## Troubleshooting

- **"Invalid authentication"**: Token is wrong or expired
- **"Package already exists"**: Need to increment version in setup.py
- **"File already exists"**: Can't overwrite - increment version

## Security Note

⚠️ **NEVER commit your PyPI token to Git!**