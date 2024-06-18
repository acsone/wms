# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_keycloak.tests.common import TestKeycloak
from odoo.addons.queue_job.tests.common import trap_jobs


class TestKeycloakUpdateFlow(TestKeycloak):
    def test_update_one_attribute_update_all_attributes(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        full_payload = keycloak_user._get_payload()

        # when
        with trap_jobs() as trap:
            self.partner.partner_type = "shareholder"
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["partner_type"]),
            )
        # then
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["partner_type"]
        )
        self.assertEqual(list(payload.keys()), ["attributes"])
        self.assertEqual(
            list(payload["attributes"].keys()), list(full_payload["attributes"].keys())
        )

    def test_update_partner_type(self):
        expected_roles = {
            "shareholder",
            "guest",
            self.partner.property_product_pricelist.role_name,
            "non_alcyonnaire",
        }
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)

        with trap_jobs() as trap:
            self.partner.partner_type = "shareholder"
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["partner_type"]),
            )
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["partner_type"]
        )
        self.assertEqual(list(payload.keys()), ["attributes"])
        roles = set(payload["attributes"]["shopinvader-vt-roles"].split(","))
        self.assertEqual(roles, expected_roles)

    def test_update_pricelist(self):
        pricelist = self.env["product.pricelist"].create({"name": "pridamis"})
        expected_roles = {"misc", "guest", pricelist.role_name, "non_alcyonnaire"}
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)

        with trap_jobs() as trap:
            self.partner.property_product_pricelist = pricelist
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["property_product_pricelist"]),
            )
        # then
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["property_product_pricelist"]
        )
        self.assertEqual(list(payload.keys()), ["attributes"])
        roles = set(payload["attributes"]["shopinvader-vt-roles"].split(","))
        self.assertEqual(roles, expected_roles)

    def test_update_partner_is_alcyonnaire_under_contract(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        alcyonnaire_group = self.env["veterinary.group"].create(
            {"name": "Alcyonnaire", "is_alcyonnaire": True}
        )
        with trap_jobs() as trap:
            self.partner.veterinary_group_ids = alcyonnaire_group
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["veterinary_group_ids"]),
            )

        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["veterinary_group_ids"]
        )
        roles = set(payload["attributes"]["shopinvader-vt-roles"].split(","))
        self.assertNotIn("is_alcyonnaire_under_contract", roles)
        self.assertIn("is_alcyonnaire", roles)

        # when a partner becomes an alcyonnaire under contract
        with trap_jobs() as trap:
            self.partner.date_start_contract_alcyonnaire = "2019-01-01"
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["date_start_contract_alcyonnaire"]),
            )
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["date_start_contract_alcyonnaire"]
        )
        roles = set(payload["attributes"]["shopinvader-vt-roles"].split(","))
        self.assertIn("is_alcyonnaire_under_contract", roles)
        self.assertNotIn("is_alcyonnaire", roles)

        # when a partner is no more an alcyonnaire under contract
        with trap_jobs() as trap:
            self.partner.date_end_contract_alcyonnaire = "2020-01-01"
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["date_end_contract_alcyonnaire"]),
            )
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["date_end_contract_alcyonnaire"]
        )
        roles = set(payload["attributes"]["shopinvader-vt-roles"].split(","))
        self.assertNotIn("is_alcyonnaire_under_contract", roles)
        self.assertIn("is_alcyonnaire", roles)

    def test_update_veterinary_groups(self):
        veterinary_group = self.env["veterinary.group"].create({"name": "VTG"})
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)

        with trap_jobs() as trap:
            self.partner.veterinary_group_ids = veterinary_group
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["veterinary_group_ids"]),
            )
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["veterinary_group_ids"]
        )
        self.assertEqual(list(payload.keys()), ["attributes"])
        vt_groups = payload["attributes"]["vt-groups"]
        expected_vt_groups = veterinary_group.ids
        self.assertEqual(vt_groups, expected_vt_groups)

    def test_veterinary_group_create(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)

        # on veterinary group creation, if we specify partners these should be exported
        with trap_jobs() as trap:
            self.env["veterinary.group"].create(
                {"name": "VTG", "partner_ids": [(6, 0, keycloak_user.partner_id.ids)]}
            )
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["veterinary_group_ids"]),
            )

    def test_veterinary_group_update_add_partner(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        veterinary_group = self.env["veterinary.group"].create({"name": "VTG"})

        # on veterinary group update if we add a partner it should be exported
        with trap_jobs() as trap:
            veterinary_group.partner_ids = keycloak_user.partner_id
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["veterinary_group_ids"]),
            )

    def test_veterinary_group_update_remove_partner(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        veterinary_group = self.env["veterinary.group"].create(
            {"name": "VTG", "partner_ids": [(6, 0, keycloak_user.partner_id.ids)]}
        )
        # delete queue job created by the group creation

        # on veterinary group update if we add a partner it should be exported
        with trap_jobs() as trap:
            veterinary_group.partner_ids = False
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["veterinary_group_ids"]),
            )

    def test_update_write_lang(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)

        # when
        with trap_jobs() as trap:
            self.partner.lang = "en_US"
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["lang"]),
            )
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["lang"]
        )
        self.assertEqual(payload["attributes"]["locale"], "en_US")

    def test_update_write_everything(self):
        pricelist = self.env["product.pricelist"].create({"name": "pridamis"})
        expected_attributes = {
            "locale": "en_US",
            "ref": "abc123",
            "can_order": False,
            "help_with_fee": True,
        }
        expected_roles = {
            "shareholder",
            "guest",
            pricelist.role_name,
            "non_alcyonnaire",
        }
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)

        # when
        vals = {
            "property_product_pricelist": pricelist.id,
            "partner_type": "shareholder",
            "lang": "en_US",
            "ref": "abc123",
            "eshop_ordering_allowed": False,
            "help_with_fee": True,
        }
        with trap_jobs() as trap:
            self.partner.write(vals)
            job = next(
                filter(lambda j: j.model_name == "keycloak.backend", trap.enqueued_jobs)
            )
            self.assertSetEqual(
                set(job.args[1]),
                {
                    "lang",
                    "help_with_fee",
                    "partner_type",
                    "ref",
                    "eshop_ordering_allowed",
                    "property_product_pricelist",
                },
            )
        # then
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user,
            [
                "lang",
                "help_with_fee",
                "partner_type",
                "ref",
                "eshop_ordering_allowed",
                "property_product_pricelist",
            ],
        )
        self.assertEqual(list(payload.keys()), ["attributes"])
        roles_str = payload["attributes"].pop("shopinvader-vt-roles")
        for k, v in expected_attributes.items():
            self.assertEqual(payload["attributes"][k], v)
        self.assertEqual(set(roles_str.split(",")), expected_roles)
