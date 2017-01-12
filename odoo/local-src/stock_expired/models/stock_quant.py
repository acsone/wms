# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import itertools

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    alert_date = fields.Datetime(
        related='lot_id.alert_date',
        store=True,
        readonly=True,
    )

    use_date = fields.Datetime(
        related='lot_id.use_date',
        store=True,
        readonly=True,
    )

    life_date = fields.Datetime(
        related='lot_id.life_date',
        store=True,
        readonly=True,
    )

    @api.model
    def apply_removal_strategy(
            self, qty, move, ops=False, domain=None, removal_strategy='fifo'
    ):
        deny_reservation_for_quants_expired = True

        context = self.env.context or {}
        if (
            context.get('params')
            and context.get('params').get('model') == 'stock.picking'
            and context.get('params').get('id')
        ):
            picking = self.env['stock.picking'].browse(
                context['params']['id']
            )
            if picking and picking.to_process_quant_expired:
                deny_reservation_for_quants_expired = False

        new_domain = domain or []
        if deny_reservation_for_quants_expired:
            new_domain.append('|')
            new_domain.append('|')
            new_domain.append(('removal_date', '=', False))
            new_domain.append(('removal_date', '>', fields.Datetime.now()))
            new_domain.append(
                ('location_id.ignore_quants_expiration', '=', True)
            )

        return super(StockQuant, self).apply_removal_strategy(
            qty=qty,
            move=move,
            ops=ops,
            domain=new_domain,
            removal_strategy=removal_strategy
        )

    @api.model
    def alert_quant_expired(self):
        domain = [
            ('lot_id.alert_date', '<=', fields.Datetime.now()),
            ('location_id.usage', '=', 'internal'),
            ('location_id.ignore_quants_expiration', '=', False),
        ]
        quants = self.env['stock.quant'].search(domain)
        if len(quants) > 0:
            template = self.env.ref(
                'stock_expired.email_template_alert_quant_expired'
            )
            # To sent only one mail :
            # We create the mail on the first quant on alert
            # and we pass the list of quants on alert in context
            template.with_context(
                quants_on_alert=quants
            ).send_mail(quants[0].id)

    @api.model
    def process_quant_expired(self):
        current_pickings = self.env['stock.picking'].search([
            ('to_process_quant_expired', '=', True),
            ('state', '!=', 'done')
        ])
        quants_already_processed = current_pickings.mapped(
            'move_lines.reserved_quant_ids'
        )
        domain = [
            ('removal_date', '<=', fields.Datetime.now()),
            ('location_id.usage', '=', 'internal'),
            ('location_id.ignore_quants_expiration', '=', False),
            ('id', 'not in', quants_already_processed.ids)
        ]
        quants = self.env['stock.quant'].search(domain)
        if len(quants) > 0:
            picking_type = self.env.ref('stock.picking_type_internal')
            location_src = self.env.ref('stock.stock_location_stock')
            location_dest = self.env.ref('stock.stock_location_scrapped')
            move_lines = []
            for product, product_quants in itertools.groupby(
                quants,
                lambda q: q.product_id,
            ):
                quantity = 0
                move_quants = []
                for quant in product_quants:
                    quantity += quant.qty
                    move_quants.append(quant.id)
                move_lines.append(
                    (0, 0, {
                        'name': product.name_get()[0][1],
                        'product_id': product.id,
                        'product_uom_qty': quantity,
                        'product_uom': product.uom_id.id,
                        'location_id': location_src.id,
                        'location_dest_id': location_dest.id,
                        'reserved_quant_ids': [(6, None, move_quants)],
                    })
                )
            picking = self.env['stock.picking'].create({
                'to_process_quant_expired': True,
                'picking_type_id': picking_type.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'move_lines': move_lines,
            })
            picking.action_confirm()
