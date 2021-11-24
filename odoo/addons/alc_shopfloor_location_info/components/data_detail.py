# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo.addons.component.core import Component


class DataDetailAction(Component):
    _inherit = "shopfloor.data.detail.action"

    @property
    def _location_detail_parser(self):
        parser = super(DataDetailAction, self)._location_detail_parser
        parser.append(("products", lambda record, fname: self.location_content(record)))
        return parser

    def location_content(self, record):
        res = []
        product_qties = defaultdict(lambda: defaultdict(lambda: 0))
        for quant in record.quant_ids:
            if quant.reservation_id:
                continue
            product_qties[quant.product_id][quant.lot_id] += quant.qty
        for product, quants_qty in product_qties.items():
            val = self.product(product)
            lots = []
            val["lots"] = lots
            qty_total = 0
            for lot, qty in quants_qty.items():
                qty_total += qty
                if not lot:
                    continue
                lot_val = self.location_lot(lot)
                lot_val["quantity"] = qty
                lots.append(lot_val)
            val["quantity"] = qty_total
            res.append(val)
        return res

    def location_lot(self, record, **kw):
        # Define a new method to not overload the base one which is used in many places
        return self._jsonify(record, self._location_lot_detail_parser, **kw)

    @property
    def _location_lot_detail_parser(self):
        return self._lot_parser + [
            "removal_date",
            "life_date:expire_date",
        ]
