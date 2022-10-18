# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.keycloak.tests.common import TestKeycloak


class TestKeycloakUpdateFlow(TestKeycloak):
    def test_update_one_attribute_update_all_attributes(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        full_payload = keycloak_user._get_payload()
        job_counter = self.job_counter()

        # when
        self.partner.partner_type = "shareholder"
        # then
        job = job_counter.search_created()
        payload = keycloak_user.keycloak_backend_id._get_user_payload(*job.args)
        self.assertEqual(list(payload.keys()), ["attributes"])
        self.assertEqual(
            list(payload["attributes"].keys()), list(full_payload["attributes"].keys())
        )

    def test_update_partner_type(self):
        expected_roles = {
            "shareholder",
            "guest",
            "price-yourcompany",
            "non_alcyonnaire",
        }
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        job_counter = self.job_counter()

        # when
        self.partner.partner_type = "shareholder"
        # then
        job = job_counter.search_created()
        self.assertEqual(job.args, [keycloak_user, ["partner_type"]])
        payload = keycloak_user.keycloak_backend_id._get_user_payload(*job.args)
        self.assertEqual(list(payload.keys()), ["attributes"])
        roles = set(payload["attributes"]["shopinvader-vt-roles"].split(","))
        self.assertEqual(roles, expected_roles)

    def test_update_pricelist(self):
        pricelist = self.env["product.pricelist"].create({"name": "pridamis"})
        expected_roles = {"misc", "guest", "price-pridamis", "non_alcyonnaire"}
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        job_counter = self.job_counter()

        # when
        self.partner.property_product_pricelist = pricelist
        # then
        jobs = job_counter.search_created()
        job = jobs.filtered(lambda j: j.model_name == "keycloak.backend")
        self.assertEqual(job.args, [keycloak_user, ["property_product_pricelist"]])
        payload = keycloak_user.keycloak_backend_id._get_user_payload(*job.args)
        self.assertEqual(list(payload.keys()), ["attributes"])
        roles = set(payload["attributes"]["shopinvader-vt-roles"].split(","))
        self.assertEqual(roles, expected_roles)

    def test_update_veterinary_groups(self):
        veterinary_group = self.env["veterinary.group"].create({"name": "VTG"})
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        job_counter = self.job_counter()

        # when
        self.partner.write({"veterinary_group_ids": [(6, 0, veterinary_group.ids)]})
        # then
        jobs = job_counter.search_created()
        job = jobs.filtered(lambda j: j.model_name == "keycloak.backend")
        self.assertEqual(job.args, [keycloak_user, ["veterinary_group_ids"]])
        payload = keycloak_user.keycloak_backend_id._get_user_payload(*job.args)
        self.assertEqual(list(payload.keys()), ["attributes"])
        vt_groups = payload["attributes"]["vt-groups"]
        expected_vt_groups = veterinary_group.ids
        self.assertEqual(vt_groups, expected_vt_groups)

    def test_veterinary_group_create(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        job_counter = self.job_counter()

        # on veterinary group creation, if we specify partners these should be exported
        self.env["veterinary.group"].create(
            {"name": "VTG", "partner_ids": [(6, 0, keycloak_user.partner_id.ids)]}
        )
        jobs = job_counter.search_created()
        job = jobs.filtered(lambda j: j.model_name == "keycloak.backend")
        self.assertEqual(job.args, [keycloak_user, ["veterinary_group_ids"]])

    def test_veterinary_group_update_add_partner(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        veterinary_group = self.env["veterinary.group"].create({"name": "VTG"})
        job_counter = self.job_counter()

        # on veterinary group update if we add a partner it should be exported
        veterinary_group.write({"partner_ids": [(6, 0, keycloak_user.partner_id.ids)]})

        jobs = job_counter.search_created()
        job = jobs.filtered(lambda j: j.model_name == "keycloak.backend")
        self.assertEqual(job.args, [keycloak_user, ["veterinary_group_ids"]])

    def test_veterinary_group_update_remove_partner(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        veterinary_group = self.env["veterinary.group"].create(
            {"name": "VTG", "partner_ids": [(6, 0, keycloak_user.partner_id.ids)]}
        )
        # delete queue job created by the group creation
        self.env["queue.job"].search([]).unlink()
        job_counter = self.job_counter()

        # on veterinary group update if we add a partner it should be exported
        veterinary_group.write({"partner_ids": [(6, 0, [])]})

        jobs = job_counter.search_created()
        job = jobs.filtered(lambda j: j.model_name == "keycloak.backend")
        self.assertEqual(job.args, [keycloak_user, ["veterinary_group_ids"]])

    def test_update_write_lang(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        job_counter = self.job_counter()

        # when
        self.partner.lang = "fr_BE"

        # then
        job = job_counter.search_created()
        self.assertEqual(job.args, [keycloak_user, ["lang"]])
        payload = keycloak_user.keycloak_backend_id._get_user_payload(*job.args)
        self.assertEqual(payload["attributes"]["locale"], "fr_BE")

    def test_update_write_everything(self):
        pricelist = self.env["product.pricelist"].create({"name": "pridamis"})
        expected_attributes = {
            "locale": "fr_BE",
            "ref": "abc123",
            "can_order": False,
            "help_with_fee": True,
        }
        expected_roles = {"shareholder", "guest", "price-pridamis", "non_alcyonnaire"}
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        job_counter = self.job_counter()

        # when
        vals = {
            "property_product_pricelist": pricelist.id,
            "partner_type": "shareholder",
            "lang": "fr_BE",
            "ref": "abc123",
            "eshop_ordering_allowed": False,
            "help_with_fee": True,
        }
        self.partner.write(vals)

        # then
        jobs = job_counter.search_created()
        job = jobs.filtered(lambda j: j.model_name == "keycloak.backend")
        self.assertEqual(set(job.args[1]), set(vals))
        payload = keycloak_user.keycloak_backend_id._get_user_payload(*job.args)
        self.assertEqual(list(payload.keys()), ["attributes"])
        roles_str = payload["attributes"].pop("shopinvader-vt-roles")
        for k in expected_attributes:
            self.assertEqual(payload["attributes"][k], expected_attributes[k])
        self.assertEqual(set(roles_str.split(",")), expected_roles)
