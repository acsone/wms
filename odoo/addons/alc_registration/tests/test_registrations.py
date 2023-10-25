# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestRegistrationMixin


class TestRegistration(TestRegistrationMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.model = cls.env["alc.registration"]

    def test_creation_flow(self):
        vals = self._get_registration_vals()
        vals.pop("company_name")

        registration = self.model.create(vals)

        self.assertEqual(registration.state, "pending")
        self.assertEqual(registration.clientele, "equine")

        partner = registration.create_partners()

        self.assertEqual(registration.state, "accepted")
        self.assertEqual(registration.name, partner.name)
        self.assertEqual(registration.partner_id, partner)
        category_equine = self.env.ref("alc_partner_category.equins")
        self.assertEqual(partner.category_id, category_equine)

        # the partner already exist, do nothing
        no_partner = registration.create_partners()

        self.assertFalse(no_partner)
        self.assertEqual(registration.state, "accepted")

    def test_multiple_clientele(self):
        vals = self._get_registration_vals()
        vals["clientele"] = "livestock,pet"
        registration = self.model.create(vals)
        partner = registration.create_partners()

        category_petit = self.env.ref("alc_partner_category.petits_animaux")
        category_grand = self.env.ref("alc_partner_category.grands_animaux")
        self.assertEqual(partner.category_id, category_petit + category_grand)

    def test_clientele_no_category(self):
        vals = self._get_registration_vals()
        vals["clientele"] = "nobody"
        registration = self.model.create(vals)
        partner = registration.create_partners()

        self.assertFalse(partner.category_id)

    def test_creation_with_company_name(self):
        # given
        vals = self._get_registration_vals()
        registration = self.model.create(vals)
        # when
        partner = registration.create_partners()
        # then: we moved around the name/company_name
        self.assertEqual(registration.company_name, partner.name)
        self.assertEqual(registration.name, partner.suite)

    def test_archive(self):
        vals = self._get_registration_vals()
        registration = self.model.create(vals)

        registration.action_archive()
        self.assertEqual(registration.state, "rejected")

        registration.action_reset_to_pending()
        self.assertEqual(registration.state, "pending")

    def test_similar_partner(self):
        vals = self._get_registration_vals()
        registration = self.model.create(vals)
        partner_name = self.env["res.partner"].create({"name": vals["name"]})

        # the newly created partner does not trigger the recompute
        registration._compute_similar_partner_ids()
        # do not assert equality: other test data partners may be similar
        self.assertTrue(partner_name in registration.similar_partner_ids)

        partner_vat = self.env["res.partner"].create({"name": "V", "vat": vals["vat"]})
        registration._compute_similar_partner_ids()
        self.assertTrue(partner_name in registration.similar_partner_ids)
        self.assertTrue(partner_vat in registration.similar_partner_ids)
