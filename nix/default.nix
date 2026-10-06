{
  lib,
  stdenv,
  python3Packages,
  fetchFromGitHub,
}:

python3Packages.buildPythonApplication rec {
  pname = "lucidadl";
  version = "1.4.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "Jude-A";
    repo = "lucidadl";
    rev = "v${version}";
    hash = "sha256-KpnhhgBh8YYrfcZFklX72NQR+4mRKe674hIi2btUyS0=";
  };

  nativeBuildInputs = [ python3Packages.setuptools ];

  propagatedBuildInputs = with python3Packages; [
    playwright
    click
    httpx
    pyjson5
    imageio-ffmpeg
    mutagen
    rich
    questionary
  ];

  meta = with lib; {
    description = "Lucida downloader CLI for tracks, albums and public playlists";
    homepage = "https://github.com/Jude-A/lucidadl";
    license = licenses.mit;
    mainProgram = "lucidadl";
    platforms = platforms.linux;
  };
}
