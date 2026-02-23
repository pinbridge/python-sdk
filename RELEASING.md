# Releasing `pinbridge-sdk` to PyPI

This repository is already configured to publish with trusted publishing via:

- `.github/workflows/publish.yml`

## One-time PyPI setup

1. Create the project on PyPI (or claim it): `pinbridge-sdk`.
2. In PyPI project settings, configure **Trusted Publishers**:
   - Owner: your GitHub org/user (for example: `pinbridge`)
   - Repository: `python-sdk`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. In GitHub repo settings:
   - Ensure environment `pypi` exists
   - Allow the publish workflow to deploy to that environment

No API token secret is required when trusted publishing is configured correctly.

## Release process

1. Update version in `pyproject.toml` and `src/pinbridge_sdk/__init__.py`.
2. Commit and push to `main`.
3. Create and push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The publish workflow will:

1. Lint and test
2. Build distributions
3. Verify package metadata
4. Validate tag version matches package version
5. Publish to PyPI

## Manual publish (optional)

You can trigger `publish.yml` manually with an explicit `version` input.
The workflow validates that input matches `pyproject.toml`.
