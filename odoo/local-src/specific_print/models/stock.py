# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016 BCIM sprl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields, _
from openerp.exceptions import Warning


def hw_print(self, report_xmlid):
    document = self.env['report']._get_raw(self._ids, report_xmlid)
    report = self.env.ref(report_xmlid)
    behaviour = report.behaviour()[report.id]
    printer = behaviour['printer']
    if not printer:
        raise Warning(_('No printer assigned'))
    try:
        printer.print_document(report, document, 'text')
    except UnicodeEncodeError, e:
        raise e
    except:
        raise Warning(_('Printer unavailable'))


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def print_product_label(self):
        for op in self:
            if not op.picking_id.partner_id:
                raise Warning(_('No destination partner defined'))
        hw_print(self, 'specific_print.report_stock_product_label')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def print_products_label(self):
        self.pack_operation_ids.print_product_label()

    @api.one
    def print_packages_label(self, quantity=1):
        if not self.partner_id:
            raise Warning(_('No destination partner defined'))
        hw_print(self.with_context(nbr=int(quantity)),
                 'specific_print.report_stock_pick_packs_label')

    package_ids = fields.One2many(
        'stock.quant.package',
        compute='_get_package_ids',
        string='Packages')

    @api.one
    def _get_package_ids(self):
        self.package_ids = self.pack_operation_ids.mapped('package_id')
