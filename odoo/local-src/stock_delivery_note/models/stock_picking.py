# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import unicodecsv as csv

from io import BytesIO
from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        result = super(StockPicking, self).do_new_transfer()
        picking_type_out = self.env.ref('stock.picking_type_out')
        for r in self:
            if r.picking_type_id == picking_type_out:
                r._save_delivery_note(r._generate_delivery_note())
        return result

    @api.multi
    def _save_delivery_note(self, lines):
        """Save the delivery note in csv format in ir.attachment"""
        self.ensure_one()
        file_data = BytesIO()
        w = csv.writer(file_data, delimiter=';', encoding='utf-8')
        for line in lines:
            w.writerow(line)
        data = file_data.getvalue()
        filename = '_'.join([
            'NE',
            str(self.partner_id.id),
            str(self.id),
            ''.join(self.create_date[:10].split('-')),
            ''.join(self.create_date[-8:].split(':')),
            ]) + '.csv'
        existing = self.env['ir.attachment'].search([('name', '=', filename)])
        if len(existing):
            existing[0].db_datas = data.encode('base_64')
        else:
            self.env['ir.attachment'].create({
                'type': 'binary',
                'res_model': 'stock.picking',
                'res_id': self.id,
                'name': filename,
                'datas_fname': filename,
                'mimetype': 'text/csv',
                'db_datas': data.encode('base_64')
            })

    @api.multi
    def _generate_delivery_note(self):
        """ Generate the data for a delivery note when a stock pick is validated.

        It is a peculiar csv file because it does not have the same fields
        on each line, is structure is as folllow:

        1: Id (name of picking); email customer
        2: name customer; street customer; zip + city; country
        Next lines are the details of what is send one line by stock moves:
            Product esb_ref
            Product name
            Product qty
            Net price without VAT
            Crude price without VAT
            Vat rate ?
            Lot ids
            Use dates
            Suite name ?

        """
        self.ensure_one()
        lines = []
        partner = self.partner_id
        lines.append([
            self.name,
            partner.email if partner.email else '',
            ])
        lines.append([
            partner.name if partner.name else '',
            partner.street if partner.street else '',
            (partner.zip + ' ' if partner.zip else ''
             + partner.city if partner.city else ''),
            partner.country_id.name if partner.country_id else '',
            ])
        for move in self.move_lines:
            product = move.product_id
            sol = move.procurement_id.sale_line_id
            quants = move.quant_ids | move.reserved_quant_ids
            # Get the use dates in format dd-mm-yyyy
            use_date = [ld[:10] for ld in quants.mapped('life_date') if ld]
            use_date = [ld[-2:] + ld[4:8] + ld[:4] for ld in use_date]
            use_date = '/'.join(use_date)
            lines.append([
                product.default_code if product.default_code else '',
                product.name,
                str(sum(quants.mapped('qty'))),
                #  Net HTVA price
                str(sol.price_reduce),
                #  Brut HTVA price
                str(sol.price_unit),
                #  VAT rate ? First tax, all taxes, waiting for an answer
                str(sol.tax_id[0].amount) if len(sol.tax_id) else '0',
                ' / '.join([str(l.id) for l in quants.mapped('lot_id')]),
                use_date,
                'no suite',
                ]
            )
            return lines
