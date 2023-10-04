# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestClassifiedCase(TransactionCase):
    @classmethod
    def create_classified(cls, partner=False, state=False, **params):
        vals = {
            "partner_id": (partner or cls.partner_1).id,
            "state_id": (state or cls.state_wlg).id,
            "name": "name",
            "body": "body",
            "category": "misc",
            "phone": "phone",
            "email": "email",
            "contact": "contact",
        }
        vals.update(params)
        return cls.model_classified.create(vals)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_0 = cls.env["res.partner"].create({"name": "P0"})
        cls.partner_1 = cls.env["res.partner"].create({"name": "P1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "P2"})
        cls.partners = cls.partner_0 + cls.partner_1 + cls.partner_2

        cls.state_wlg = cls.env.ref("alc_address_data.province_wlg")
        cls.state_wbr = cls.env.ref("alc_address_data.province_wbr")

        cls.model_classified = cls.env["alc.classified"]

        cls.classified_1_misc = cls.create_classified()
        cls.classified_1_employment = cls.create_classified(category="employment")

        cls.classifieds_1 = cls.classified_1_misc | cls.classified_1_employment

        cls.classified_2_misc = cls.create_classified(cls.partner_2)
        cls.classified_2_wbr = cls.create_classified(cls.partner_2, cls.state_wbr)

        cls.classifieds_2 = cls.classified_2_misc | cls.classified_2_wbr

        cls.classifieds = cls.classifieds_1 | cls.classifieds_2
