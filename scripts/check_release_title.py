"""Ensure squash-merge titles describe whether a PR needs a Python release."""
import os
import re
import subprocess


def check(title, paths):
    code = any(p.startswith('lucidadl/') or p == 'pyproject.toml' for p in paths)
    # Release Please changes the package version itself, with this exact title.
    if re.fullmatch(r'chore\(main\): release \d+\.\d+\.\d+', title):
        return
    kind = re.match(r'([a-z]+)(?:\([^\n)]+\))?!?: .+', title)
    if not kind:
        raise ValueError('Use a conventional PR title, e.g. fix: correct playlist order or docs: update README')
    release_kind = kind[1] in {'fix', 'feat', 'perf', 'revert'}
    if code != release_kind:
        raise ValueError('Package changes need fix:/feat:/perf:/revert:; docs, CI, tests and Nix-only changes need docs:/ci:/test:/chore:/build:')


if __name__ == '__main__':
    paths = subprocess.check_output(['git', 'diff', '--name-only', os.environ['BASE_SHA'], os.environ['HEAD_SHA']], text=True).splitlines()
    check(os.environ['PR_TITLE'], paths)
