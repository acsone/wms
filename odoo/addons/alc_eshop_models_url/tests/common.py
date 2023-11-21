# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestUrlCase(TransactionCase):
    def assertUrlForLang(self, record, lang, url_key):
        self.assertEqual(record._get_main_url("global", lang).key, url_key)
