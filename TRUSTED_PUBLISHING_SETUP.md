# PyPI Trusted Publishing Configuration

## What is Trusted Publishing?

Trusted Publishing uses OpenID Connect (OIDC) to securely publish packages from GitHub Actions to PyPI without managing API tokens. It's more secure and convenient than traditional token-based authentication.

## Setup Instructions

### Step 1: Configure PyPI Trusted Publisher

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the following details:

   - **PyPI Project Name**: `bitfinex-api-py-postonly`
   - **Owner**: `0xferit`
   - **Repository name**: `bitfinex-api-py`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi` (optional but recommended)

4. Click "Add"

### Step 2: Push the Workflow to GitHub

```bash
git add .github/workflows/publish.yml
git commit -m "Add PyPI Trusted Publishing workflow"
git push origin master
```

### Step 3: Create a GitHub Environment (Optional but Recommended)

1. Go to your repository on GitHub: https://github.com/0xferit/bitfinex-api-py
2. Go to Settings → Environments
3. Click "New environment"
4. Name it `pypi`
5. Add protection rules if desired (e.g., require review for releases)

## How to Publish

### Automatic Publishing (Recommended)

1. Create a new release on GitHub:
   ```bash
   git tag v3.0.5.post1
   git push origin v3.0.5.post1
   ```

2. Go to https://github.com/0xferit/bitfinex-api-py/releases/new
3. Choose the tag you just created
4. Fill in release title and notes
5. Click "Publish release"

The workflow will automatically:
- Build the package
- Upload to PyPI using Trusted Publishing
- No manual token needed!

### Manual Testing (Optional)

You can manually trigger the workflow for testing:

1. Go to https://github.com/0xferit/bitfinex-api-py/actions
2. Click on "Publish to PyPI" workflow
3. Click "Run workflow"
4. This will publish to TestPyPI for testing

## Workflow Features

The `publish.yml` workflow includes:

- **Automatic building**: Creates both wheel and source distributions
- **Artifact storage**: Saves built packages as GitHub artifacts
- **PyPI publishing**: Automatically publishes on release
- **TestPyPI support**: Manual trigger for testing
- **Environment protection**: Can add approval requirements

## Troubleshooting

### "Workflow not found"
- Make sure `publish.yml` is in `.github/workflows/` directory
- Push the workflow to GitHub first

### "Not a trusted publisher"
- Verify all fields match exactly in PyPI configuration
- Repository owner, name, and workflow filename must be exact

### "Permission denied"
- Ensure the workflow has `id-token: write` permission
- Check GitHub environment settings if using environments

## Benefits Over Token-Based Publishing

1. **No token management**: No API tokens to create, store, or rotate
2. **More secure**: Uses short-lived OIDC tokens
3. **Auditable**: All publishes tracked in GitHub Actions
4. **Environment protection**: Can require approvals for production releases
5. **No secrets in CI**: Nothing sensitive stored in GitHub

## Next Steps

After setup:
1. Test with a release candidate version first
2. Monitor the GitHub Actions run for any issues
3. Verify package appears on PyPI after successful workflow

## Alternative: Manual Publishing

If you prefer not to use Trusted Publishing, you can still use the manual method:

```bash
PYPI_TOKEN=pypi-your-token ./publish.sh
```

But Trusted Publishing is recommended for better security and automation!