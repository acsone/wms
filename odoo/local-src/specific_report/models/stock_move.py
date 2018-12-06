# -*- coding: utf-8 -*-
# Copyright 2017-2018 Sylvain Van Hoof (Okia) <sylvain@okia.be>
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree
import json

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    # This field is only used for information
    serial_number = fields.Char(
        'Serial number', readonly=True,
        help='For delivery order only')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Display serial number + edit button only on delivery order
        (i.e.  destination location = customer location)
        """
        res = super(StockMove, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != 'tree':
            return res
        customer_location = self.env.ref('stock.stock_location_customers')
        if (self.env.context.get('default_location_dest_id') !=
                customer_location.id):
            return res
        arch = etree.XML(res['arch'])
        for node in arch.xpath("//field[@name='serial_number'] | "
                               "//button[@name='button_edit_serial_number']"):
            if node.get('modifiers'):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['tree_invisible'] = False
                node.set('modifiers', json.dumps(modifiers))
        res['arch'] = etree.tostring(arch)
        return res

    @api.multi
    def button_edit_serial_number(self):
        return self.env.ref('specific_report.action_edit_serial_number')\
            .read()[0]

    @api.multi
    def get_lots(self):
        """
        Return all lots for the stock move
        :return: Return a list of tuple
        """
        qty_by_lot = {}

        quants = filter(
            None, self.linked_move_operation_ids.mapped('reserved_quant_id'))
        for quant in quants:
            if not quant.lot_id:
                continue
            lot = quant.lot_id

            existing_qty = qty_by_lot.get(lot.name, [])
            if existing_qty:
                qty_by_lot[lot.name] = [existing_qty[0] +
                                        quant.qty, existing_qty[1]]
            else:
                qty_by_lot[lot.name] = [quant.qty, lot.life_date or '']

        result = [[key, value[0], value[1]]
                  for key, value
                  in qty_by_lot.iteritems()]

        # Sort lot by name
        return sorted(result, key=lambda lot: lot[0])
