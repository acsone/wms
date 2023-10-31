# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_keycloak.models.keycloak_backend import (
    KeycloakBackend as KeycloakBackendBase,
)


class KeycloakBackend(KeycloakBackendBase):

    _inherit = "keycloak.backend"

    def _get_update_fields(self):
        res = super()._get_update_fields()
        new = {  # elasticsearch_role is a compute depending on these
            "partner_type": "shopinvader-vt-roles",
            "property_product_pricelist": "shopinvader-vt-roles",
            "discount_pricelist_ids": "shopinvader-vt-roles",
            "supplier_promotion_sale_allowed": "shopinvader-vt-roles",
            "date_start_contract_alcyonnaire": "shopinvader-vt-roles",
            "date_end_contract_alcyonnaire": "shopinvader-vt-roles",
            "lang": "locale",
            "ref": "ref",
            "eshop_ordering_allowed": "can_order",
            "help_with_fee": "help_with_fee",
            "veterinary_group_ids": "vt-groups",
        }
        res.update(new)
        return res

    def _keycloak_user_to_payload(self, keycloak_user):
        payload = super()._keycloak_user_to_payload(keycloak_user)
        partner = keycloak_user.partner_id
        discounts = partner.discount_pricelist_ids.mapped("discount_role_name")
        new_attributes = {
            "locale": partner.lang,
            "shopinvader-vt-roles": partner.elasticsearch_role,
            "supplier_id": partner.id,
            "ref": partner.ref or None,
            "can_order": partner.eshop_ordering_allowed,
            "help_with_fee": partner.help_with_fee,
            "vt-groups": partner.veterinary_group_ids.ids,
            "vt-pricelist-gross": partner.property_product_pricelist.role_name or None,
            "vt-pricelist-discounts": discounts,
            "vt-supplier-promotion": partner.supplier_promotion_sale_allowed,
        }
        payload["attributes"].update(new_attributes)
        return payload
