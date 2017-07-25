# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
import csv
import time
import logging
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PRODUCT_ON_HAND_KEY = 'SFDTST'
PRODUCT_RESERVED_KEY = 'SFDTRE'


class ZelaproExport(models.Model):
    _name = 'zelapro.export'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    type = fields.Selection([('sql', 'SQL'), ('method', 'Method')],
                            string='Type',
                            required=True)
    sql_view = fields.Char('SQL View')
    method = fields.Char('Method')
    data_age = fields.Integer('Age of data in months (0 for unlimited)')
    file_name = fields.Char('File name', required=True)
    line_ids = fields.One2many('zelapro.export.line',
                               'zelapro_export_id',
                               string='Lines',
                               readonly=True)
    last_export = fields.Many2one('zelapro.export.line',
                                  compute='_compute_last_export',
                                  readonly=True,
                                  store=True)
    last_export_datetime = fields.Datetime('Date last export',
                                           related='last_export.date_start',
                                           readonly=True)
    last_export_state = fields.Selection(
        [('success', 'Success'),
         ('error', 'Error')],
        'State last export',
        related='last_export.state',
        readonly=True
    )

    _sql_constraints = [
        (
            'unique_export_name',
            'UNIQUE(file_name)',
            _('The file name must be unique.')
        ),
    ]

    @api.depends('line_ids')
    def _compute_last_export(self):
        for export in self:
            if export.line_ids:
                export.last_export = export.line_ids[0].id

    @api.constrains('sql_view')
    def constrains_sql_view(self):
        query = """
        SELECT table_name
        FROM INFORMATION_SCHEMA.views
        WHERE table_schema = ANY (current_schemas(FALSE)) 
        AND table_name = %s;
        """

        check_column_query = """
        SELECT 1
        FROM information_schema.columns 
        WHERE table_name = %s 
        AND column_name = 'create_date';
        """

        for export in self:
            if not export.sql_view:
                continue
            self.env.cr.execute(query, (export.sql_view, ))
            result = self.env.cr.fetchone()

            if not result:
                raise UserError(_('SQL view %s not found' % export.sql_view))

            self.env.cr.execute(check_column_query, (export.sql_view, ))
            result = self.env.cr.fetchone()
            if not result:
                raise UserError(_('The SQL view %s shoud contains the column '
                                  'create_date' % export.sql_view))

    @api.model
    def execute_all_exports(self):
        exports = self.search([])

        exports.execute_exports()

    @api.multi
    def execute_exports(self):
        """
        Execute all exports
        :return:
        """
        config_param = self.env['ir.config_parameter']

        # Retrieve the date of go live
        date_go_live_str = config_param.get_param('zelapro.date_go_live')
        date_go_live = fields.Date.from_string(date_go_live_str)
        if not date_go_live_str:
            raise UserError(_('Please define the date go live in the Zelapro '
                              'configuration before execute exports'))

        # Retrieve the path where files will be stored
        export_path = config_param.get_param('zelapro.export_path')
        if not export_path:
            raise UserError(_('Please set the export path in Zelapro config'))
        if not os.path.isdir(export_path):
            os.makedirs(export_path)

        # Retrieve the delimiter for CSV files
        delimiter = config_param.get_param('zelapro.delimiter')
        if not delimiter:
            raise UserError(_('Please set a delimiter in Zelapro config'))

        for export in self:
            _logger.info('Start export %s' % export.name)
            time_start = time.time()
            logger = export.line_ids.create({
                'zelapro_export_id': export.id,
                'date_start': fields.Datetime.now(),
            })

            try:
                fname = date.strftime(date.today(),
                                      '%Y%m%d') + '_%s' % export.file_name
                file_path = os.path.join(export_path, fname)

                # If there is a data age on this export
                # we will compute the minimum creation date according
                # the age (in months) and the GO Live.
                min_creation_date_str = None
                if export.data_age:
                    min_creation_date = date.today() - \
                                        relativedelta(months=export.data_age)
                    min_creation_date_str = \
                        fields.Date.to_string(min_creation_date)

                    # By default we take only data after the Go live
                    # It why if the date of the GO live is greater
                    # than the minimum creation date we take the date of
                    # the Go live
                    if date_go_live > min_creation_date:
                        min_creation_date_str = date_go_live_str

                if export.type == 'sql':
                    columns_query = """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                    """
                    self.env.cr.execute(columns_query, (export.sql_view, ))
                    header = [x[0].upper() for x in self.env.cr.fetchall()]
                    # Each Zelapro export should have a column create_date
                    # However we don't want to have this column in the CSV
                    header.remove('CREATE_DATE')

                    query = "SELECT %s FROM %s" % \
                            (','.join(header), export.sql_view)

                    if min_creation_date_str:
                        query += " WHERE create_date > '%s'" % \
                                 min_creation_date_str
                    self.env.cr.execute(query)

                    rows = self.env.cr.fetchall()
                elif export.type == 'method':
                    header, rows = \
                        getattr(self, export.method)(min_creation_date_str)
                else:
                    raise NotImplementedError('The export type %s is '
                                              'not implemented' % export.type)

                with open(file_path, 'wb+') as csv_file:
                    writer = csv.writer(csv_file, delimiter=str(delimiter))
                    writer.writerow(header)
                    for row in rows:
                        writer.writerow(
                            [unicode(x).encode('utf-8') for x in row]
                        )

                time_end = time.time()
                duration = time_end - time_start
                logger.write({
                    'date_end': fields.Datetime.now(),
                    'nbr_lines': len(rows),
                    'message': 'File save to %s' % file_path,
                    'duration': duration,
                })
            except Exception as e:
                _logger.error(str(e))
                logger.write({
                    'state': 'error',
                    'message': str(e)
                })

    @api.multi
    def export_cadencier(self, min_creation_date_str=None):
        """
        Export cadencier.
        This export need to retrieve some values from the ORM
        (values not reachable from SQL).

        Step 1:
        To improve the execution time we will export all other values with
        the view SQL 'zelapro_export_cadencier' (like other exports)

        Step 2:
        Retrieve all required values with the method read on product templates

        Step 3:
        Replace these values (from step 2) in the result of the query (step 1)
        :param min_creation_date_str:
        :return:
        """
        self.ensure_one()

        #############################
        # Step 1 : Execute SQL view #
        #############################
        columns_query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'zelapro_export_cadencier'
        ORDER BY ordinal_position;
        """
        self.env.cr.execute(columns_query)
        header = [x[0].upper() for x in self.env.cr.fetchall()]
        # Each Zelapro export should have a column create_date
        # However we don't want to have this column in the CSV
        header.remove('CREATE_DATE')

        query = "SELECT %s FROM zelapro_export_cadencier" % (','.join(header))

        if min_creation_date_str:
            query += " WHERE create_date > '%s'" % \
                     min_creation_date_str
        self.env.cr.execute(query)

        result = self.env.cr.fetchall()

        ########################################
        # Step 2 : Retrieve values on products #
        ########################################
        product_tmpl_ids_query = """
        SELECT DISTINCT product_tmpl_id
        FROM product_supplierinfo
        """

        if min_creation_date_str:
            product_tmpl_ids_query += " WHERE create_date > '%s'" % \
                                      (min_creation_date_str)
        self.env.cr.execute(product_tmpl_ids_query)

        product_tmpl_ids = [x[0] for x in self.env.cr.fetchall()]
        product_tmpls = self.env['product.template'].browse(product_tmpl_ids)
        product_tmpl_values = product_tmpls.read(['qty_available',
                                                   'virtual_available'])
        values_by_product = {}
        for value in product_tmpl_values:
            values_by_product[value['id']] = {
                'qty_available': value['qty_available'],
                'virtual_available': value['virtual_available'],
            }

        ################################################
        # Step 3 : Insert result from step 2 in result #
        ################################################
        header.remove('PRODUCT_TMPL_ID')
        product_on_hand_index = header.index(PRODUCT_ON_HAND_KEY)
        product_reserved_index = header.index(PRODUCT_RESERVED_KEY)

        rows = []
        for line in result:
            row = list(line)
            product_tmpl_id = int(row.pop())

            if product_tmpl_id in values_by_product:
                value = values_by_product[product_tmpl_id]
                qty_on_hand = value['qty_available']
                # Qty reserved == Qty on hand - Qty Forecast
                qty_reserved = qty_on_hand - value['virtual_available']
            else:
                qty_on_hand = qty_reserved = 0

            row[product_on_hand_index] = qty_on_hand
            row[product_reserved_index] = qty_reserved
            rows.append(row)

        return header, rows


class ZelaproExportLine(models.Model):
    _name = 'zelapro.export.line'
    _order = 'create_date DESC'
    _rec_name = 'date_start'

    zelapro_export_id = fields.Many2one('zelapro.export',
                                        string='Export',
                                        required=True)
    date_start = fields.Datetime('Date start')
    date_end = fields.Datetime('Date end')
    message = fields.Text('Message')
    nbr_lines = fields.Integer('Number of lines')
    duration = fields.Float('Duration')
    state = fields.Selection([('success', 'Success'),
                              ('error', 'Error')],
                             default='success')
