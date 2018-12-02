# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import unicodecsv as csv

from io import BytesIO
from odoo import api, models
from odoo.tools import config


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        result = super(StockPicking, self).do_transfer()
        picking_type_out = self.env.ref('stock.picking_type_out')
        if self.env.context.get('skip_pdf_gen'):
            return result
        for r in self:
            if r.picking_type_id == picking_type_out:
                r._save_delivery_note()
        return result

    @api.multi
    def _get_delivery_note_filename(self):
        """Return the delivery note filename."""
        self.ensure_one()
        return '_'.join([
            'NE',
            self.partner_id.ref or '',
            str(self.id),
            ''.join(self.date_done[:10].split('-')),
            ''.join(self.date_done[-8:].split(':')),
            ]) + '.csv'

    def _save_delivery_note(self):
        """Save the delivery note in csv format in ir.attachment"""
        self.ensure_one()
        file_data = BytesIO()
        w = csv.writer(file_data, delimiter=';', encoding='utf-8')
        for line in self._generate_delivery_note():
            w.writerow(line)
        data = file_data.getvalue()

        filename = self._get_delivery_note_filename()
        existing = self.env['ir.attachment'].search([('name', '=', filename)])
        if len(existing):
            existing[0].datas = data.encode('base_64')
        else:
            existing = self.env['ir.attachment'].create({
                'type': 'binary',
                'res_model': 'stock.picking',
                'res_id': self.id,
                'name': filename,
                'datas_fname': filename,
                'mimetype': 'text/csv',
                'datas': data.encode('base_64')
            })

        # send by email
        if config['test_enable']:
            return
        template = self.env.ref('stock_delivery_note.delivery_note_csv')
        values = template.generate_email(self.id)
        values['recipient_ids'] = [
            (4, pid) for pid in values.get('partner_ids', list())]
        if 'email_from' in values and not values.get('email_from'):
            values.pop('email_from')
        values['attachment_ids'] = [(6, 0, existing[0].ids)]
        mail = self.env['mail.mail'].create(values)
        mail.send(raise_exception=True)

    @api.multi
    def _generate_delivery_note(self):
        """ Generate the data for a delivery note when a stock pick is validated.

        It is a peculiar csv file because it does not have the same fields
        on each line, is structure is as folllow:

        1: Id (name of picking); email customer
        2: name customer; street customer; zip + city; country
        Next lines are the details of what is send one line by stock moves:
            Product esb_ref (default_code)
            Product name
            Product qty
            Net price without VAT
            Crude price without VAT
            Vat rate
            Lot ids
            Use dates
            Suite name

        """
        def format_number(number, fractional_size=None):
            """Format a number to a string.

            The number is formated separating the decimal and fractional part
            with a comma. With between 1 and 3 number after the comma.
            """
            if fractional_size == 1:
                formater = '{:.1f}'
            elif fractional_size == 2:
                formater = '{:.2f}'
            elif fractional_size == 3:
                formater = '{:.3f}'
            else:
                formater = '{}'
            s = formater.format(number)
            return ','.join(s.split('.'))

        self.ensure_one()
        lines = []
        partner = self.partner_id
        # The two header lines
        lines.append([
            self.id,
            partner.email or '',
            ])
        lines.append([
            u'{} {}'.format(partner.title.shortcut or '',
                            partner.name or '').strip(),
            partner.street or '',
            u'{} {}'.format(partner.zip or '', partner.city or '').strip(),
            partner.country_id.name or '',
            ])
        # The product lines
        for move in self.move_lines:
            product = move.product_id
            sol = move.procurement_id.sale_line_id
            quants = move.quant_ids | move.reserved_quant_ids
            # Get the use dates in format dd-mm-yyyy
            use_date = [ld[:10] for ld in quants.mapped('life_date') if ld]
            use_date = [ld[-2:] + ld[4:8] + ld[:4] for ld in use_date]
            use_date = '/'.join(use_date)
            lines.append([
                product.default_code or '',
                product.name,
                # Quantity computed from the quants
                format_number(sum(quants.mapped('qty')), 3),
                #  Net HTVA price
                format_number(sol.price_reduce, 2),
                #  Brut HTVA price
                format_number(sol.price_unit, 2),
                #  VAT rate, yes only the first one if present
                format_number(sol.tax_id[0].amount if sol.tax_id else 0, 1),
                # Lots name
                '/'.join(quants.mapped('lot_id.name')),
                use_date,
                sol.order_id.suite_name or '',
                ]
            )
        return lines
