# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class TestRegistration(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestRegistration, cls).setUpClass()
        cls.model = cls.env["alc.registration"]

    def _get_registration_vals(self, **kwargs):
        vals = {
            "name": "first last",
            "title": self.env.ref("base.res_partner_title_madam").id,
            "company_name": "company_name",
            "clientele": "equine",
            "street": "14 rue de la gaufre",
            "street2": "porte 2",
            "zip": "4000",
            "city": "Liège",
            "country_id": self.env.ref("base.be").id,
            "vet_depot_number": "vet_depot_number",
            "vet_subscription_number": "vet_subscription_number",
            "apb_authorization": "apb_authorization",
            "vat": "vat",
            "partner_type": "veterinary",
            "comment": "comment",
            "email": "email",
            "mobile": "mobile",
            "fax": "fax",
            "phone": "phone",
            "opt_out": False,
        }
        return dict(vals, **kwargs)
