# GitHub-managed releases

The workflows are disabled until their repository variables are enabled. Merging this
setup does not publish a package. The migration starts from the published **v1.4.0**;
Release Please's first grouped patch is **v1.4.1**. Do not bump versions manually.

## One-time setup

### 1. Release bot

Create a private GitHub App at <https://github.com/settings/apps/new>:

- Choose an available name such as `lucidadl-release-bot` and set the homepage to this repo.
- Disable the webhook; no callback URL or OAuth flow is needed.
- Repository permissions: **Contents**, **Pull requests**, **Issues**: read and write.
  Keep other permissions unset (Metadata read is automatic).
- Allow installation only on your account; install it on **lucidadl only**.
- Generate a private key. In the repository's **Settings → Secrets and variables → Actions**,
  add its PEM contents as secret `RELEASE_APP_PRIVATE_KEY` and the App's **Client ID**
  as variable `RELEASE_APP_CLIENT_ID`.

The App creates short-lived tokens. Its PRs and release events trigger the normal CI
and publishing workflows; using the default `GITHUB_TOKEN` for these writes would not.
Do not paste the private key into an issue, chat, commit or workflow file.

Enable squash merging in the repository's **Settings → General → Pull Requests** and
use the PR title for the squash commit. Release-worthy titles use `fix:`, `feat:`,
`perf:` or `revert:`. A PR check verifies that package changes have one of these titles.
Use `chore(nix): ...` for Nix-only changes and `ci: ...` for workflow changes.
For a small repository, review the green CI manually before merging; no ruleset is required
by this setup. If you already use a ruleset, its checks must pass for the release PR too.

### 2. PyPI without an API token

Create a GitHub environment named **`pypi`** in repository **Settings → Environments**.
Allow the `v*` tags and `main` branch to deploy (main is used for manual recovery).
No environment reviewer is needed: merging the release PR is the approval.

In the **existing** PyPI project, open
<https://pypi.org/manage/project/lucidadl/settings/publishing/> and add a GitHub publisher:

| Field | Exact value |
| --- | --- |
| Owner | `Jude-A` |
| Repository | `lucidadl` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

This is an existing-project publisher, not a pending publisher for a new project.
The workflow exchanges GitHub's OIDC identity for a short-lived PyPI credential.
No `PYPI_TOKEN` secret is needed.

### 3. Codeberg mirror

Use the existing Codeberg repository. Generate a **dedicated** SSH key on your machine
(no passphrase, since Actions has no interactive prompt), for example:

```sh
ssh-keygen -t ed25519 -C lucidadl-github-mirror -f lucidadl-codeberg
```

Use a fresh filename; do not overwrite an existing key. Add the `.pub` file in the
Codeberg repository's **Settings → Deploy Keys**, with write access. Add the private
file's contents as GitHub Actions secret `CODEBERG_SSH_KEY`.

Set these GitHub repository variables:

| Variable | Value |
| --- | --- |
| `CODEBERG_REPOSITORY` | The actual SSH URL, `git@codeberg.org:OWNER/REPO.git` |
| `CODEBERG_MIRROR_ENABLED` | `true`, after configuring the above |

The workflow verifies Codeberg's ED25519 host key against the fingerprint in
[Codeberg's official documentation](https://docs.codeberg.org/security/ssh-fingerprint/).
A host-key change stops the mirror; verify the new fingerprint before updating the pin.
The mirror never force-pushes or deletes refs. If Codeberg has diverged, reconcile the
commits before retrying; never solve it by adding `--force`.

### 4. Activate and make the first release

1. Disable any existing publishing automation to avoid duplicate releases.
2. Merge the automation PR with passing CI.
3. After configuring the App and PyPI publisher, set repository variable
   `RELEASE_AUTOMATION_ENABLED` to **`true`**.
4. Under **Actions → Prepare release → Run workflow**, select `main`.
5. Review the generated **1.4.1** PR: Amazon regional fallback, GrilledCheese,
   current Qobuz/Amazon regions and safe playlist track-number normalization.
   Check that all three source versions and the manifest agree, the notes are complete,
   and CI is green. Merge when ready to publish.
6. Watch **Publish release** and **Mirror to Codeberg**. Run the mirror manually once
   after enabling it if the relevant push happened before activation.

Thereafter, normal merges update one grouped release PR. Merging that PR publishes it.

## Recovery

A GitHub Release appears before PyPI publication completes. A release is fully published
only when **Publish release** verifies both PyPI files. Read the failed job before retrying.

Run **Actions → Publish release → Run workflow** from **main**, entering the existing tag
(e.g. `v1.4.1`). The workflow checks the tag's ancestry and source versions, reuses the
saved GitHub release distributions, compares PyPI SHA-256 checksums, and uploads only
missing files. A mismatching or yanked remote file is a hard failure, not `skip-existing`.

If uploading GitHub assets itself stopped after one file, download the `distributions`
artifact from the original build run (retained for 90 days), restore **only the missing
file** to the same GitHub Release, then retry. Never rebuild or replace the file already
published. If the original artifact is unavailable, stop and investigate; don't guess.
Transient PyPI indexing delays may make final verification fail: recheck/retry the same
tag rather than inventing another version.

If PyPI succeeded and only the Nix job failed, rerun that job. Nix updates use the published
tag's unpacked source hash and open a separate PR; they do not publish another Python
version. Until the Nix packaging PR is merged, this job reports a skip. Afterwards,
rerun publication for the latest release to create its Nix update PR. Older releases
cannot downgrade the Nix package. Nix CI builds and checks command entry points; it
does not verify a full NixOS desktop installation or a live provider download.

A failed Codeberg mirror can be rerun independently. It pushes the current `main` and all
`v*` tags atomically, preserving history and remote-only refs.

References: [Release Please](https://github.com/googleapis/release-please-action),
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).
