import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / 'lucidadl-1.4.1.tar.gz'
        self.file.write_bytes(b'original artifact')
        self.files = {self.file.name: self.file}
        self.remote = {'filename': self.file.name, 'digests': {
            'sha256': hashlib.sha256(self.file.read_bytes()).hexdigest()}}

    def test_tag_is_strict(self):
        self.assertEqual(release.version_from_tag('v1.4.1'), '1.4.1')
        for tag in ['main', 'v1.4.1rc1', 'v1.4.1\n', '--help', 'v1.4.1/../../']:
            with self.assertRaises(ValueError):
                release.version_from_tag(tag)

    def test_complete_upload_is_not_repeated(self):
        self.assertEqual(release.missing_distributions(self.files, [self.remote]), [])

    def test_partial_upload_only_stages_missing_file(self):
        wheel = self.root / 'lucidadl-1.4.1-py3-none-any.whl'
        wheel.write_bytes(b'wheel')
        files = {**self.files, wheel.name: wheel}
        self.assertEqual(release.missing_distributions(files, [self.remote]), [wheel.name])

    def test_remote_mismatch_unexpected_or_yanked_stops(self):
        for change in [{'digests': {'sha256': 'wrong'}}, {'filename': 'other.whl'}, {'yanked': True}]:
            with self.assertRaises(ValueError):
                release.missing_distributions(self.files, [{**self.remote, **change}])

    def test_only_pypi_404_means_unpublished(self):
        for status in [404, 403, 500]:
            with patch('urllib.request.urlopen', side_effect=HTTPError('url', status, '', {}, None)):
                if status == 404:
                    self.assertEqual(release.pypi_files('1.4.1'), [])
                else:
                    with self.assertRaises(HTTPError):
                        release.pypi_files('1.4.1')

    def test_changelog_carries_curated_notes_and_is_idempotent(self):
        content = ('# Changelog\n\n## [1.4.1](compare) (2026-10-07)\n\n### Fixed\n* generated\n\n'
                   '## [Unreleased]\n\n### Fixed\n- Preserve downloads.\n\n'
                   '## [1.4.0] - 2026-09-03\n\n- Old changes.\n\n'
                   '[Unreleased]: old\n')
        result, notes = release.finalize_changelog(content, '1.4.1')
        self.assertIn('Preserve downloads.', notes)
        self.assertNotIn('generated', notes)
        self.assertNotIn('Old changes.', notes)
        self.assertLess(result.index('## [Unreleased]'), result.index('## [1.4.1]'))
        self.assertIn('/compare/v1.4.1...HEAD', result)
        self.assertEqual(release.finalize_changelog(result, '1.4.1'), (result, notes))

    def test_nix_updates_both_fields_but_never_downgrades(self):
        path = self.root / 'default.nix'
        old = 'sha256-' + 'A' * 43 + '='
        new = 'sha256-' + 'B' * 43 + '='
        path.write_text('version = "1.4.0";\nrev = "v${version}";\nhash = "' + old + '";\n')
        release.update_nix('1.4.1', new, path)
        self.assertIn('version = "1.4.1"', path.read_text())
        self.assertIn(new, path.read_text())
        release.update_nix('1.4.0', old, path)
        self.assertIn(new, path.read_text())
        path.write_text('version = "1.4.0"; rev = "v${version}";')
        with self.assertRaises(ValueError):
            release.update_nix('1.4.1', new, path)

    def test_repository_versions_agree(self):
        release.source_version()


if __name__ == '__main__':
    unittest.main()
