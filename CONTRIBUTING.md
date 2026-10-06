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
   when behavior or options change. Keep these notes limited to user-visible changes.
3. Make sure `python selftest.py` passes.
4. Open the PR with a clear description of what changed and how you tested it.
5. Use `fix:`, `feat:`, `perf:` or `revert:` for package changes; use `docs:`, `ci:`,
   `test:`, `build:` or `chore:` for changes that do not need a Python release.
   Squash-merge using that title so Release Please can classify the change.
   Direct commits to `main` must follow the same convention.

## Release policy

A validated user-facing code change on `main` requires a patch release, including a
provider compatibility fix. Group accumulated changes into one release. Documentation,
status, CI, tests and Nix packaging changes alone do not require a Python release.

GitHub Actions owns release preparation and publication; no local AI session, scheduler,
Windows keyring or PyPI API token is required. See [release setup and recovery](docs/releasing.md).

1. Before merging a provider fix, confirm one minimal live download in a temporary
   folder, clean it up, and record the result in the PR. Complete a focused independent
   review. Offline CI does not establish that a live provider works.
2. Release Please maintains one release PR, updating `pyproject.toml`,
   `lucidadl/__init__.py`, the version assertion in `selftest.py`, its version manifest,
   and `CHANGELOG.md`. The default bump is patch; a deliberate minor/major change needs
   an explicit `Release-As: X.Y.Z` commit footer and maintainer review.
3. Review the release PR's notes and passing tests, then merge it. This is the publication
   approval: Actions creates the tag and GitHub Release, builds and checks the package,
   publishes through PyPI Trusted Publishing, and verifies the remote file checksums.
4. Nix follows a **published** release via a separate version/hash PR and the Nix CI.
   The Codeberg mirror pushes `main` and version tags without force-pushing.

Maintain a complete set of user-facing notes under `Unreleased` while fixes accumulate.
If that section contains notes, they replace the generated commit-title notes in the
release PR and GitHub Release. Otherwise, Release Please's generated notes are used.

PyPI versions are immutable. A partial or ambiguous publication must be inspected and
resumed using the existing tag and original distribution files. Never overwrite a tag,
replace existing release assets, or silently reuse a published version for different code.
