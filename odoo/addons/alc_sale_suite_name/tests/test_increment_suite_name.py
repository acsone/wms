# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest

from ..utils import increment_suite_name


class TestIncrementSuiteName(unittest.TestCase):
    def test_increment(self):
        self.assertEqual("1", increment_suite_name(False))
        self.assertEqual("1", increment_suite_name(None))
        self.assertEqual("1", increment_suite_name(" "))
        self.assertEqual("2", increment_suite_name("1"))
        self.assertEqual("2", increment_suite_name("1 "))
        self.assertEqual("2", increment_suite_name(" 1 "))
        self.assertEqual("1 a1", increment_suite_name("1 a"))
        self.assertEqual("sn100", increment_suite_name("sn99"))
        self.assertEqual("sn99.100", increment_suite_name("sn99.99"))
        self.assertEqual("sn99.99 100", increment_suite_name("sn99.99 99"))
        self.assertEqual("Compl\xc3\xa9ment100", increment_suite_name(u"Complément99"))
        self.assertEqual("Compl\xc3\xa9ment100", increment_suite_name("Complément99"))
        self.assertEqual("Compl\xc3\xa9ment99!1", increment_suite_name("Complément99!"))
