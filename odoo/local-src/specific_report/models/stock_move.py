# -*- coding: utf-8 -*-
# Copyright 2017-2018 Sylvain Van Hoof (Okia) <sylvain@okia.be>
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from lxml import etree
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    # This field is only used for information
    serial_number = fields.Char(
        'Serial number', readonly=True, help='For delivery order only'
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        """Display serial number + edit button only on delivery order
        (i.e.  destination location = customer location)
        """
        res = super(StockMove, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type != 'tree':
            return res
        customer_location = self.env.ref('stock.stock_location_customers')
        if (
            self.env.context.get('default_location_dest_id')
            != customer_location.id
        ):
            return res
        arch = etree.XML(res['arch'])
        for node in arch.xpath(
            "//field[@name='serial_number'] | "
            "//button[@name='button_edit_serial_number']"
        ):
            if node.get('modifiers'):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['tree_invisible'] = False
                node.set('modifiers', json.dumps(modifiers))
        res['arch'] = etree.tostring(arch)
        return res

    @api.multi
    def button_edit_serial_number(self):
        return self.env.ref(
            'specific_report.action_edit_serial_number'
        ).read()[0]
