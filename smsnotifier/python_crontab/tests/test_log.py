#!/usr/bin/python
#
# Copyright (C) 2013 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Test the cron log extention with a test syslog example data file.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, '../')

import unittest
from crontab import CronTab
from cronlog import CronLog, LogReader
try:
    from test import test_support
except ImportError:
    from test import support as test_support

INITAL_TAB = """
* * * * * userscript &> /dev/null
* * * * * rootscript &> /dev/null
* * * * * shadowscript &> /dev/null
"""

ROOT_PIDS = ['16592', '16574', '16552', '16522', '16514', '16489']
SHAD_PIDS = ['16551', '16497']
USER_PIDS = ['16591', '16588', '16573', '16569', '16554', '16539', '16523',\
            '16519','16513','16496','16490']

ROOT_DATES = [
    datetime(2013, 4, 4, 21, 34, 1),
    datetime(2013, 4, 4, 21, 32, 1),
    datetime(2013, 4, 4, 21, 30, 1),
    datetime(2013, 4, 4, 21, 28, 1),
    datetime(2013, 4, 4, 21, 26, 1),
    datetime(2013, 4, 4, 21, 24, 1),
  ]
SHAD_DATES = [
    datetime(2013, 4, 4, 21, 30, 1),
    datetime(2013, 4, 4, 21, 25, 1),
  ]
USER_DATES = [
    datetime(2013, 4, 4, 21, 34, 1),
    datetime(2013, 4, 4, 21, 33, 2),
    datetime(2013, 4, 4, 21, 32, 1),
    datetime(2013, 4, 4, 21, 31, 1),
    datetime(2013, 4, 4, 21, 30, 1),
    datetime(2013, 4, 4, 21, 29, 1),
    datetime(2013, 4, 4, 21, 28, 1),
    datetime(2013, 4, 4, 21, 27, 1),
    datetime(2013, 4, 4, 21, 26, 1),
    datetime(2013, 4, 4, 21, 25, 1),
    datetime(2013, 4, 4, 21, 24, 1),
  ]
READ_LINE = [ 'The End', 'Sickem', '2', '9', 'First Line' ]

class BasicTestCase(unittest.TestCase):
    """Test basic functionality of crontab."""
    def setUp(self):
        self.crontab = CronTab(tab=INITAL_TAB, log='data/test.log')

    def test_00_logreader(self):
        """Log Reader"""
        lines = READ_LINE[:]
        reader = LogReader('data/basic.log')
        for line in reader:
            self.assertEqual(line.strip(), lines.pop(0))

    def test_01_cronreader(self):
        """Cron Log Lines"""
        lines = list(self.crontab.log.readlines())
        self.assertEqual(len(lines), 32)
        self.assertEqual(lines[0][1], "Apr  4 21:34:01 servername CRON[16592]: (root) CMD (rootscript &> /dev/null)")
        self.assertEqual(lines[15][1], "Apr  4 21:28:31 servername NOTCRON: that these are ignored")
        self.assertEqual(lines[-1][1], "Apr  4 21:24:01 servername CRON[16490]: (user) CMD (userscript &> /dev/null)")

    def test_02_cronlog(self):
        """Cron Log Items"""
        entries = list(CronLog('data/test.log'))
        self.assertEqual(len(entries), 19)
        self.assertEqual(entries[0]['pid'], "16592")
        self.assertEqual(entries[3]['pid'], "16574")
        self.assertEqual(entries[-1]['pid'], "16490")

    def test_03_crontab(self):
        """Cron Tab Items"""
        entries = list(self.crontab.log)
        self.assertEqual(len(entries), 8)
        self.assertEqual(entries[0]['pid'], "16592")
        self.assertEqual(entries[3]['pid'], "16551")
        self.assertEqual(entries[-1]['pid'], "16489")

    def test_04_root(self):
        """Cron Job Items"""
        pids, dates = ROOT_PIDS[:], ROOT_DATES[:]
        job = self.crontab.find_command('rootscript')[0]
        for log in job.log:
            self.assertEqual(log['pid'], pids.pop(0))
            self.assertEqual(log['date'], dates.pop(0))
        self.assertEqual(pids, [])

    def tst_05_shadow(self):
        """Seperate Job Items"""
        pids, dates = SHAD_PIDS[:], SHAD_DATES[:]
        job = self.crontab.find_command('shadowscript')[0]
        for log in job.log:
            self.assertEqual(log['pid'], pids.pop(0))
            self.assertEqual(log['date'], dates.pop(0))
        self.assertEqual(pids, [])

    def tst_06_user(self):
        """Seperate User Crontab"""
        pids, dates = USER_PIDS[:], User_DATES[:]
        self.crontab.user = 'user'
        job = self.crontab.find_command('userscript')[0]
        for log in job.log:
            self.assertEqual(log['pid'], pids.pop(0))
            self.assertEqual(log['date'], dates.pop(0))
        self.assertEqual(pids, [])

if __name__ == '__main__':
    test_support.run_unittest(
       BasicTestCase,
    )
