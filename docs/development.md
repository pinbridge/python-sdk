# Development

The docs system has two parts:

- hand-written guides under `docs/`
- generated reference pages under `docs/reference/`

## Local Workflow

Install docs dependencies:

```bash
pip install -e .[docs]
```

Regenerate reference pages:

```bash
python scripts/generate_reference.py
```

Serve the docs site locally:

```bash
mkdocs serve
```

Build the site the same way CI does:

```bash
python scripts/generate_reference.py --check
mkdocs build --strict
```

## Why The Reference Is Generated

The reference pages are generated from the package layout so that:

- new resource and model modules appear in docs with less manual bookkeeping
- CI can fail if generated files drift from the current package structure
- hand-written guides stay separate from low-level API reference material
