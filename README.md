# lucidadl — Lucida downloader for tracks, albums and playlists

![lucidadl — Lucida downloader for tracks, albums and playlists](https://raw.githubusercontent.com/Jude-A/lucidadl/main/docs/assets/lucidadl-social-preview.png)

[![PyPI](https://img.shields.io/pypi/v/lucidadl.svg)](https://pypi.org/project/lucidadl/)
[![CI](https://github.com/Jude-A/lucidadl/actions/workflows/ci.yml/badge.svg)](https://github.com/Jude-A/lucidadl/actions/workflows/ci.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/lucidadl.svg)](https://pypi.org/project/lucidadl/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A small Python CLI and terminal interface for downloading music through
[lucida.to](https://lucida.to).**

Paste a track, album, text list, or public playlist. lucidadl extracts the titles, finds
matching results through Lucida, downloads them in parallel, and keeps your library
organized.

> **Official project:** [github.com/Jude-A/lucidadl](https://github.com/Jude-A/lucidadl)
>
> Install lucidadl only from [PyPI](https://pypi.org/project/lucidadl/) or this
> repository's [GitHub releases](https://github.com/Jude-A/lucidadl/releases). No
> standalone Windows `.exe` is currently distributed.

## What makes lucidadl useful?

| Input | Result |
|---|---|
| Track or album search | Qobuz, Amazon Music, or GrilledCheese through Lucida |
| Large `.txt` list | Parallel downloads with deduplication and retry |
| Public streaming playlist | Ordered import from eight supported services |
| FLAC source | Optional local MP3, AAC, Opus, Ogg, WAV, or FLAC conversion |
| Interrupted playlist | Resume with the original order and folder |

Supported public playlist sources: **Apple Music, Spotify, Deezer, YouTube/YouTube
Music, Amazon Music, TIDAL, SoundCloud, and Qobuz.** Playlist sources and download
providers are separate: playlists can originate from any supported service, while
lucidadl resolves downloads through Lucida's **Qobuz, Amazon Music, and GrilledCheese**
providers when they are available.

> **Upstream status — last checked 6 October 2026:** lucida.to remains unstable. Qobuz
> is available again through its Netherlands account, while Amazon Music resolves in
> automatic, US, UK, and Japan modes. GrilledCheese no longer exposes an account and
> currently returns no search results. This is upstream service status, not a limitation
> of playlist importing. Run `lucida setup` before retrying, and expect availability to
> change without a lucidadl release.

![lucidadl public playlist import demo](https://raw.githubusercontent.com/Jude-A/lucidadl/main/docs/assets/lucidadl-demo.gif)

> Use lucidadl only for content you are entitled to download. You are responsible for
> complying with applicable law and with the terms of the services involved. This
> project is not affiliated with lucida.to, Apple, Spotify, Deezer, YouTube, Amazon,
> TIDAL, SoundCloud, Qobuz, or any streaming service.

## Install

Python 3.10 or newer and a normal desktop session are required. Using
[pipx](https://pipx.pypa.io) keeps the application isolated and available everywhere:

```bash
pipx install lucidadl
lucida setup
lucida
```

`lucida setup` installs the matching Playwright Chromium build when needed, opens
lucida.to once for the Cloudflare check, then saves the resulting access locally.

Plain pip also works:

```bash
pip install lucidadl
lucida setup
```

Installing the package creates both `lucida` and `lucidadl`. If another application
already owns the `lucida` command, use the `lucidadl` alias for every example below.

## Installation trough Nix and Home Manager
Currently, two architectures are supported for nix: `x86_64-linux` and `aarch64-linux`.

The flake supports several installation and usage methods:
- [Direct package use](#run-or-build-it-directly)
- [Nixos Package Installation](#nixos-direct-package-installation) : **Recommended for system-wide install**
- [Nixos Module](#nixos-module)
- [Home Manager Package Installation](#home-manager-direct-package-installation)
- [Home-Manger Module](#home-manager-module)  : **Recommended for single-user install**
- [Overlay](#overlay) 

But first, **you have to import the flake** :  

Add lucidadl to the `inputs` of the flake that manages your system or home
configuration:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    lucidadl.url = "github:Captniz/lucidadl";
  };
}
```


It is recommended to use the same `nixpkgs` revision as your system. This
reuses the system's `nixpkgs` input instead of fetching a separate revision and
helps keep packages consistent. However, if lucidadl has only been tested
against a different `nixpkgs` revision, following your system's revision could
occasionally cause dependency incompatibilities.

```nix
    lucidadl = {
        url = "github:Captniz/lucidadl";
        inputs.nixpkgs.follows = "nixpkgs";
    }
```

Lucidadl can updated with:

```bash
nix flake update lucidadl
```

### Nixos direct package installation

You can install lucidadl directly in your NixOS system without importing the
NixOS module or applying the overlay. Add the package output to
`environment.systemPackages` in your system module:

```nix
{ inputs, systemSettings, ... }:
{
  environment.systemPackages = [
    inputs.lucidadl.packages.${pkgs.stdenv.hostPlatform.system}.default
  ];
}
```

Rebuild the system from the flake directory:

```bash
sudo nixos-rebuild switch --flake .#my-host
```

After the rebuild, run the installed command with:

```bash
lucidadl
```

This direct package method does not use `inputs.lucidadl.nixosModules.default`,
`inputs.lucidadl.homeModule`, or `inputs.lucidadl.overlays.default`.

### NixOS module

The NixOS module installs lucidadl system-wide and registers the overlay automatically.
Import it in the `modules` list of your `nixosSystem`:

```nix
{
  inputs.lucidadl.url = "github:Captniz/lucidadl";

  outputs = { nixpkgs, lucidadl, ... }: {
    nixosConfigurations.my-host = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        lucidadl.nixosModules.default
      ];
    };
  };
}
```

After rebuilding, the `lucidadl` command is available system-wide:

```bash
sudo nixos-rebuild switch --flake .#my-host
lucidadl
```

The module is equivalent to adding `lucidadl.overlays.default` and
`pkgs.lucidadl` to the system configuration. You do not need to add the overlay
separately when using `lucidadl.nixosModules.default`.

### Home Manager direct package installation

As with the [NixOS direct package installation](#nixos-direct-package-installation),
you can install lucidadl directly through Home Manager by adding the package to
`home.packages`. This does not enable the lucidadl-specific
`programs.lucidadl` options; use the [Home Manager module](#home-manager-module)
if you want those options.
```nix
{ inputs, pkgs, ... }:
{
  home.packages = [
    inputs.lucidadl.packages.${pkgs.stdenv.hostPlatform.system}.default
  ];
}
```

For standalone Home Manager, rebuild from the flake directory:

```sh
home-manager switch --flake .#my-user
```

For Home Manager integrated with NixOS, use:

```sh
sudo nixos-rebuild switch --flake .#my-host
```
After the rebuild, run:
```sh
lucidadl
```

### Home Manager module

The Home Manager module builds the package and installs lucidadl into the user's profile.

For standalone Home Manager, pass `inputs` (_and any system settings used by the
flake_) through `extraSpecialArgs`, then import the module in `home.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
    lucidadl.url = "github:Captniz/lucidadl";
  };

  outputs = { home-manager, nixpkgs, ... }@inputs: {
    homeConfigurations.my-user = home-manager.lib.homeManagerConfiguration {
      pkgs = import nixpkgs { system = "x86_64-linux"; };
      extraSpecialArgs = { inherit inputs; };
      modules = [ ./home.nix ];
    };
  };
}
```

```nix
# home.nix
{ inputs, ... }:
{
  imports = [ inputs.lucidadl.homeManagerModules.default ];
  programs.lucidadl.enable = true;
}
```

The shorter alias `inputs.lucidadl.homeModule` is also available:

```nix
imports = [ inputs.lucidadl.homeModule ];
```

For NixOS-integrated Home Manager, add
`home-manager.nixosModules.home-manager` to the NixOS modules and import the
lucidadl module in the user's Home Manager module:

```nix
{
  home-manager.users.my-user = {
    imports = [ inputs.lucidadl.homeManagerModules.default ];
    programs.lucidadl.enable = true;
  };
}
```

The module also accepts an explicit package when you need to pin or replace the
default:

```nix
{
  programs.lucidadl = {
    enable = true;
    package = inputs.lucidadl.packages.${pkgs.stdenv.hostPlatform.system}.default;
  };
}
```


### Run or build it directly

No module or overlay is required for **one-off** use:

```bash
nix run github:Captniz/lucidadl
nix build github:Captniz/lucidadl
```


### Overlay

The optional overlay adds lucidadl to the nixpkgs package set as `pkgs.lucidadl`:


```nix
{
  nixpkgs.overlays = [ inputs.lucidadl.overlays.default ];
  environment.systemPackages = [ pkgs.lucidadl ];
}
```

It provides a shorter alternative to the direct package references used in the
[NixOS direct package installation](#nixos-direct-package-installation) and
[Home Manager direct package installation](#home-manager-direct-package-installation)
sections. The overlay is therefore optional.

Applying the overlay is not needed for `nix run`, direct package references, the
NixOS module, or the Home Manager module.

## Three ways to download

### 1. A track or album

```bash
lucida track "Daft Punk - Around the World"
lucida album "Daft Punk - Discovery"
```

A direct Qobuz or Amazon URL can be used in place of the search text. Albums are
expanded and downloaded track by track so the available parallelism is preserved.

Use interactive search when you want to choose the result yourself:

```bash
lucida search "Discovery Daft Punk"
```

### 2. Many tracks or albums from a text file

```bash
lucida tracks --file "D:/music-lists/tracks.txt"
lucida albums --file "D:/music-lists/albums.txt"
```

The format is deliberately simple: one search or direct URL per line. Blank lines and
comments beginning with `#` are ignored.

```text
# Road-trip additions
Daft Punk - Around the World
The Chemical Brothers - Galvanize
https://play.qobuz.com/track/24107150
```

The source file is never edited. Already downloaded items are skipped unless `--force`
is used. When `--file` is omitted, the plural commands use `./inputs/tracks.txt` or
`./inputs/albums.txt`; ready-to-copy examples are included in the repository.

### 3. A public streaming playlist

```bash
lucida playlist "https://music.apple.com/.../pl.xxxxxxxx"
lucida playlist "https://open.spotify.com/playlist/xxxxxxxx"
lucida playlist "https://www.deezer.com/playlist/xxxxxxxx"
lucida playlist "https://music.youtube.com/playlist?list=xxxxxxxx"
lucida playlist "https://music.amazon.com/playlists/xxxxxxxx"
lucida playlist "https://tidal.com/playlist/xxxxxxxx"
lucida playlist "https://soundcloud.com/user/sets/xxxxxxxx"
lucida playlist "https://open.qobuz.com/playlist/xxxxxxxx"
```

lucidadl detects the service from the URL, reads its public track list, resolves each
title through lucida.to, and stores the result under `Playlists/<playlist name>/`. An
`.m3u8` file is written beside the tracks so players and devices recognize the folder as
an actual playlist.

Preview the extraction without downloading anything:

```bash
lucida playlist "https://music.apple.com/.../pl.xxxxxxxx" --dry-run
```

To verify what lucidadl will select on Qobuz or Amazon before starting a large download:

```bash
lucida playlist "https://music.apple.com/.../pl.xxxxxxxx" --check
```

The extracted list is saved in lucidadl's application-data folder. If a title is
ambiguous or unavailable, edit that file (or remove the line), then download the reviewed
version while preserving playlist order:

```bash
lucida playlist-file "C:/path/to/playlist.txt" --name "My playlist"
```

If a playlist is interrupted, `lucida retry` resumes it with its original folder,
settings, and track numbers. Existing files are skipped, and the `.m3u8` is rebuilt when
the run finishes. Repeating the same song at two different positions is supported.

Only public playlists are read: lucidadl does not connect to or modify a streaming
account. Deezer, Amazon Music, and Qobuz are read directly; short Spotify and TIDAL
lists use their fast public players. Apple Music, YouTube, SoundCloud, and longer
Spotify/TIDAL lists automatically use a headless browser to load every public position.
The import stops with a clear error instead of accepting a known partial list.

## Interactive menu

Run `lucida` without arguments (or `lucida ui`):

```text
╭────────────────── lucidadl ──────────────────╮
│ 3 concurrent downloads · qobuz · original    │
│ Music: ~/Downloads/music                     │
│ Access: prepared                             │
╰──────────────────────────────────────────────╯

► What do you want to do?
  ⬇   Download music
  🎶  Playlists — streaming link or an edited list
  📄  Download from a .txt file
  ⚙   Settings
  🧰  Help, access and diagnostics
  🚪  Quit
```

The menu remembers its download count, source service, conversion settings, and music
folder. Each run ends with a readable summary and offers failed items for retry from the
main menu.

## Output and formats

Music is saved to `~/Downloads/music` by default, independently of the directory from
which lucidadl is launched:

```text
music/
├── Artists/
│   └── Artist/
│       └── Album/
└── Playlists/
    └── Playlist name/
        ├── 01 - Track.flac
        └── Playlist name.m3u8
```

Change the main folder permanently or for one run:

```bash
lucida config --music "D:/Music"
lucida track "Artist - Title" --out "E:/Temporary music"
```

For local conversion, lucidadl downloads the best source first and invokes the bundled
ffmpeg executable:

```bash
lucida album "Artist - Album" --to mp3 --bitrate 320k --jobs 8
```

If conversion fails, the source audio is kept and the item is reported as failed rather
than silently counted as a success.

Useful download options:

| Option | Purpose |
|---|---|
| `-j, --jobs N` | Parallel downloads, from 1 to 100 (default: 3) |
| `-s, --service` | Search service: `qobuz`, `amazon`, or `grilledcheese` |
| `--to FORMAT` | Local conversion to MP3, AAC/M4A, Opus, Ogg, FLAC, or WAV |
| `--bitrate RATE` | Conversion bitrate such as `320k` or `192k` |
| `--keep-original` | Keep the source FLAC after conversion |
| `--flat` | Place files under `Music/` instead of organizing from tags |
| `--force` | Ignore download history and fetch the item again |
| `--hidden` | Move a necessary Cloudflare browser window off-screen |

Run `lucida <command> --help` for the complete options of a command.

## Access, failures, and diagnostics

Cloudflare access is prepared once in a real Chromium window. Downloads then use a
lightweight HTTP client. If the saved access expires, lucidadl briefly opens the browser
again and refreshes it.

```bash
lucida doctor          # quick local check; never opens a browser
lucida doctor --live   # browser and lucida.to connectivity check
lucida setup           # install/repair Chromium and refresh access
lucida retry           # retry failures or resume an interrupted playlist
lucida cleanup         # prune stale state and old partial downloads
```

Failed tracks and albums retain their original type; playlist failures also retain their
folder and original position. Automated and scheduled commands return a non-zero status
while work remains unresolved. The latest details are stored in `run.log`; `lucida
config` prints its exact location along with the extracted playlist and recovery data.

Common fixes:

- No confident automatic match: use `lucida search` and choose the result manually.
- Cloudflare or browser failure: run `lucida setup`, then `lucida doctor --live`.
- Unexpected output folder: run `lucida config` and check `LUCIDADL_MUSIC`.
- Another program uses the `lucida` command: call this application with `lucidadl`.

## Scheduling a batch

Once access has been prepared, a `.txt` batch can run unattended while its cached access
remains valid. A Windows Scheduled Task helper is included:

```powershell
.\schedule.ps1 -Mode tracks -Time 21:30 -WorkingDir "D:\music-lists"
```

The scheduled task uses `inputs/tracks.txt` or `inputs/albums.txt` under its working
directory. A logged-in desktop session is still required if Cloudflare access must be
renewed.

## Application data

The browser profile, access data, configuration, deduplication state, last log,
failed-item list, and playlist recovery data are stored outside the repository:

- Windows: `%LOCALAPPDATA%\lucidadl`
- Linux: `~/.local/share/lucidadl`
- macOS: `~/Library/Application Support/lucidadl`

Advanced overrides are available through `LUCIDADL_HOME` and `LUCIDADL_MUSIC`.

## Development

```bash
git clone https://github.com/Jude-A/lucidadl
cd lucidadl
python -m venv .venv
pip install -e ".[dev]"
python selftest.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for platform-specific setup and validation.
Release changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## Credits

lucidadl takes inspiration from
[lucida-flow](https://github.com/ryanlong1004/lucida-flow) and
[lucida-downloader](https://github.com/jelni/lucida-downloader).

## License

[MIT](LICENSE)
