# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
import csv
import time
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError


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
            time_start = time.time()
            logger = export.line_ids.create({
                'zelapro_export_id': export.id,
                'date_start': fields.Datetime.now(),
            })

            try:
                fname = date.strftime(date.today(),
                                      '%Y%m%d') + '_%s' % export.file_name
                file_path = os.path.join(export_path, fname)

                if export.type == 'sql':
                    columns_query = """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                    """
                    self.env.cr.execute(columns_query, (export.sql_view, ))
                    header = [x[0] for x in self.env.cr.fetchall()]
                    # Each Zelapro export should have a column create_date
                    # However we don't want to have this column in the CSV
                    header.remove('create_date')

                    query = "SELECT %s FROM %s" % \
                            (','.join(header), export.sql_view)

                    # If there is a data age on this export
                    # we will add a where close on the query
                    if export.data_age:
                        min_creation_date = \
                            date.today() - \
                            relativedelta(months=export.data_age)
                        min_creation_date_str = \
                            fields.Date.to_string(min_creation_date)

                        # By default we take only data after the Go live
                        # It why if the date of the GO live is greater
                        # than the minimum creation date we take the date of
                        # the Go live
                        if date_go_live > min_creation_date:
                            min_creation_date_str = date_go_live_str

                        query += " WHERE create_date > '%s'" % \
                                 min_creation_date_str
                    self.env.cr.execute(query)

                    rows = self.env.cr.fetchall()
                elif export.type == 'method':
                    header, rows = getattr(self, export.method)
                else:
                    raise NotImplementedError('The export type %s is '
                                              'not implemented' % export.type)

                with open(file_path, 'wb+') as csv_file:
                    writer = csv.writer(csv_file, delimiter=str(delimiter))
                    writer.writerow(header)
                    writer.writerow(rows)

                time_end = time.time()
                duration = time_end - time_start
                logger.write({
                    'date_end': fields.Datetime.now(),
                    'nbr_lines': len(rows),
                    'message': 'File save to %s' % file_path,
                    'duration': duration,
                })
            except Exception as e:
                logger.write({
                    'state': 'error',
                    'message': str(e)
                })


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
