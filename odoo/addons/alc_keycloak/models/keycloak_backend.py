# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class KeycloakBackend(models.Model):

    _inherit = "keycloak.backend"

    def _get_update_fields(self):
        res = super(KeycloakBackend, self)._get_update_fields()
        new = {  # elasticsearch_role is a compute depending on these
            "partner_type": "shopinvader-vt-roles",
            "property_product_pricelist": "shopinvader-vt-roles",
            "discount_pricelist_id": "shopinvader-vt-roles",
            "supplier_promotion_sale_allowed": "shopinvader-vt-roles",
            "lang": "locale",
            "ref": "ref",
        }
        res.update(new)
        return res

    def _keycloak_user_to_payload(self, keycloak_user):
        payload = super(KeycloakBackend, self)._keycloak_user_to_payload(keycloak_user)
        new_attributes = {
            "locale": keycloak_user.partner_id.lang,
            "shopinvader-vt-roles": keycloak_user.partner_id.elasticsearch_role,
            "supplier_id": keycloak_user.partner_id.id,
            "ref": keycloak_user.partner_id.ref or None,
        }
        payload["attributes"].update(new_attributes)
        return payload
