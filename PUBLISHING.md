# Publishing BosBase Python SDK to PyPI

This guide explains how to publish the `bosbase` Python SDK to PyPI using hatch, so users can install it with `pip install bosbase`.

## Prerequisites

1. **Install hatch**: 
   ```bash
   pip install hatch
   ```

2. **PyPI Account**: You need an account on [PyPI](https://pypi.org) (and optionally [TestPyPI](https://test.pypi.org) for testing)

3. **API Token**: Create an API token on PyPI:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with "Upload packages" scope
   - Save the token securely (format: `pypi-...`)

## Publishing Steps

### 1. Update Version

Before publishing, update the version in `pyproject.toml`:

```toml
[project]
version = "0.1.0"  # Update this to the new version
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backward compatible
- **PATCH** (0.1.1): Bug fixes, backward compatible

### 2. Build the Package

Build the distribution files:

```bash
cd python-sdk
hatch build
```

This creates:
- `dist/bosbase-<version>-py3-none-any.whl` (wheel)
- `dist/bosbase-<version>.tar.gz` (source distribution)

### 3. Test the Build (Optional but Recommended)

Test the build locally:

```bash
# Install the built package in a virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate
pip install dist/bosbase-<version>-py3-none-any.whl

# Test that it works
python -c "from bosbase import BosBase; print('Import successful!')"
```

### 4. Test on TestPyPI (Recommended)

Before publishing to production PyPI, test on TestPyPI:

```bash
# Publish to TestPyPI
hatch publish --repo testpypi

# Or manually with twine
pip install twine
twine upload --repository testpypi dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your TestPyPI API token (different from PyPI token)

Test installation from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ bosbase
```

### 5. Publish to PyPI

Once tested, publish to production PyPI:

```bash
hatch publish
```

Or manually with twine:
```bash
twine upload dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your PyPI API token

### 6. Verify Publication

After publishing, verify the package is available:

```bash
pip install bosbase
python -c "import bosbase; print(bosbase.__version__)"
```

Check on PyPI: https://pypi.org/project/bosbase/

## Using Environment Variables (Recommended)

Instead of entering credentials interactively, use environment variables:

```bash
# For PyPI
export HATCH_INDEX_USER=__token__
export HATCH_INDEX_AUTH=your-pypi-api-token

# Then publish
hatch publish
```

Or with twine:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-pypi-api-token
twine upload dist/*
```

## Automated Publishing with GitHub Actions

You can automate publishing using GitHub Actions. Create `.github/workflows/publish-python-sdk.yml`:

```yaml
name: Publish Python SDK

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install hatch
        run: pip install hatch
      
      - name: Build package
        working-directory: python-sdk
        run: hatch build
      
      - name: Publish to PyPI
        working-directory: python-sdk
        run: hatch publish
        env:
          HATCH_INDEX_USER: __token__
          HATCH_INDEX_AUTH: ${{ secrets.PYPI_API_TOKEN }}
```

Add `PYPI_API_TOKEN` to your GitHub repository secrets.

## Troubleshooting

### "Package already exists"
- The version number is already published. Increment the version in `pyproject.toml`.

### "Invalid credentials"
- Verify your API token is correct
- Ensure you're using `__token__` as the username
- Check token hasn't expired

### "File already exists"
- Delete old files in `dist/` or use `hatch clean` before building

### Build errors
- Ensure all dependencies are listed in `pyproject.toml`
- Check that `src/bosbase/__init__.py` exists and is correct
- Verify Python version compatibility

## Post-Publication Checklist

- [ ] Package installs correctly: `pip install bosbase`
- [ ] Package page is live on PyPI
- [ ] README displays correctly on PyPI
- [ ] Version number is correct
- [ ] All dependencies are listed
- [ ] Documentation links work

## Additional Resources

- [Hatch Documentation](https://hatch.pypa.io/)
- [PyPI Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)


