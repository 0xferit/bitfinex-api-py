# PyPI Upload Instructions for bitfinex-api-py-postonly

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify email address
   - Enable 2FA (recommended)

2. **API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create new API token with scope "Entire account" 
   - Save token securely (shown only once)

3. **Install Tools**
   ```bash
   pip install --upgrade pip setuptools wheel twine
   ```

## Build Process

### 1. Clean Previous Builds
```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Verify Package Metadata
```bash
python setup.py check
```

### 3. Build Distribution Files
```bash
# Build both wheel and source distribution
python setup.py sdist bdist_wheel
```

### 4. Verify Build Contents
```bash
# Check what files are included
tar -tzf dist/bitfinex-api-py-postonly-*.tar.gz | head -20

# Verify no test files or CLAUDE.md included
tar -tzf dist/bitfinex-api-py-postonly-*.tar.gz | grep -E "(test_|CLAUDE\.md)" || echo "✓ No test files found"
```

## Upload to PyPI

### Test Upload (TestPyPI) - Recommended First

1. **Upload to TestPyPI**
   ```bash
   twine upload --repository testpypi dist/*
   ```
   Username: `__token__`
   Password: `<your-test-pypi-token>`

2. **Test Installation**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ bitfinex-api-py-postonly
   ```

3. **Verify Package Works**
   ```python
   from bfxapi import Client
   print("Package imported successfully")
   ```

### Production Upload (PyPI)

1. **Final Checks**
   - [ ] All tests pass
   - [ ] Documentation updated
   - [ ] Version number correct in setup.py
   - [ ] GitHub release created
   - [ ] Package tested on TestPyPI

2. **Upload to PyPI**
   ```bash
   twine upload dist/*
   ```
   Username: `__token__`
   Password: `<your-pypi-token>`

3. **Verify on PyPI**
   - Check https://pypi.org/project/bitfinex-api-py-postonly/
   - Verify description renders correctly
   - Check all metadata displayed

## Post-Upload Tasks

### 1. Test Installation from PyPI
```bash
# Fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from PyPI
pip install bitfinex-api-py-postonly

# Test import
python -c "from bfxapi import Client; print('Success')"
```

### 2. Create GitHub Release
```bash
# Tag the release
git tag v3.0.5.post1
git push origin v3.0.5.post1

# Create release on GitHub
gh release create v3.0.5.post1 \
  --title "v3.0.5.post1 - POST_ONLY Enforcement Fork" \
  --notes "Safety-enhanced fork with automatic POST_ONLY enforcement on all orders" \
  dist/*
```

### 3. Update README if needed
Add PyPI badges:
```markdown
[![PyPI version](https://badge.fury.io/py/bitfinex-api-py-postonly.svg)](https://pypi.org/project/bitfinex-api-py-postonly/)
[![Downloads](https://pepy.tech/badge/bitfinex-api-py-postonly)](https://pepy.tech/project/bitfinex-api-py-postonly)
```

## Version Management

### Updating Version
When releasing updates:

1. Update version in `setup.py`
2. Follow semantic versioning:
   - MAJOR.MINOR.PATCH.postN
   - Keep base version aligned with upstream (3.0.5)
   - Increment postN for fork-specific changes

Example versions:
- `3.0.5.post1` - First fork release
- `3.0.5.post2` - Bug fixes in fork
- `3.0.6.post1` - When upstream updates to 3.0.6

## Troubleshooting

### "Package already exists"
- Increment version number in setup.py
- Cannot overwrite existing versions on PyPI

### "Invalid distribution"
```bash
# Check with twine before upload
twine check dist/*
```

### Authentication Issues
- Use `__token__` as username (not your PyPI username)
- Token must start with `pypi-`
- Check token has upload permissions

### Missing Dependencies
Ensure setup.py has all required packages in `install_requires`

## Security Notes

1. **Never commit tokens** to repository
2. **Use .pypirc** for credentials (optional):
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-...

   [testpypi]
   username = __token__
   password = pypi-...
   ```
   Then: `chmod 600 ~/.pypirc`

3. **Use environment variables** alternatively:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-...
   twine upload dist/*
   ```

## Maintenance

### Regular Tasks
- Monitor for upstream updates
- Keep fork synchronized where safe
- Respond to issues on GitHub
- Update documentation as needed

### Upstream Sync Strategy
1. Monitor https://github.com/bitfinexcom/bitfinex-api-py
2. Review changes for compatibility
3. Cherry-pick safe updates
4. Never merge order submission changes that bypass POST_ONLY
5. Test thoroughly before release

## Support Channels

- GitHub Issues: https://github.com/0xferit/bitfinex-api-py/issues
- PyPI Project: https://pypi.org/project/bitfinex-api-py-postonly/