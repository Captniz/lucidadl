# Releases

GitHub Actions prepares and publishes releases through Release Please and PyPI Trusted
Publishing. The release workflows require repository configuration and remain inactive
until enabled.

## Preparing a release

Release Please groups changes on `main` into a release PR. It updates `pyproject.toml`,
`lucidadl/__init__.py`, the version assertion in `selftest.py`, the release manifest and
`CHANGELOG.md`. Do not edit version numbers independently.

Keep complete user-facing notes under `Unreleased`. These become the release notes;
when the section is empty, Release Please uses the relevant commit titles instead.
See [CONTRIBUTING.md](../CONTRIBUTING.md#release-policy) for commit conventions and
validation requirements.

## Publishing

Review the release PR's notes and passing CI before merging. Once merged:

1. **Prepare release** creates the version tag and GitHub Release.
2. **Publish release** tests the tagged source, builds the wheel and source distribution,
   saves the files as GitHub Release assets, publishes to PyPI and verifies their checksums.
3. When Nix packaging is present, a separate PR updates its version and source hash.
   The Nix CI must pass before that PR is merged.

**Mirror to Codeberg** runs independently on pushes to `main` and version tags. It
preserves history and never force-pushes or deletes remote refs.

A GitHub Release appears before PyPI publication completes. Publication is complete
only when **Publish release** verifies both PyPI files.

## Recovering a failed publication

Inspect the failed job before retrying. Run **Publish release** manually from `main`
with the existing tag. It reuses the saved distribution files, checks PyPI's SHA-256
checksums and uploads only missing files. Mismatching or yanked files stop the workflow.
Never overwrite a tag, replace published files or reuse a version for different code.

If saving the GitHub assets stopped after one file, retrieve the `distributions`
artifact from the original build run and restore only the missing file to the same
GitHub Release. Artifacts are retained for 90 days. If the original files are unavailable,
investigate before proceeding; do not rebuild a substitute for an existing publication.

A transient PyPI indexing delay may fail final verification. Recheck the same tag
rather than creating another version.

If only the Nix update failed, rerun that job. It updates packaging for the published
release without creating a new Python version. If packaging was added after publication,
rerun the latest release to create its Nix update PR.

A failed Codeberg mirror can be rerun separately. If its history has diverged, reconcile
the commits before retrying. A host-key mismatch requires checking Codeberg's published
fingerprint before updating the workflow's pin.
