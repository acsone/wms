# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestRegistrationMixin(TransactionCase):
    def _get_registration_vals(self, **kwargs):
        vals = {
            "name": "first last",
            "title": self.env.ref("base.res_partner_title_madam").id,
            "occupation": "veterinary",
            "company_name": "company_name",
            "clientele": "equine",
            "street": "14 rue de la gaufre",
            "street2": "porte 2",
            "zip": "4000",
            "city": "Liège",
            "country_name": "Belgik",  # no enforcement of correct spelling
            "vet_depot_number": "vet_depot_number",
            "vet_subscription_number": "vet_subscription_number",
            "apb_authorization": "apb_authorization",
            "vat": "vat",
            "comment": "comment",
            "email": "email",
            "mobile": "mobile",
            "fax": "fax",
            "phone": "phone",
            "opt_out": False,
        }
        return dict(vals, **kwargs)
