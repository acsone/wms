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
                {"name": "abc_1234", "ref": "456"},
            ]
        )

    @classmethod
    def _get_names(cls, res):
        return {x[1] for x in res}

    def assertNameSearchEqual(self, name: str, expected_result: list):
        self.assertSetEqual(
            self._get_names(self.partner_model.name_search(name)), set(expected_result)
        )

    def assertNameSearchFirstElement(self, name: str, expected_first_element: str):
        self.assertEqual(
            self.partner_model.name_search(name)[0][1], expected_first_element
        )

    def test_name_search(self):
        """
        Cases:

            1- search by a substring of the name
                > return all partners with a name contains the substring
            2- search by the exact name
                > return the partner that matches the name
            3- search by a substring of the email
                > return all partners with an email contains the substring
            4- search by the exact ref which a substring of the name
                > return all partner with the exact ref or a name contains the ref
                > first results are partners that match the exact ref
            5- search by a substring that don't match any partner
                > Nothing to return
        """
        # case 1
        self.assertNameSearchEqual(
            name="Par", expected_result=["Partner 1", "Partner 2", "Partner 3"]
        )
        self.assertNameSearchEqual(
            name="Partner", expected_result=["Partner 1", "Partner 2", "Partner 3"]
        )
        self.assertNameSearchEqual(name="abc_", expected_result=["abc_1234"])
        # case 2
        self.assertNameSearchEqual(name="Partner 1", expected_result=["Partner 1"])
        # case 3
        self.assertNameSearchEqual(
            name="email.com", expected_result=["Partner 2", "Partner 3"]
        )
        # case 4
        self.assertNameSearchEqual(
            name="1234", expected_result=["abc_1234", "Partner 3"]
        )
        self.assertNameSearchFirstElement(
            name="1234", expected_first_element="Partner 3"
        )
        self.assertNameSearchEqual(
            name="abc_1234", expected_result=["abc_1234", "Partner 1"]
        )
        self.assertNameSearchFirstElement(
            name="abc_1234", expected_first_element="Partner 1"
        )
        self.assertNameSearchEqual(
            name="aBc_1234", expected_result=["abc_1234", "Partner 1"]
        )
        self.assertNameSearchFirstElement(
            name="aBc_1234", expected_first_element="Partner 1"
        )
        self.assertNameSearchEqual(
            name="ABC_1234", expected_result=["abc_1234", "Partner 1"]
        )
        self.assertNameSearchFirstElement(
            name="ABC_1234", expected_first_element="Partner 1"
        )
        # case 5
        self.assertNameSearchEqual(name="12345", expected_result=[])
        self.assertNameSearchEqual(name="XYZ", expected_result=[])
