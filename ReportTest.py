import unittest
import Command
import os

from Application import init_config
from Report import make_report_text, write_report_file


class ReportTest (unittest.TestCase):
    def setUp(self):
        self.standardpath = init_config()
        Command.Args().parse("")

    def test_report(self):
        report_file = os.path.expanduser("~/podcasts/report.html")
        if os.path.exists(report_file):
            os.unlink(report_file)

        basedir = self.standardpath
        r = make_report_text(basedir)
        text = r
        filename = report_file
        write_report_file(filename, text)
        self.assertTrue(self._diff_equal_true())

    def _diff_equal_true(self):
        rc = os.system('diff /tmp/report.html ~/podcasts/report.html')
        if rc == 0 :
            return True
        return False
