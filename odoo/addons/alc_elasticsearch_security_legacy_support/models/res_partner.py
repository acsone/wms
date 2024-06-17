# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_elasticsearch_security.models import res_partner


class ResPartner(res_partner.ResPartner):
    def _get_elasticearch_roles(self):
        roles = super()._get_elasticearch_roles()
        # check config parameter to add old roles
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_elasticsearch_security_legacy_support.enable", False)
        ):
            roles.add(self.property_product_pricelist.old_role_name)
            for old_role_name in self.discount_pricelist_ids.mapped("old_role_name"):
                roles.add(old_role_name)
            # add old vt group old role names
            for vt_group in self.veterinary_group_ids:
                roles.add(vt_group._get_old_role_name())
        return roles
