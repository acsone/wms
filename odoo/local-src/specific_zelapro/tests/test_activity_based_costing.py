# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from odoo import fields


class TestActivityBasedCostring(common.TransactionCase):

    INVOICES_BY_PRODUCTS = {
        1: (1, 100), # CA 100
        2: (2, 25), # CA 50
        3: (8, 10), # CA 80
        4: (15, 20), # CA 300
        5: (0, 0), # CA 0,
        6: (1, 50), # CA 50
        7: (16, 5), # CA 80
        8: (5, 20), # CA 100
        9: (25, 8), # CA 200
        10: (8, 5), # CA 40
    }

    def test_compute_ca_by_product(self):
        """
        Compute the CA for all products and check the sum
        :return:
        """

        disable_products = "UPDATE product_product SET active = FALSE;"
        self.env.cr.execute(disable_products)

        product_obj = self.env['product.product']
        invoice_obj = self.env['account.invoice']

        journal = invoice_obj._default_journal()
        account = self.env.ref('__setup__.account_400000')
        account_line = self.env.ref('__setup__.account_701000')

        partner = self.env['res.partner'].create({
            'name': 'Partner'
        })

        # Create all products (see INVOICES_BY_PRODUCTS)
        for product_num in range(1, len(self.INVOICES_BY_PRODUCTS) + 1):
            product = product_obj.create({
                'name': 'Product %s' % product_num
            })
            setattr(self, 'product_%s' % product_num, product)

            quantity, price_unit = self.INVOICES_BY_PRODUCTS[product_num]
            invoice_obj.create({
                'partner_id': partner.id,
                'journal_id': journal.id,
                'account_id': account.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': product.id,
                        'name': 'Invoice Line %s' % product_num,
                        'account_id': account_line.id,
                        'quantity': quantity,
                        'price_unit': price_unit
                    })
                ]
            })

        ca_total = product_obj.compute_ca_by_product()

        self.assertEquals(ca_total, 1000.0)
        self.assertEquals(getattr(self, 'product_1').year_ca, 100.0)
        self.assertEquals(getattr(self, 'product_2').year_ca, 50.0)
        self.assertEquals(getattr(self, 'product_3').year_ca, 80.0)
        self.assertEquals(getattr(self, 'product_4').year_ca, 300.0)
        self.assertEquals(getattr(self, 'product_5').year_ca, 0.0)

        self.assertEquals(getattr(self, 'product_6').year_ca_nbr_lines, 1)
        self.assertEquals(getattr(self, 'product_7').year_ca_nbr_lines, 1)

        # Create ABC rate
        abc_obj = self.env['activity.based.costing']
        abc_obj.search([]).unlink()
        rate_a = abc_obj.create({
            'code': 'A',
            'rate': 60
        })
        rate_b = abc_obj.create({
            'code': 'B',
            'rate': 75
        })
        rate_c = abc_obj.create({
            'code': 'C',
            'rate': 100
        })

        ir_config = self.env['ir.config_parameter']
        ir_config.set_param('zelapro.ca_computation_delay', 12)

        product_obj.compute_abc_rate(ca_total=ca_total)

        self.assertEqual(getattr(self, 'product_1').abc_id, rate_a)
        self.assertEqual(getattr(self, 'product_2').abc_id, rate_c)
        self.assertEqual(getattr(self, 'product_3').abc_id, rate_b)
        self.assertEqual(getattr(self, 'product_4').abc_id, rate_a)
        self.assertEqual(getattr(self, 'product_5').abc_id, rate_c)
        self.assertEqual(getattr(self, 'product_6').abc_id, rate_c)
        self.assertEqual(getattr(self, 'product_7').abc_id, rate_b)
        self.assertEqual(getattr(self, 'product_8').abc_id, rate_a)
        self.assertEqual(getattr(self, 'product_9').abc_id, rate_a)
        self.assertEqual(getattr(self, 'product_10').abc_id, rate_c)
