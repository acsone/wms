# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, api, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


def hw_print(self, report_xmlid, printer=False, qty=1):
    document = self.env['report']._get_raw(self._ids, report_xmlid, qty=qty)
    report = self.env.ref(report_xmlid)
    behaviour = report.behaviour()[report.id]
    if not printer:
        printer = behaviour['printer']
    if not printer:
        raise Warning(_('No printer assigned'))
    try:
        printer.print_document(report, document, 'text')
    except UnicodeEncodeError as e:
        raise e
    except Exception as e:
        _logger.error(str(e))
        raise Warning(_('Printer unavailable'))


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def get_so_partner(self):
        """ Find SO Customer:
            - first find the related move (picking)
            - then find the delivery move (shipping)
            - then find the related procurement
            - then find the originate sales order
            - finally have the customer
        """
        self.ensure_one()
        moves = self.linked_move_operation_ids.mapped('move_id')

        def descend_moves(lvl):
            next_lvl = lvl.mapped('move_dest_id')
            if next_lvl:
                lvl |= descend_moves(next_lvl)
            return lvl

        moves = descend_moves(moves)
        partners = moves.mapped(
            'procurement_id.sale_line_id.order_id.partner_id')
        # While we could potentially have multiple SO, and so partners,
        # practically it won't be the case in 99% otherwise it's not important
        # which one we return
        return partners and partners[0]

    @api.multi
    def print_product_label(self, printer=False):
        for op in self:
            if not op.picking_id.partner_id:
                raise Warning(_('No destination partner defined'))
        hw_print(self, 'specific_print.report_stock_product_label',
                 printer=printer)

    @api.multi
    def get_qty_by_lot(self):
        """
        This method will return the quantity by lot.
        If the product is not track by lot
        we return the quantity done without lot
        :return:
        """
        self.ensure_one()

        if not self.pack_lot_ids:
            return [(int(self.qty_done), None)]

        result = []
        for pack in self.pack_lot_ids:
            result.append((int(pack.qty), pack.lot_id))

        return result


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def print_products_label(self, printer=False):
        self.ensure_one()

        packs_to_print = self.pack_operation_ids.filtered(
            lambda pack_op: not pack_op.product_id.is_do_not_print_label)
        if packs_to_print:
            packs_to_print.print_product_label(printer=printer)

    @api.multi
    def print_packages_label(self, quantity=1, printer=False):
        self.ensure_one()
        if not self.partner_id:
            raise Warning(_('No destination partner defined'))
        hw_print(self,
                 'specific_print.report_stock_pick_packs_label',
                 printer=printer,
                 qty=quantity)

    @api.multi
    def print_passport_report(self, printer):
        self.ensure_one()
        pdf = self.env['report']\
            .get_pdf(self.ids, 'specific_report.report_passport')
        printer.print_document('', pdf, '')


class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    @api.multi
    def print_lot_label(self, quantity=1):
        self.ensure_one()
        self.lot_id.print_lot_label()


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def print_lot_label(self, quantity=1, printer=False):
        self.ensure_one()
        hw_print(self, 'specific_print.report_lot_label',
                 qty=quantity, printer=printer)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def print_lot_label(self, quantity=1):
        self.ensure_one()
        hw_print(self, 'specific_print.report_lot_nolot_label', qty=quantity)
