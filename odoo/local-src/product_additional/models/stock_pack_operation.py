from odoo import api, fields, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    main_operation_id = fields.Many2one('stock.pack.operation',
                                        'Main operation',
                                        ondelete='cascade')

    @api.model
    def create(self, vals):
        result = super(StockPackOperation, self).create(vals)

        if 'product_id' not in vals or 'product_uom_id' not in vals:
            return result

        product_id = vals['product_id']
        product_uom_id = vals['product_uom_id']
        product_qty = vals['product_qty']
        picking_id = vals['picking_id']

        add_product_query = """
        SELECT 
          add_product.id,
          add_product_tmpl.uom_id,
          product_tmpl.ratio_main_product,
          product_tmpl.ratio_additional_product
        FROM product_product AS product
          INNER JOIN product_template AS product_tmpl
            ON product.product_tmpl_id = product_tmpl.id
          INNER JOIN product_template AS add_product_tmpl
            ON product_tmpl.additional_product_id = add_product_tmpl.id
          INNER JOIN product_product AS add_product
            ON add_product_tmpl.id = add_product.product_tmpl_id
        WHERE product.id = %s;
        """
        self.env.cr.execute(add_product_query, (product_id, ))
        add_result = self.env.cr.fetchone()
        if not add_result:
            return add_result

        product_id = add_result[0]
        uom_id = add_result[1]
        ratio_main_product = add_result[2]
        ratio_additional_product = add_result[3]

        if product_uom_id != uom_id:
            product_uom = self.env['product.uom'].browse(product_uom_id)
            product_qty = product_uom._compute_quantity(product_qty, uom_id)

        coefficient = int(product_qty / ratio_main_product)
        add_product_qty = coefficient * ratio_additional_product

        additional_vals = {
            'picking_id': picking_id,
            'main_operation_id': result.id,
            'product_id': product_id,
            'product_qty': add_product_qty
        }

        super(StockPackOperation, self).create(additional_vals)

        return result
