# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_keycloak.models import keycloak_backend


class KeycloakBackend(keycloak_backend.KeycloakBackend):
    def _keycloak_user_to_payload(self, keycloak_user):
        payload = super()._keycloak_user_to_payload(keycloak_user)
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_elasticsearch_security_legacy_support.enable", False)
        ):
            partner = keycloak_user.partner_id
            attributes = payload["attributes"]
            discounts = attributes.get("vt-pricelist-discounts", [])
            discounts += partner.discount_pricelist_ids.mapped("old_discount_role_name")
            attributes["vt-pricelist-discounts"] = discounts
            attributes[
                "vt-pricelist-gross"
            ] += f",{partner.property_product_pricelist.old_role_name}"
        return payload
