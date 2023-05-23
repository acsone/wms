# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPartnerName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.partners = cls.partner_model.create(
            [
                {"name": "Partner 1", "ref": "abc_1234"},
                {"name": "Partner 2", "email": "p2@email.com"},
                {"name": "Partner 3", "email": "p3@email.com", "ref": "1234"},
            ]
        )

    @classmethod
    def _get_names(cls, res):
        return {x[1] for x in res}

    def assertNameSearchEqual(self, name: str, expected_result: list):
        self.assertSetEqual(
            self._get_names(self.partner_model.name_search(name)), set(expected_result)
        )

    def test_name_search(self):
        self.assertNameSearchEqual("Par", ["Partner 1", "Partner 2", "Partner 3"])
        self.assertNameSearchEqual("Partner", ["Partner 1", "Partner 2", "Partner 3"])
        self.assertNameSearchEqual("Partner 1", ["Partner 1"])
        self.assertNameSearchEqual("email.com", ["Partner 2", "Partner 3"])
        self.assertNameSearchEqual("1234", ["Partner 3"])
        self.assertNameSearchEqual("abc_1234", ["Partner 1"])
        self.assertNameSearchEqual("aBc_1234", ["Partner 1"])
        self.assertNameSearchEqual("ABC_1234", ["Partner 1"])
        self.assertNameSearchEqual("12345", [])
        self.assertNameSearchEqual("abc_", [])
        self.assertNameSearchEqual("XYZ", [])
