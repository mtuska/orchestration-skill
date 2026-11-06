import contextlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('usage', str(Path(__file__).resolve().parents[1] / 'scripts/usage'))
spec = importlib.util.spec_from_loader(loader.name, loader)
u = importlib.util.module_from_spec(spec)
loader.exec_module(u)


def result(status='ok', level='green'):
    return {'vendor': 'claude', 'status': status, 'level': level, 'windows': [], 'notes': []}


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name, value in [('CACHE_DIR', self.tmp.name), ('CACHE_FILE', self.tmp.name + '/last.json'),
                            ('CACHE_LOCK', self.tmp.name + '/last.lock')]:
            p = patch.object(u, name, value)
            p.start()
            self.addCleanup(p.stop)

    def call(self, *args):
        output = io.StringIO()
        with patch('sys.argv', ['usage', '--vendor', 'claude', *args]), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit):
                u.main()
        return json.loads(output.getvalue())

    def test_success_cache_and_force_refresh(self):
        with patch.object(u, 'read_claude', side_effect=[result(), result(level='red')]) as reader:
            self.call()
            cached = self.call()
            self.assertEqual(reader.call_count, 1)
            self.assertEqual(cached['cached_vendors'], ['claude'])
            self.assertIn('observed_at', cached['vendors']['claude'])
            self.call('--no-cache')
            self.assertEqual(self.call()['vendors']['claude']['level'], 'red')
            self.assertEqual(reader.call_count, 2)

    def test_failure_backoff_and_expiry(self):
        with patch.object(u, 'read_claude', return_value=result('unavailable', None)) as reader:
            self.call()
            self.call()
            self.assertEqual(reader.call_count, 1)
            cache = json.loads(Path(u.CACHE_FILE).read_text())
            cache['vendor_epochs']['claude'] -= 61
            Path(u.CACHE_FILE).write_text(json.dumps(cache))
            self.call()
            self.assertEqual(reader.call_count, 2)

    def test_crossed_reset_refreshes(self):
        now = time.time()
        old = result()
        old['windows'] = [{'resets_at': u.iso(u.dt.datetime.fromtimestamp(now - 1, u.dt.timezone.utc))}]
        Path(u.CACHE_FILE).write_text(json.dumps({'cache_version': u.CACHE_VERSION,
            'vendors': {'claude': old, 'codex': result()}, 'vendor_epochs': {'claude': now - 10, 'codex': now}}))
        with patch.object(u, 'read_claude', return_value=result()) as reader:
            self.call()
            self.assertEqual(reader.call_count, 1)
            self.call('--no-cache')
            self.assertIn('codex', json.loads(Path(u.CACHE_FILE).read_text())['vendors'])


class ClaudeScopeTests(unittest.TestCase):
    def read(self, data):
        with patch.object(u, 'claude_token', return_value=('fake', {}, None)), \
             patch.object(u.urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(data))):
            return u.read_claude(False)

    def test_scoped_stop_does_not_block_shared_capacity(self):
        r = self.read({'limits': [
            {'kind': 'weekly_all', 'percent': 10},
            {'kind': 'weekly_scoped', 'percent': 100, 'severity': 'locked', 'scope': {'model': {'display_name': 'Fable'}}}]})
        self.assertEqual(r['level'], 'green')
        self.assertEqual(r['windows'][1]['level'], 'red')
        self.assertEqual(r['windows'][1]['bucket'], 'Fable')

    def test_shared_stop_still_blocks(self):
        r = self.read({'limits': [{'kind': 'weekly_all', 'percent': 10, 'severity': 'locked'}]})
        self.assertEqual(r['level'], 'red')

    def test_legacy_scoped_limit(self):
        r = self.read({'seven_day': {'utilization': 10}, 'seven_day_opus': {'utilization': 100}})
        self.assertEqual(r['level'], 'green')
        self.assertEqual(r['windows'][1]['level'], 'red')


if __name__ == '__main__':
    unittest.main()
