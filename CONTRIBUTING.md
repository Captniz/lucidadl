# Contributing to lucidadl

Thanks for your interest! Bug reports, feature ideas, and pull requests are all welcome.

> **Scope reminder.** lucidadl is a personal-use tool in the spirit of `yt-dlp`. Please
> keep contributions aligned with that purpose and with the disclaimer in the
> [README](README.md).

## Development setup

```bash
git clone https://github.com/Jude-A/lucidadl
cd lucidadl
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Unix:     source .venv/bin/activate
pip install -e ".[dev]"      # editable install + build/twine
python -m playwright install chromium  # one-time for the live browser flow
```

`pip install -e .` makes the `lucida` / `lucidadl` commands point at your working copy,
so edits take effect immediately.

## Running the tests

The self-tests are **offline** — no browser, no network — and must pass before a PR:

```bash
python selftest.py        # prints "ALL OFFLINE TESTS PASSED"
```

CI runs the same self-tests on Linux and Windows for Python 3.10–3.12, plus a packaging
check (`python -m build` + `twine check`).

For playlist changes, also run `--dry-run` with the affected public source; use `--check`
when the matching path changed. Neither command writes audio files.

### What can't be tested automatically

The live flow — solving Cloudflare, downloading, and the interactive `ui` — needs a
real desktop session and a terminal, so it can't run in CI. If your change touches that
path, please test it manually and say so in the PR (e.g. `lucida setup` then
`lucida track "Artist - Title"`, or `lucida ui`).

## Style

- Match the surrounding code: same naming, comment density, and idioms. Comments and
  user-facing strings are in English.
- Keep user-facing failures **visible** — avoid swallowing errors into silent
  degradation (see the warnings around mutagen / `state.json` / `config.json`).
- Add or update a `selftest.py` assertion when you change pure logic (parsing, matching,
  organization, dedup, transcode argument building).

## Pull requests

1. Branch off `main`.
2. Keep the change focused; update `README.md` / `CHANGELOG.md` (under `## [Unreleased]`)
   when behavior or options change.
3. Make sure `python selftest.py` passes.
4. Open the PR with a clear description of what changed and how you tested it.

## Release policy

A validated user-facing code change on `main` requires a patch release, including a
provider compatibility fix. Documentation-only status updates do not require a release.
If several validated fixes have accumulated since the latest tag, publish them together
in one patch release rather than creating one version per commit.

Before publishing:

1. Confirm the affected real-world flow works; provider fixes require one minimal live
   download in a temporary folder, followed by cleanup.
2. Complete a focused independent review and run `python selftest.py`.
3. Increment the patch version consistently in `pyproject.toml`,
   `lucidadl/__init__.py`, and the version assertion in `selftest.py`.
4. Move the relevant `CHANGELOG.md` entries out of `Unreleased`, add the release date,
   and update the comparison links.
5. Build with `.venv\Scripts\python -m build` and validate with
   `.venv\Scripts\python -m twine check dist/*`.
6. Commit the release, create an annotated `vX.Y.Z` tag, and push the commit and tag to
   GitHub and Codeberg.
7. Upload with `.venv\Scripts\python -m twine upload dist/*`; Twine reads the PyPI token
   from the local system keyring. Never print, copy into the repository, or include the
   token in command arguments.
8. Create the GitHub release from the matching changelog section. Release notes describe
   user-visible changes only and must not contain internal validation commentary.
9. Verify the new version on PyPI and GitHub before reporting success.

PyPI versions are immutable. If publication is partial or ambiguous, inspect the remote
state before retrying and never overwrite or silently reuse an already published version.
