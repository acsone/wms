# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import veterinary_groups_router


class TestVeterinaryGroupService(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = veterinary_groups_router
        cls.VeterinaryGroup = cls.env["veterinary.group"]
        cls.group_a = cls.VeterinaryGroup.create(
            {
                "name": "group_a",
                "display_color": "#123212",
                "sequence": 10,
                "is_alcyonnaire": True,
            }
        )
        vals_partner = {"name": "P", "veterinary_group_ids": [(6, 0, cls.group_a.ids)]}
        cls.partner = cls.env["res.partner"].create(vals_partner)
        vals_group_b = {
            "name": "group_b",
            "display_color": "#123212",
            "sequence": 5,
            "is_alcyonnaire": False,
        }
        cls.group_b = cls.VeterinaryGroup.create(vals_group_b)
        cls.partner_no_vt_group = cls.env["res.partner"].create({"name": "P2"})

    def test_group_search(self):
        with self._create_test_client(partner=self.partner_no_vt_group) as test_client:
            response = test_client.get("/veterinary_groups")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

    def test_search(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/veterinary_groups")
            self.assertEqual(response.status_code, 200)
            res = response.json()
            self.assertEqual(1, res["size"])
            self.assertEqual(self.group_a.id, res["data"][0]["id"])
            self.assertEqual("group_a", res["data"][0]["name"])
            self.assertEqual(10, res["data"][0]["sequence"])
            self.assertEqual(True, res["data"][0]["is_alcyonnaire"])
            self.assertEqual("#123212", res["data"][0]["color"])

        self.partner.write({"veterinary_group_ids": [(4, self.group_b.id)]})
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/veterinary_groups")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(2, response.json()["size"])
