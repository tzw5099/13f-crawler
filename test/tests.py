import unittest
import os

from crawler import find_13f_report, parse_13f_doc, Holding, _file_to_holding_array, generate_report_for_ticker


examples = [
        '0000102909',  # vanguard group inc
        '0001166559',  # gates foundation
        '0001350694',  # bridgewater associates lp
        '0001103804',  # VIKING GLOBAL INVESTORS LP,
        '0001067983',  # berkeshire hathaway
        '0001483238',  # montage investments
        '0001625246',  # summit financial strategies
        '0001567755',  # private advisor group
        '0001351903',  # sii investments
        '0001492262'   # national planning corp
    ]


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.examples = examples

    def tearDown(self):
        for example in self.examples:
            os.remove('{}.tsv'.format(example))

    def test_integration(self):
        for example in self.examples:
            filename = '{}.tsv'.format(example)

            holding_array = generate_report_for_ticker(example, filename)

            self.assertIsNotNone(holding_array)
            self.assertIsInstance(holding_array, list)
            self.assertGreater(len(holding_array), 0)
            self.assertIsInstance(holding_array[0], Holding)

            loaded_holding_array = _file_to_holding_array(filename)

            self.assertEqual(len(holding_array), len(loaded_holding_array))

            for row, loaded_row in zip(holding_array, loaded_holding_array):
                self.assertListEqual(row.to_array(), loaded_row.to_array())


class WriteTsvFileTests(unittest.TestCase):
    def setUp(self):
        self.filename = '/tmp/quovo_crawler.tsv'

    def tearDown(self):
        os.remove(self.filename)

    def test_writing(self):
        for example in examples[0:4]:

            holding_array = generate_report_for_ticker(example, self.filename)

            loaded_holding_array = _file_to_holding_array(self.filename)

            self.assertEqual(len(holding_array), len(loaded_holding_array))

            for row, loaded_row in zip(holding_array, loaded_holding_array):
                self.assertListEqual(row.to_array(), loaded_row.to_array())


class ParseReportTests(unittest.TestCase):
    def setUp(self):
        self.reports = []

        for path in ('data/0000950123-16-022127.txt',
                     'data/0001104659-16-139781.txt',
                     'data/0001140361-16-085573.txt',
                     'data/0001085146-16-004730.txt',
                     'data/0001085146-16-004731.txt',
                     'data/0001085146-17-000310.txt'):
            with open(os.path.join(os.path.dirname(__file__), path), 'r') as handle:
                self.reports.append(handle.read())

    def tearDown(self):
        pass

    def test_valid_report(self):
        for report in self.reports:
            holding_array = parse_13f_doc(report)

            self.assertIsNotNone(holding_array)
            self.assertIsInstance(holding_array, list)
            self.assertGreater(len(holding_array), 0)
            self.assertIsInstance(holding_array[0], Holding)


class DownloadTests(unittest.TestCase):
    def test_valid_ticker(self):
        cik = '0000102909'  # todo find a valid ticker

        report = find_13f_report(cik)

        self.assertIsNotNone(report)
        self.assertIsInstance(report, str)
        self.assertTrue(report)  # thanks to http://stackoverflow.com/a/9573283

    def test_invalid_ticker(self):
        cik = 'asdf'

        self.assertRaises(ValueError, find_13f_report, cik)

    def test_valid_cik(self):
        cik = '0000102909'  # vanguard group inc

        report = find_13f_report(cik)

        self.assertIsNotNone(report)
        self.assertIsInstance(report, str)
        self.assertTrue(report)  # thanks to http://stackoverflow.com/a/9573283

    def test_invalid_cik(self):
        cik = 'asdf'

        self.assertRaises(ValueError, find_13f_report, cik)

if __name__ == '__main__':
    unittest.main()
