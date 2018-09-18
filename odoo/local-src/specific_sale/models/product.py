# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _sales_count(self):
        # rewrite of method as sale.report is very slow to load
        query = """
            SELECT
                product_id,
                sum ("sale_order_line"."product_uom_qty") AS "product_uom_qty",
                state
                FROM sale_order_line
                WHERE state in ('sale', 'done')
                    AND product_id in %s
                GROUP BY product_id, state
                """
        self._cr.execute(query, (tuple(self.ids), ))

        done = {}
        for product_id, qty, state in self._cr.fetchall():
            product = self.browse(product_id)
            if state == 'sale':
                product.sale_lines_count = qty
            elif state == 'done':
                done[product_id] = qty
            product.sales_count = (product.sale_lines_count +
                                   done.get(product_id, 0))

    sale_lines_count = fields.Integer(
        compute='_sales_count'
    )

    older_lot_id = fields.Many2one(
        'stock.production.lot',
        string='Older lot',
        compute='_compute_older_lot_id'
    )

    def _compute_older_lot_id(self):
        get_lot_query = """
        SELECT lot.id
        FROM stock_production_lot AS lot
        WHERE lot.product_id = %s
        AND lot.is_archived = FALSE
        AND EXISTS (SELECT 1 FROM stock_quant AS quant
                    WHERE quant.lot_id = lot.id
                    AND quant.qty > 0)
        ORDER BY lot.life_date
        LIMIT 1;
        """

        for product in self:
            self.env.cr.execute(get_lot_query, (product.id, ))
            result = self.env.cr.fetchone()

            if result:
                product.older_lot_id = result[0]

    @api.model
    def get_cnk_products_domain(self):
        """ Generate the domain to get stock with CNK product """
        domain = [('sale_ok', '=', True), ('cnk_code', '!=', False)]

        user_newpharma = self.env.ref('__setup__.res_user_newpharma',
                                      raise_if_not_found=False)

        if user_newpharma and self.env.context.get('uid') == user_newpharma.id:
            domain += self.get_newpharma_products_domain()

        return domain

    @api.model
    def get_sku_products_domain(self):
        """ Generate the domain to get stock with SKU product """
        domain = [('sale_ok', '=', True), ('default_code', '!=', False)]

        user_olalux = self.env.ref('__setup__.res_user_olalux',
                                   raise_if_not_found=False)

        if user_olalux and self.env.context.get('uid') == user_olalux.id:
            domain += self.get_olalux_products_domain()

        return domain

    @api.model
    def get_newpharma_products_domain(self):
        """ Return an additional domain (used by the method search on
        product.product) for the wholesaler NewPharma.
        """

        return [('veterinary_only', '=', False)]

    @api.model
    def get_olalux_products_domain(self):
        """ Return an additional domain (used by the method search on
        product.product) for the wholesaler Olalux.

        Olalux can only have an access to following products:
        - All products from Royal Canin, Hill's and Nestle
        - Only food from V.M.D Aliments and DECHRA * (60422)
        - Only food and parapharmacie from VIRBAC Belgium
        and VIRBAC Belgium aliments
        """

        ##########################
        # All products suppliers #
        ##########################
        royal_canin = self.env.ref('__import__.supplier_78650',
                                   raise_if_not_found=False)
        hills = self.env.ref('__import__.supplier_68250',
                             raise_if_not_found=False)
        nestle = self.env.ref('__import__.supplier_61800',
                              raise_if_not_found=False)

        all_products_supplier = self.env['res.partner']
        if royal_canin:
            all_products_supplier |= royal_canin
        if hills:
            all_products_supplier |= hills
        if nestle:
            all_products_supplier |= nestle

        #######################
        # only food suppliers #
        #######################
        dechra = self.env.ref('__import__.supplier_60422',
                              raise_if_not_found=False)
        vmd_aliment = self.env.ref('__import__.supplier_82702',
                                   raise_if_not_found=False)

        only_food_suppliers = self.env['res.partner']
        if vmd_aliment:
            only_food_suppliers |= vmd_aliment
        if dechra:
            only_food_suppliers |= dechra

        #######################
        # specific for Virbac #
        #######################
        virbac_belgium = self.env.ref('__import__.supplier_81200',
                                      raise_if_not_found=False)
        virbac_belgium_aliment = self.env.ref('__import__.supplier_81201',
                                              raise_if_not_found=False)

        virbac_suppliers = self.env['res.partner']
        if virbac_belgium:
            virbac_suppliers |= virbac_belgium
        if virbac_belgium_aliment:
            virbac_suppliers |= virbac_belgium_aliment

        categ_ali = self.env.ref('specific_data.product_categ_ali')
        categ_parapharmacie = \
            self.env.ref('specific_data.product_categ_parapharmacie')

        domain = [
            '|',
            ('supplier_id', 'in', all_products_supplier.ids),
            '|',
            '&',
            ('supplier_id', 'in', only_food_suppliers.ids),
            ('categ_id', 'child_of', categ_ali.id),
            '&',
            ('supplier_id', 'in', virbac_suppliers.ids),
            '|',
            ('categ_id', 'child_of', categ_ali.id),
            ('categ_id', 'child_of', categ_parapharmacie.id)
        ]

        return domain


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_lines_count = fields.Integer(
        compute='_compute_sale_lines_count'
    )

    lot_ids = fields.Many2many(
        'stock.production.lot',
        string='Lots',
        compute='_compute_lot_ids',
        readonly=True
    )

    def _compute_lot_ids(self):
        StockProductionLot = self.env['stock.production.lot']

        for product_tmpl in self:
            products = product_tmpl.product_variant_ids
            lots = StockProductionLot.search([
                ('product_id', 'in', products.ids),
                ('is_archived', '=', False)],
                order='life_date'
            )
            product_tmpl.lot_ids = [(6, 0, lots.ids)]

    @api.multi
    @api.depends('product_variant_ids.sales_count')
    def _compute_sale_lines_count(self):
        for product in self:
            product.sale_lines_count = sum(
                [p.sale_lines_count for p in product.product_variant_ids])

    @api.multi
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            'specific_sale.action_sale_lines_unavailable_list'
        ).read()[0]
        action_data['domain'] = [
            ('state', 'in', ['sale']),
            ('product_id.product_tmpl_id', '=', self.id)
        ]

        return action_data

    @api.multi
    def action_view_sales(self):
        res = super(ProductTemplate, self).action_view_sales()
        if res['context']:
            action_context = ast.literal_eval(res['context'])
            action_context[
                'search_default_remains_to_deliver'
            ] = 1
            res['context'] = str(action_context)
        else:
            res['context'] = "{"\
                "'search_default_remains_to_deliver': 1," \
                "}"
        return res
