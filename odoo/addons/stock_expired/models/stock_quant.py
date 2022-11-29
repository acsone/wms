# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# Copyright 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools

from odoo import api, fields, models
from odoo.osv.expression import FALSE_LEAF, NEGATIVE_TERM_OPERATORS, TRUE_LEAF


class StockQuant(models.Model):
    _inherit = "stock.quant"

    alert_date = fields.Datetime(related="lot_id.alert_date", store=True, readonly=True)
    use_date = fields.Datetime(related="lot_id.use_date", store=True, readonly=True)
    life_date = fields.Datetime(related="lot_id.life_date", store=True, readonly=True)
    is_expired = fields.Boolean(
        compute="_compute_is_expired", search="_search_is_expired"
    )
    expiry_date = fields.Datetime(
        related="lot_id.expiry_date", store=True, index=True, readonly=True
    )

    @api.depends("lot_id.is_expired")
    def _compute_is_expired(self):
        for rec in self:
            rec.is_expired = rec.lot_id.is_expired

    def _search_is_expired(self, operator, value):
        domain = []
        negative_operator = operator in NEGATIVE_TERM_OPERATORS
        search_expired = (  # atomic case
            # is_expired != False
            (negative_operator and not value)
            or
            # is_expired = True
            (not negative_operator and value)
        )
        if "in" in operator:  # value should be a list
            if not value:
                domain = TRUE_LEAF if negative_operator else FALSE_LEAF
            elif True in value and False in value:
                domain = FALSE_LEAF if negative_operator else TRUE_LEAF
            elif False in value:  # not in [False]
                search_expired = negative_operator
            else:  # in [True]
                search_expired = not negative_operator
        if search_expired:
            domain = domain or [("expiry_date", "<", fields.Datetime.now())]
        else:
            domain = domain or [
                "|",
                ("expiry_date", "=", False),
                ("expiry_date", ">=", fields.Datetime.now()),
            ]
        return domain

    def _quants_get_reservation_domain(
        self,
        move,
        pack_operation_id=False,
        lot_id=False,
        company_id=False,
        initial_domain=None,
    ):
        deny_reservation_for_quants_expired = True
        if (
            move.picking_id.to_process_quant_expired
            or move.scrapped
            or not move.picking_id
        ):
            deny_reservation_for_quants_expired = False

        new_domain = initial_domain or []
        if deny_reservation_for_quants_expired:
            new_domain.append("|")
            new_domain.append(("is_expired", "=", False))
            new_domain.append(("location_id.ignore_quants_expiration", "=", True))

        return super(StockQuant, self)._quants_get_reservation_domain(
            move,
            pack_operation_id=pack_operation_id,
            lot_id=lot_id,
            company_id=company_id,
            initial_domain=new_domain,
        )

    @api.model
    def alert_quant_expired(self):
        domain = [
            ("alert_date", "<=", fields.Datetime.now()),
            ("location_id.usage", "=", "internal"),
            ("location_id.ignore_quants_expiration", "=", False),
        ]
        StockQuantModel = self.env["stock.quant"]
        with StockQuantModel._auto_join(["lot_id", "location_id"]):
            quants = self.env["stock.quant"].search(domain)
        if len(quants) > 0:
            template = self.env.ref("stock_expired.email_template_alert_quant_expired")
            # To sent only one mail :
            # We create the mail on the first quant on alert
            # and we pass the list of quants on alert in context
            template.with_context(quants_on_alert=quants).send_mail(quants[0].id)

    @api.model
    def process_quant_expired(self):
        current_pickings = self.env["stock.picking"].search(
            [("to_process_quant_expired", "=", True), ("state", "!=", "done")]
        )
        quants_already_processed = current_pickings.mapped(
            "move_lines.reserved_quant_ids"
        )
        domain = [
            ("is_expired", "=", True),
            ("location_id.usage", "=", "internal"),
            ("location_id.ignore_quants_expiration", "=", False),
            ("id", "not in", quants_already_processed.ids),
        ]
        StockQuantModel = self.env["stock.quant"]
        with StockQuantModel._auto_join(["lot_id", "location_id"]):
            quants = StockQuantModel.search(domain)
        picking_type = self.env.ref("stock_expired.picking_type_scrap")
        location_dest = picking_type.default_location_dest_id
        for location_src, quants_bylocation in itertools.groupby(
            quants, lambda q: q.location_id
        ):
            move_lines = []
            for product, product_quants in itertools.groupby(
                quants_bylocation, lambda q: q.product_id
            ):
                quantity = 0
                move_quants = []
                for quant in product_quants:
                    quantity += quant.qty
                    move_quants.append(quant.id)
                move_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": product.name_get()[0][1],
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                            "product_uom": product.uom_id.id,
                            "location_id": location_src.id,
                            "location_dest_id": location_dest.id,
                            "reserved_quant_ids": [(6, None, move_quants)],
                        },
                    )
                )
            picking = self.env["stock.picking"].create(
                {
                    "to_process_quant_expired": True,
                    "picking_type_id": picking_type.id,
                    "location_id": location_src.id,
                    "location_dest_id": location_dest.id,
                    "move_lines": move_lines,
                }
            )
            picking.action_confirm()
            picking.action_assign()
