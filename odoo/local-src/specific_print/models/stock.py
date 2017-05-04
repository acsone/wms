# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _
from odoo.exceptions import Warning


def hw_print(self, report_xmlid, printer=False):
    document = self.env['report']._get_raw(self._ids, report_xmlid)
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
    except:
        raise Warning(_('Printer unavailable'))


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def print_product_label(self, printer=False):
        for op in self:
            if not op.picking_id.partner_id:
                raise Warning(_('No destination partner defined'))
        hw_print(self, 'specific_print.report_stock_product_label',
                 printer=printer)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def print_products_label(self, printer=False):
        self.ensure_one()
        self.pack_operation_ids.print_product_label(printer=printer)

    @api.multi
    def print_packages_label(self, quantity=1, printer=False):
        self.ensure_one()
        if not self.partner_id:
            raise Warning(_('No destination partner defined'))
        hw_print(self.with_context(nbr=int(quantity)),
                 'specific_print.report_stock_pick_packs_label',
                 printer=printer)

    @api.multi
    def print_passport_report(self, printer):
        self.ensure_one()
        pdf = self.env['report']\
            .get_pdf(self.ids, 'specific_report.report_passport')
        printer.print_document('', pdf, '')


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def print_lot_label(self, quantity=1):
        self.ensure_one()
        hw_print(self.with_context(nbr=int(quantity)),
                 'specific_print.report_lot_label')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def print_lot_label(self, quantity=1):
        self.ensure_one()
        hw_print(self.with_context(nbr=int(quantity)),
                 'specific_print.report_lot_nolot_label')
