import contextlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
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
        installed = patch.object(u.shutil, 'which', side_effect=lambda command: '/fake/bin/' + command)
        installed.start()
        self.addCleanup(installed.stop)
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

    def test_missing_cli_bypasses_cache_and_recovers_after_install(self):
        with patch.object(u, 'read_claude', return_value=result()) as reader:
            self.call()
            with patch.object(u.shutil, 'which', return_value=None):
                missing = self.call()
                self.assertEqual(missing['vendors']['claude']['status'], 'not_installed')
                self.assertEqual(missing['advice']['prefer'], 'neither')
                self.assertEqual(reader.call_count, 1)
            self.call()
            self.assertEqual(reader.call_count, 2)

    def test_missing_vendors_are_excluded_from_advice(self):
        vendors = {v: {'status': 'not_installed'} for v in u.VENDORS}
        vendors['cursor'] = {'status': 'ok', 'level': 'green'}
        advice = u.advise(vendors)
        self.assertEqual(advice['prefer'], 'cursor')
        self.assertEqual(advice['codex'], 'not_installed')
        vendors['cursor'] = {'status': 'not_installed'}
        self.assertEqual(u.advise(vendors)['prefer'], 'neither')

    def test_vendor_reads_overlap_and_cache_skips_them(self):
        barrier = threading.Barrier(4, timeout=3)
        def reader(*args, **kwargs):
            barrier.wait()
            return result()
        with patch.object(u, 'read_claude', side_effect=reader) as claude, \
             patch.object(u, 'read_codex', side_effect=reader), \
             patch.object(u, 'read_gemini', side_effect=reader), \
             patch.object(u, 'read_cursor', side_effect=reader):
            snap = self.call('--vendor', 'all')
            self.assertTrue(all(d['status'] == 'ok' for d in snap['vendors'].values()))
            self.assertEqual(list(snap['vendors']), list(u.VENDORS))
            cached = self.call('--vendor', 'all')
            self.assertEqual(claude.call_count, 1)
            self.assertEqual(cached['cached_vendors'], list(u.VENDORS))

    def test_failed_reader_preserves_other_results(self):
        with patch.object(u, 'read_claude', side_effect=RuntimeError('probe failure')), \
             patch.object(u, 'read_codex', return_value=result()), \
             patch.object(u, 'read_gemini', return_value=result()), \
             patch.object(u, 'read_cursor', return_value=result()):
            snap = self.call('--vendor', 'all')
            self.assertEqual(snap['vendors']['claude']['status'], 'unavailable')
            self.assertTrue(all(snap['vendors'][v]['status'] == 'ok' for v in ('codex', 'gemini', 'cursor')))

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

    def test_reserve_changes_routing_and_preserves_actual(self):
        reset = u.now_utc() + u.dt.timedelta(days=3.5)
        r = self.read({'limits': [{'kind': 'weekly_all', 'percent': 55,
                                  'resets_at': u.iso(reset)}]})
        u.apply_policy({'claude': r}, {'claude': {'reserve_percent': 10}})
        self.assertEqual(r['windows'][0]['actual_percent'], 55)
        self.assertEqual(r['windows'][0]['percent'], 65)
        self.assertEqual(r['binding']['headroom_percent'], 35)
        self.assertEqual(r['level'], 'yellow')
        report = u.text_report({'generated_at': 'test', 'vendors': {'claude': r},
                                'advice': u.advise({'claude': r})})
        self.assertIn('actual 55.0%', report)
        self.assertIn('+10pp reserve', report)

    def test_reserve_bounds_unknown_and_pace(self):
        now = u.now_utc()
        for vendor in u.VENDORS:
            for actual, expected in [(0, 10), (95, 100), (None, None), (50, 60)]:
                with patch.object(u, 'now_utc', return_value=now):
                    raw = u.window('weekly', 'weekly', actual, now + u.dt.timedelta(hours=5), 36000)
                    r = {'status': 'ok', 'windows': [raw]}
                    u.apply_policy({vendor: r}, {vendor: {'reserve_percent': 10}})
                    self.assertEqual(r['windows'][0]['percent'], expected)
                    self.assertEqual(raw['percent'], actual)
                    u.apply_policy({vendor: r}, {vendor: {'reserve_percent': 10}})
                    self.assertEqual(r['windows'][0]['percent'], expected)
                    u.apply_policy({vendor: r}, {})
                    self.assertEqual(r['windows'][0]['percent'], actual)

    def test_scoped_stop_does_not_block_shared_capacity(self):
        r = self.read({'limits': [
            {'kind': 'weekly_all', 'percent': 10},
            {'kind': 'weekly_scoped', 'percent': 100, 'severity': 'locked', 'scope': {'model': {'display_name': 'Fable'}}}]})
        self.assertIsNone(r['level'])
        self.assertEqual(r['windows'][1]['level'], 'red')
        self.assertEqual(r['windows'][1]['bucket'], 'Fable')

    def test_shared_stop_still_blocks(self):
        r = self.read({'limits': [{'kind': 'weekly_all', 'percent': 10, 'severity': 'locked'}]})
        self.assertEqual(r['level'], 'red')

    def test_legacy_scoped_limit(self):
        r = self.read({'seven_day': {'utilization': 10}, 'seven_day_opus': {'utilization': 100}})
        self.assertIsNone(r['level'])
        self.assertEqual(r['windows'][1]['level'], 'red')


class PolicyTests(unittest.TestCase):
    def test_pace_override_and_preference_preserve_measurement(self):
        d = {'status': 'ok', 'level': 'red', 'windows': [u.window('weekly', 'weekly', 80, u.now_utc() + u.dt.timedelta(hours=5), 36000)], 'notes': []}
        vendors = {'codex': d, 'cursor': {'status': 'ok', 'level': 'green'},
                   'gemini': {'status': 'ok', 'level': 'green'},
                   'claude': {'status': 'ok', 'level': 'red'}}
        u.apply_policy(vendors, {'codex': {'ignore_pace': True, 'prefer': True}})
        self.assertEqual(d['level'], 'red')
        self.assertEqual(d['routing_level'], 'green')
        self.assertEqual(set(u.advise(vendors)['prefer'].split('+')), {'codex', 'cursor', 'gemini'})
        self.assertEqual(u.advise(vendors)['policy_preferred'], ['codex'])
        u.apply_policy(vendors, {})
        self.assertEqual(d['routing_level'], 'red')

    def test_credits_require_permission_balance_and_service_availability(self):
        for allowed, balance, service, expected in [(True, 20, True, 'green'),
                (False, 20, True, 'red'), (True, 0, True, 'red'), (True, 20, False, 'red'),
                (True, 20, None, 'red')]:
            d = {'status': 'ok', 'level': 'red', 'windows': [{'percent': 100}],
                 'ordinary_usage_allowed': service, 'credits': {'has_credits': True, 'balance': balance}}
            u.apply_policy({'codex': d}, {'codex': {'ignore_pace': True, 'allow_credits': allowed}})
            self.assertEqual(d['routing_level'], expected)

    def test_blocks_stale_and_unknown_not_overridden(self):
        for extra in [{'hard_stop': True}, {'status': 'stale'}, {'spend_control_reached': True}]:
            d = {'status': 'ok', 'level': 'red', 'windows': [u.window('weekly', 'weekly', 50, u.now_utc() + u.dt.timedelta(hours=7.5), 36000)], **extra}
            u.apply_policy({'codex': d}, {'codex': {'ignore_pace': True}})
            self.assertEqual(d['routing_level'], 'red')
        d = {'status': 'unavailable', 'windows': []}
        u.apply_policy({'codex': d}, {'codex': {'ignore_pace': True}})
        self.assertIsNone(d['routing_level'])

    def test_policy_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'policy.json'
            for data in [{'codex': {'prefer': 'false'}}, {'typo': {}}, {'codex': {'typo': True}},
                         {'codex': {'reserve_percent': -1}}, {'codex': {'reserve_percent': 101}},
                         {'codex': {'reserve_percent': True}}]:
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    u.load_policy(path)


class PaceTests(unittest.TestCase):
    def test_levels_follow_pace_not_absolute_usage(self):
        for used, ratio, expected in [(95, 1.0, 'green'), (15, 1.5, 'red'),
                                      (13, 1.3, 'yellow'), (60, 1.2, 'green'),
                                      (100, 1.0, 'red'), (50, None, None)]:
            with self.subTest(used=used, ratio=ratio):
                self.assertEqual(u.level_for([{'percent': used, 'pace_ratio': ratio}]), expected)
        self.assertEqual(u.level_for([], hard_stop=True), 'red')
        self.assertIsNone(u.level_for([]))

    def test_binding_selects_worst_pace(self):
        windows = [dict(id='weekly', label='weekly', percent=95, pace_ratio=1.0),
                   dict(id='short', label='short', percent=15, pace_ratio=1.5)]
        self.assertEqual(u.binding(windows)['id'], 'short')
        self.assertEqual(u.level_for(windows), 'red')


class GrokBillingTests(unittest.TestCase):
    def test_shared_pool_reset_and_pace(self):
        payload = {'config': {'creditUsagePercent': 51,
            'currentPeriod': {'type': 'USAGE_PERIOD_TYPE_WEEKLY',
                              'start': '2026-11-02T19:19:57Z', 'end': '2026-11-09T19:19:57Z'},
            'productUsage': [{'product': 'Cursor', 'usagePercent': 34},
                             {'product': 'GrokBuild', 'usagePercent': 11}]}}
        with patch.object(u, 'grok_billing', return_value=payload), \
             patch.object(u, 'now_utc', return_value=u.parse_ts('2026-11-06T07:19:57Z')):
            r = u.read_cursor()
        self.assertEqual(r['status'], 'ok')
        self.assertEqual(r['binding']['percent'], 51)
        self.assertEqual(r['windows'][0]['window_hours'], 168)
        self.assertEqual(r['windows'][0]['expected_percent_now'], 50)
        self.assertNotIn('products', r)

    def test_missing_or_invalid_usage_stays_unknown(self):
        for value in [None, '51', True, float('nan'), float('inf'), -1]:
            with self.subTest(value=value), patch.object(u, 'grok_billing',
                    return_value={'config': {'creditUsagePercent': value}}):
                r = u.read_cursor()
                self.assertEqual(r['status'], 'unavailable')
                self.assertNotIn('level', r)

    def test_auth_retry_and_no_refresh(self):
        error = u.urllib.error.HTTPError(u.GROK_BILLING_URL, 401, 'Unauthorized', {}, None)
        with patch.object(u, 'grok_billing', side_effect=[error, {'config': {'creditUsagePercent': 0}}]) as fetch, \
             patch.object(u, 'refresh_grok_token') as refresh:
            self.assertEqual(u.read_cursor()['status'], 'ok')
            self.assertEqual(fetch.call_count, 2)
            refresh.assert_called_once()
        with patch.object(u, 'grok_billing', side_effect=error), \
             patch.object(u, 'refresh_grok_token') as refresh:
            self.assertEqual(u.read_cursor(False)['status'], 'unavailable')
            refresh.assert_not_called()

    def test_service_failure_is_unknown_without_refresh(self):
        error = u.urllib.error.HTTPError(u.GROK_BILLING_URL, 503, 'Unavailable', {}, None)
        with patch.object(u, 'grok_billing', side_effect=error), \
             patch.object(u, 'refresh_grok_token') as refresh:
            self.assertEqual(u.read_cursor()['status'], 'unavailable')
            refresh.assert_not_called()


if __name__ == '__main__':
    unittest.main()
