import unittest
from scripts.check_release_title import check


class TitleTests(unittest.TestCase):
    def test_code_and_release_titles(self):
        check('fix: repair provider', ['lucidadl/api.py', 'README.md'])
        check('chore(main): release 1.4.1', ['pyproject.toml'])
        with self.assertRaises(ValueError):
            check('docs: repair provider', ['lucidadl/api.py'])

    def test_non_package_changes_do_not_trigger_a_release(self):
        for files in [['README.md'], ['flake.lock', 'nix/default.nix'], ['.github/workflows/ci.yml']]:
            check('chore: update configuration', files)
            with self.assertRaises(ValueError):
                check('fix: update configuration', files)
