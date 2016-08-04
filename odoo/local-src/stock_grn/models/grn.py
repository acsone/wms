# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright (C) 2015-TODAY BCIM <http://www.bcim.be>.
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

from openerp import _, models, fields, api
from openerp.exceptions import Warning


class GRN_Type(models.Model):
    """ GRN Type """
    _name = 'stock.grn.type'

    name = fields.Char(string='Type', required=True)


class GRN(models.Model):
    """ Goods Received Note """
    _name = 'stock.grn'
    _description = 'Goods Received Note'
    _order = 'id desc'

    name = fields.Char(
        string='Name',
        copy=False,
        index=True,
        required=True,
        default='/'
    )
    carrier_id = fields.Many2one(
        'res.partner',
        string='Carrier',
        required=True)
    carrier_ref = fields.Char(string='Carrier Id')

    from_info = fields.Char(string='From')
    ref = fields.Char(string='Reference')

    # origin = fields.Char(string='Origin')
    # order_ref = fields.Char(string='Order')
    # to_info = fields.Char(string='To')

    date = fields.Datetime(
        'Date',
        required=True,
        default=lambda self: fields.Datetime.now())
    description = fields.Text('Description')
    type_id = fields.Many2one(
        'stock.grn.type',
        string='Type')
    qty_pallet = fields.Integer(string='Qty Pallets')
    qty_box = fields.Integer(string='Qty Boxes')

    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        required=True, readonly=True)

    picking_ids = fields.One2many(
        'stock.picking', 'grn_id',
        string='Incoming Shipments',
        domain=[('picking_type_code', '=', 'incoming')])

    _defaults = {
        # required to declare this way due to bug on default m2o (return id
        # instead of record)
        'company_id': lambda self, cr, uid, c:
            self.pool.get('res.company')._company_default_get(
                cr, uid, 'stock.grn', context=c),
    }

    #@api.multi
    #def name_get(self):
    #    """ Read the stored complete_name field """
    #    res = []
    #    for record in self:
    #        name = record.name
    #        if record.ref:
    #            name = '[%s] %s' % (record.ref, name)
    #        if record.origin:
    #            name = '%s (%s)' % (name, record.origin)
    #        res.append((record.id, name))
    #    return res

    #@api.model
    #def name_search(self, name='', args=None, operator='ilike', limit=100):
    #    """ Perform name search on name only """
    #    name = name.split(']')[-1]
    #    name = name.split('(')[-1]
    #    name = name.strip()
    #    return super(GRN, self).name_search(
    #        name, args=args, operator=operator, limit=limit)

    @api.multi
    def print_label(self):
        document = self.env['report']._get_raw(
            self._ids, 'stock_grn.report_grn_label')
        report = self.env.ref('stock_grn.report_grn_label')
        behaviour = report.behaviour()[report.id]
        printer = behaviour['printer']
        if not printer:
            raise Warning(_('No printer assigned'))
        try:
            printer.print_document(report, document, 'text')
        except:
            raise Warning(_('Printer unavailable'))

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.grn') or '/'
        return super(GRN, self).create(vals)
