# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas import Address


class TestSchemaAddress(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        ExtendableMixin.init_extendable_registry()
        cls.country_state = cls.env["res.country.state"].create(
            {"name": "Brussels", "code": "BRU", "country_id": cls.env.ref("base.be").id}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "street": "Rue de la Loi",
                "city": "Brussels",
                "zip": "1000",
                "country_id": cls.env.ref("base.be").id,
                "email": "test@test.com",
                "phone": "0123456789",
                "mobile": "0123456789",
                "vat": "BE0477472701",
                "is_company": True,
                "ref": "123456",
                "opt_out": True,
                "vet_depot_number": "123456",
                "vet_subscription_number": "123456",
                "state_id": cls.country_state.id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.reset_extendable_registry()
        super().tearDownClass()

    def test_schema_from_record(self):
        model = Address.from_res_partner(self.partner)
        self.assertEqual(model.name, "Test Partner")
        self.assertEqual(model.street, "Rue de la Loi")
        self.assertEqual(model.city, "Brussels")
        self.assertEqual(model.zip, "1000")
        self.assertEqual(model.country.id, self.env.ref("base.be").id)
        self.assertEqual(model.email, "test@test.com")
        self.assertEqual(model.phone, "0123456789")
        self.assertEqual(model.mobile, "0123456789")
        self.assertEqual(model.vat, "BE0477472701")
        self.assertEqual(model.is_company, True)
        self.assertEqual(model.ref, "123456")
        self.assertEqual(model.opt_out, True)
        self.assertEqual(model.opt_in, False)
        self.assertEqual(model.vet_depot_number, "123456")
        self.assertEqual(model.vet_subscription_number, "123456")
        self.assertEqual(model.state.id, self.country_state.id)
