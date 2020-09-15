# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from . import common


class TestStockDeliveryNoteAdditionalProduct(
    common.StockDeliveryNoteAdditionalProductTestCase
):
    @classmethod
    def setUpClass(cls):
        super(TestStockDeliveryNoteAdditionalProduct, cls).setUpClass()

    def test_delivery_note_line_with_additional_product(self):
        """Check that if an additional product is linked to a product, no prices are given for it"""
        tax_amount = ",".join(str(self.tax.amount).split("."))
        # Check that the additional product is taken into account after confirmation
        sale = self._confirm_sale_order()
        picking = self.create_pick(sale)

        expected = [
            [picking.id, "", ""],
            [u"Unittest first partner", "", "", "", ""],
            [
                "1234567",
                self.main_product.name,
                "10,000",
                "50,00",
                "50,00",
                tax_amount,
                "",
                "",
                "",
                "",
            ],
            [
                "987654321",
                self.additional_product.name,
                "10,000",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        ]

        for move in picking.move_lines:
            move.write({"state": "done", "order_line_id": sale.order_line.id})

        picking.do_transfer()
        lines = picking._generate_delivery_note()
        self.assertEqual(lines, expected)
