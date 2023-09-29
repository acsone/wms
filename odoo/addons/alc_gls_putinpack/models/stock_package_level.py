# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_package_level import StockPackageLevel


class PackageLevel(StockPackageLevel):
    def display_package_content(self):
        package_wizard = self.env["delivery.package.gls.wizard"].create(
            {
                "picking_id": self.picking_id.id,
                "package_id": self.package_id.id,
                "package_type_id": self.package_id.package_type_id.id,
            }
        )
        return dict(
            self.env["ir.actions.act_window"]._for_xml_id(
                "alc_gls_putinpack.delivery_package_gls_wizard_act_window"
            ),
            res_id=package_wizard.id,
        )
