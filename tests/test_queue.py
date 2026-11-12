import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('fetch_queue', Path(__file__).parents[1] / 'scripts/fetch_queue.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class QueueTests(unittest.TestCase):
    def room(self, **overrides):
        info = dict(RName='第一診', RTime='028', WRecs='3', WDoct='測試醫師', WSect='下午', MTime='最後更新：2026-11-12 14:12:00')
        info.update(overrides)
        return module.parse_rooms({'Code': '0000', 'Infos': [info]})[0]

    def test_numbers_are_separate(self):
        result = self.room()
        self.assertEqual(result['current_number'], 28)
        self.assertEqual(result['waiting_count'], 3)
        self.assertTrue(result['source_updated_at'].endswith('+08:00'))

    def test_closed_sentinel_hides_zero_and_doctor(self):
        result = self.room(RTime='XXXX', WRecs='0')
        self.assertIsNone(result['current_number'])
        self.assertIsNone(result['waiting_count'])
        self.assertEqual(result['doctor'], '')

    def test_zero_is_valid_only_when_provided(self):
        self.assertEqual(self.room(WRecs='0')['waiting_count'], 0)
        self.assertIsNone(self.room(WRecs='----')['waiting_count'])

    def test_malformed_response_fails_closed(self):
        with self.assertRaises(ValueError):
            module.parse_rooms({'Code': '0000', 'Infos': [{'RName': '第一診'}]})
        with self.assertRaises(ValueError):
            module.parse_rooms({'Code': '9999'})


if __name__ == '__main__':
    unittest.main()
