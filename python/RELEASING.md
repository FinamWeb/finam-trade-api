# Releasing the Python SDK

This document is for maintainers cutting a release of `finam-sdk` on PyPI.
For SDK usage, see [README.md](README.md).

## One-time setup

The publish workflow uses [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/)
via OIDC — no API tokens are stored in the repo. This must be configured
once per index (PyPI and TestPyPI), per project.

### 1. Create the PyPI projects

The `finam-sdk` name is currently unclaimed. Create the project on each
index by doing a manual first upload (with an account-scoped API token),
**or** configure a "pending publisher" before any release exists.

The pending-publisher route is preferred — it lets the GitHub Action create
the project on first publish, without ever using an API token:

- PyPI: <https://pypi.org/manage/account/publishing/> → *Add a pending publisher*
- TestPyPI: <https://test.pypi.org/manage/account/publishing/> → *Add a pending publisher*

Use these values for both indexes:

| Field | Value |
| --- | --- |
| PyPI project name | `finam-sdk` |
| Owner | `FinamWeb` |
| Repository name | `finam-trade-api` |
| Workflow filename | `publish_python.yml` |
| Environment | `pypi` (real) / `testpypi` (test) |

### 2. Configure the GitHub environments

In the GitHub repo, go to **Settings → Environments** and create two
environments: `pypi` and `testpypi`.

For `pypi`, strongly recommended:

- **Required reviewers** — at least one maintainer must approve each
  publish run. This is the safety net against accidental releases (PyPI
  versions are immutable).
- **Deployment branches** — restrict to tag pushes only.

For `testpypi`, no required reviewers — prereleases should publish
without ceremony.

## Cutting a release

### Pre-release / dry-run (publishes to TestPyPI)

1. Bump version in [pyproject.toml](pyproject.toml) to a PEP 440 prerelease,
   e.g. `0.2.0rc1`.
2. Update [CHANGELOG.md](CHANGELOG.md): move items from `[Unreleased]` to a
   new `[0.2.0rc1] — YYYY-MM-DD` section. Update the link references at the
   bottom.
3. Commit, push, merge to `main`.
4. Create a GitHub Release with tag `v0.2.0rc1`, target `main`. Mark it
   *Pre-release*.
5. The `publish_python.yml` workflow detects the prerelease marker in the
   tag and pushes to TestPyPI.
6. Verify in a clean venv:
   ```sh
   python -m venv /tmp/finam-verify && source /tmp/finam-verify/bin/activate
   pip install -i https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     finam-sdk==0.2.0rc1
   python -c "from finam_trade_api import FinamClient; print('ok')"
   ```
   The `--extra-index-url` is needed because TestPyPI doesn't mirror
   runtime dependencies (grpcio, protobuf, …).

### Final release (publishes to real PyPI)

1. Bump version in [pyproject.toml](pyproject.toml) to the final number,
   e.g. `0.2.0`.
2. Update [CHANGELOG.md](CHANGELOG.md) similarly — final section, link
   references.
3. Commit, push, merge to `main`.
4. Create a GitHub Release with tag `v0.2.0`, target `main`. **Do not**
   mark it pre-release.
5. The workflow detects a final tag, requires environment approval (per
   the `pypi` environment config), and on approval pushes to PyPI.
6. Verify:
   ```sh
   python -m venv /tmp/finam-verify && source /tmp/finam-verify/bin/activate
   pip install finam-sdk==0.2.0
   python -c "from finam_trade_api import FinamClient; print('ok')"
   ```

## Version policy

`finam-sdk` follows [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)** — breaking changes to the Python public API
  (`FinamClient`, `AsyncFinamClient`, the per-service shim modules, the
  exception hierarchy). A breaking proto change upstream (Finam removes
  or renames an RPC) is also a major bump for this SDK.
- **Minor (0.X.0)** — new RPCs, new shim re-exports, new optional
  parameters. Should not break existing callers.
- **Patch (0.0.X)** — bug fixes, internal refactors, regenerated stubs
  with no surface change.

Until `1.0.0`, minor versions may include small breaking changes if
clearly noted in the changelog.

## Troubleshooting

### "Tag does not match pyproject.toml version"

The `build` job validates that the release tag (`v0.2.0`) and the
`pyproject.toml` version (`0.2.0`) agree. If you tagged before bumping
the version: delete the release + tag, bump the version, push, and
recreate the release.

### Trusted publisher rejected the upload

Check that the GitHub environment name matches the one configured on PyPI
exactly (case-sensitive: `pypi`, `testpypi`). Then check the workflow
filename — PyPI expects `publish_python.yml` literally.

### `twine check` fails in CI

Run locally to see the exact issue:

```sh
cd python
python -m build
twine check --strict dist/*
```

Most common: README contains a markdown construct PyPI can't render
(rare with GitHub-flavored markdown), or a classifier was removed/renamed.

## What ships in the wheel

The build pipeline (see [.github/workflows/python_test.yml](../.github/workflows/python_test.yml))
verifies on every PR that the wheel contains:

- `finam_trade_api/` — hand-written modules + per-service shim re-exports.
- `finam_trade_api/proto/` — generated gRPC stubs (`.py` + `.pyi`).
- `finam_trade_api/py.typed` — typing marker.
- `LICENSE`.

Notably *not* shipped: `tests/`, `examples/`, `scripts/`, `.venv/`,
`__pycache__/`.
