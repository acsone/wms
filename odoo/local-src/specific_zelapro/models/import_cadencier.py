# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import traceback
from datetime import datetime
from babel import numbers

from odoo import api, fields, models


class ImportCadencierHeader(models.Model):
    _name = 'import.cadencier.header'
    _inherit = 'import.model'

    columns_mapping = {
        'SFESUI': 'suite_no',
        'SFEFOU': 'supplier_ref',
        'SFENFO': 'supplier_name',
        'SFEDLI': 'scheduled_date',
        'LIBDLI': 'scheduled_date_2',
        'SFEPDS': 'total_weight',
        'SFEMNT': 'total_amount',
        'SFEMNS': 'suggested_amount',
        'SFEDBO': 'older_bo_date',
        'LIBDBO': 'older_bo_date_2',
        'SFESTS': 'status',
        'SFEPRT': 'traite',
    }

    suite_no = fields.Char(index=True)
    supplier_ref = fields.Char()
    supplier_name = fields.Char()
    scheduled_date = fields.Char()
    scheduled_date_2 = fields.Char()
    total_weight = fields.Char()
    total_amount = fields.Char()
    suggested_amount = fields.Char()
    older_bo_date = fields.Char()
    older_bo_date_2 = fields.Char()
    status = fields.Char()
    traite = fields.Char()

    @api.multi
    def execute_import(self, logger_id):
        """
        The import cadencier header is ignored.
        We only need to load data in DB
        :param logger_id:
        :return:
        """
        return True


class ImportCadencier(models.Model):
    _name = 'import.cadencier'
    _inherit = 'import.model'

    columns_mapping = {
        'SFDSUI': 'suite_no',
        'SFDNLI': 'line_index',
        'SFDART': 'product_ref',
        'SFDDEN': 'product_name',
        'SFDQTE': 'qty_ordered',
        'SFDQMO': 'qty_ordered_mod',
        'SFDPAN': 'sale_price',
        'SFDPAM': 'sale_price_mod',
        'SFDR1O': 'supplier_discount',
        'SFDR1M': 'supplier_discount_mod',
        'SFDR2O': 'supplier_discount_2',
        'SFDR2M': 'supplier_discount_2_mod',
        'SFDDLI': 'scheduled_date',
        'LIBDLI': 'scheduled_date_mod',
        'SFDDMO': 'scheduled_date_mod_2',
        'LIBDMO': 'scheduled_date_mod_3',
        'SFDDBO': 'code_delete_bo',
        'SFDDBM': 'code_delete_bo_mod',
        'SFDSTS': 'status',
        'SFDTMI': 'stock_min_total',
        'SFDTMA': 'stock_max_total',
        'SFDTST': 'stock_total',
        'SFDTBO': 'stock_bo_total',
        'SFDTRE': 'stock_reserved_total',
        'SFASUA': 'add_product_supplier_id',
        'SFANLA': 'add_product_line_index',
        'SFAQTA': 'add_product_qty',
        'SFASUP': 'main_product_supplier_id',
        'SFANLP': 'main_product_line_index',
        'SFAQTP': 'main_product_qty',
    }

    suite_no = fields.Char(index=True)
    line_index = fields.Char()
    product_ref = fields.Char()
    product_name = fields.Char()
    qty_ordered = fields.Char()
    qty_ordered_mod = fields.Char()
    sale_price = fields.Char()
    sale_price_mod = fields.Char()
    supplier_discount = fields.Char()
    supplier_discount_mod = fields.Char()
    supplier_discount_2 = fields.Char()
    supplier_discount_2_mod = fields.Char()
    scheduled_date = fields.Char()
    scheduled_date_mod = fields.Char()
    scheduled_date_mod_2 = fields.Char()
    scheduled_date_mod_3 = fields.Char()
    code_delete_bo = fields.Char()
    code_delete_bo_mod = fields.Char()
    status = fields.Char()
    stock_min_total = fields.Char()
    stock_max_total = fields.Char()
    stock_total = fields.Char()
    stock_bo_total = fields.Char()
    stock_reserved_total = fields.Char()
    add_product_supplier_id = fields.Char()
    add_product_line_index = fields.Char()
    add_product_qty = fields.Char()
    main_product_supplier_id = fields.Char()
    main_product_line_index = fields.Char()
    main_product_qty = fields.Char()

    @api.multi
    def execute_import(self, logger_id):
        po_obj = self.env['purchase.order']
        config_param = self.env['ir.config_parameter']
        logger = self.env['import.logger'].browse(logger_id)

        locale = config_param.get_param('import.locale')

        supplier_query = """
        SELECT DISTINCT header.supplier_ref AS supplier_ref,
        supplier.id AS supplier_id,
        (SELECT min(line.scheduled_date_mod_2)
          FROM import_cadencier AS line
          WHERE line.suite_no = header.suite_no) AS scheduled_date
        FROM import_cadencier_header AS header
         LEFT JOIN res_partner AS supplier
         ON supplier.ref = header.supplier_ref;
        """
        self.env.cr.execute(supplier_query)
        suppliers = self.env.cr.fetchall()

        for supplier in suppliers:
            supplier_ref = supplier[0]
            supplier_id = supplier[1]
            scheduled_date_str = supplier[2]

            if not supplier_id:
                logger.line_ids.create({
                    'name': 'Supplier not found with the ref %s'
                            % supplier_ref,
                    'level': 'error',
                    'logger_id': logger_id
                })
                return False

            lines_query = """
            SELECT
              line.id,
              product.id AS product_id,
              line.qty_ordered_mod AS qty_ordered,
              line.sale_price_mod AS sale_price,
              line.supplier_discount_mod AS supplier_discount_1,
              line.supplier_discount_2_mod AS supplier_discount_2,
              line.scheduled_date_mod_2 AS scheduled_date
            FROM import_cadencier AS line
              LEFT JOIN import_cadencier_header
                AS header ON header.suite_no = line.suite_no
              LEFT JOIN res_partner
                AS supplier ON header.supplier_ref = supplier.ref
              LEFT JOIN product_product
                AS product ON line.product_ref = product.default_code
              LEFT JOIN product_template
                AS product_tmpl ON product.product_tmpl_id = product_tmpl.id
            WHERE supplier.id = %s
            ORDER BY line.suite_no;
            """
            self.env.cr.execute(lines_query, (supplier_id,))
            lines = self.env.cr.fetchall()

            try:
                scheduled_date = datetime.strptime(scheduled_date_str,
                                                   '%Y%m%d')
                date_planned = fields.Date.to_string(scheduled_date)
            except:
                logger.line_ids.create({
                    'name': 'Cannot convert the date ' % scheduled_date_str,
                    'level': 'error',
                    'logger_id': logger_id
                })
                return False

            # Create the sale order
            purchase_order = po_obj.create({
                'partner_id': supplier_id,
                'date_planned': date_planned
            })

            for line in lines:
                line_id = line[0]
                product_id = int(line[1])
                product_qty = numbers.parse_decimal(line[2], locale=locale)
                sale_price = numbers.parse_decimal(line[3], locale=locale)
                discount_1 = numbers.parse_decimal(line[4], locale=locale)
                discount_2 = numbers.parse_decimal(line[5], locale=locale)

                line_date_str = line[6]
                line_date = datetime.strptime(line_date_str, '%Y%m%d')
                line_date_planned = fields.Date.to_string(line_date)

                po_line = purchase_order.order_line.new({
                    'product_id': product_id,
                })
                po_line.onchange_product_id()

                po_line.update({
                    'date_planned': line_date_planned,
                    'product_qty': product_qty,
                    'price_unit_base': sale_price,
                    'discount_global': discount_1,
                    'promotion_supplier': discount_2,
                    'order_id': purchase_order.id,
                })
                po_line._compute_price_unit()

                try:
                    # Create the purchase line
                    po_line.create(po_line._convert_to_write(po_line._cache))
                except:
                    logger.line_ids.create({
                        'name': 'Cannot create the purchase line (line %s)'
                                % line_id,
                        'level': 'error',
                        'logger_id': logger_id,
                        'traceback': traceback.format_exc(),
                    })
                    return False

        return True
