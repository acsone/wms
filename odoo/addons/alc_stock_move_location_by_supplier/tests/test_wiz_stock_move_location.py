# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock_move_location.tests.test_common import TestsCommon


class TestStockMoveLocationBySupplier(TestsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_product_amounts()
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.supplier_2 = cls.env["res.partner"].create({"name": "Supplier 2"})
        cls.product_supplier = cls.env["product.supplierinfo"].create(
            {
                "product_id": cls.product_no_lots.id,
                "partner_id": cls.supplier.id,
                "product_tmpl_id": cls.product_no_lots.product_tmpl_id.id,
            }
        )

    def test_wizard_onchange_origin_location(self):
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        lines = wizard.stock_move_location_line_ids
        nbr_lines_prod_no_lots = len(
            [line for line in lines if line.product_id == self.product_no_lots]
        )
        self.assertTrue(nbr_lines_prod_no_lots >= 1)
        self.assertTrue(nbr_lines_prod_no_lots < len(lines))
        wizard.supplier_ids = self.supplier
        wizard.onchange_supplier_ids()
        new_lines = wizard.stock_move_location_line_ids
        self.assertEqual(len(new_lines), nbr_lines_prod_no_lots)

    def test_wizard_supplier_domain(self):
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        self.assertEqual(wizard.supplier_ids_domain, [("id", "in", [self.supplier.id])])
        self.product_lots.write(
            {"seller_ids": [(0, 0, {"partner_id": self.supplier_2.id})]}
        )
        wizard.invalidate_recordset(["supplier_ids_domain"])
        self.assertEqual(
            wizard.supplier_ids_domain,
            [("id", "in", [self.supplier.id, self.supplier_2.id])],
        )
