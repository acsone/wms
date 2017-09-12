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

# Cadencier export keys
PRODUCT_INDEX_KEY = 'SFDNLI'
PRODUCT_ON_HAND_KEY = 'SFDTST'
PRODUCT_BO_QTY_KEY = 'SFDTBO'
PRODUCT_RESERVED_KEY = 'SFDTRE'
ACCESSORY_SUPPLIER_KEY = 'SFASUA'
ACCESSORY_LINE_NO_KEY = 'SFANLA'
MAIN_PRODUCT_SUPPLIER_KEY = 'SFASUP'
MAIN_PRODUCT_LINE_NO_KEY = 'SFANLP'

# Lots export keys
PRODUCT_QTY_ON_LOT_KEY = 'LOTACT'


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
        'Last export state',
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
                raise UserError(_('The SQL view %s should contain the column '
                                  'create_date') % export.sql_view)

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
                        getattr(export, export.method)(min_creation_date_str)
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
                    'message': 'File saved to %s' % file_path,
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
                                                  'virtual_available',
                                                  'immediately_usable_qty',
                                                  'additional_product_id'])
        values_by_product = {}
        for value in product_tmpl_values:
            values_by_product[value['id']] = {
                'qty_available': value['qty_available'],
                'virtual_available': value['virtual_available'],
                'immediately_usable_qty': value['immediately_usable_qty'],
                'additional_product_id': value['additional_product_id'],
            }

        ################################################
        # Step 3 : Insert result from step 2 in result #
        ################################################
        header.remove('PRODUCT_TMPL_ID')
        product_index_index = header.index(PRODUCT_INDEX_KEY)
        product_on_hand_index = header.index(PRODUCT_ON_HAND_KEY)
        product_bo_qty_index = header.index(PRODUCT_BO_QTY_KEY)
        product_reserved_index = header.index(PRODUCT_RESERVED_KEY)
        accessory_supplier_index = header.index(ACCESSORY_SUPPLIER_KEY)
        accessory_line_no_index = header.index(ACCESSORY_LINE_NO_KEY)
        main_product_supplier_index = header.index(MAIN_PRODUCT_SUPPLIER_KEY)
        main_product_line_no_index = header.index(MAIN_PRODUCT_LINE_NO_KEY)

        rows = []
        previous_supplier = None
        for line in result:
            row = list(line)
            product_tmpl_id = int(row.pop())

            # The product_index is a way to order products in the CSV file.
            # The first column of the CSV is the supplier ID.
            # It allow Zetes to order by supplier. Moreover we want to
            # order products (by supplier) to have main product followed
            # by his additional product (if needed).
            # E.G:
            # Supplier 42 with 3 products and 1 additional product
            # for the product 2.
            # 1 | 10 | Product 1
            # 1 | 20 | Product 2
            # 1 | 21 | Additional product <== Look the index 21
            # 1 | 30 | Product 3
            supplier_id = row[0]
            if supplier_id != previous_supplier:
                product_index = 10
                previous_supplier = supplier_id
            else:
                product_index += 10

            additional_product_id = None
            qty_on_hand = qty_reserved = qty_bo = 0
            additional_product_index = additional_product_supplier = 0
            if product_tmpl_id in values_by_product:
                value = values_by_product[product_tmpl_id]
                qty_on_hand = value['qty_available']
                # Qty reserved == Qty on hand - Qty Forecast
                qty_reserved = qty_on_hand - value['virtual_available']

                additional_product_id = value['additional_product_id']
                if additional_product_id:
                    additional_product_index = product_index + 1
                    additional_product_supplier = supplier_id

                # Compute the qty in BO for this product
                # Take the value of "Qty available"
                # If the value is less than zero, it means that
                qty_available = value['immediately_usable_qty']
                if qty_available >= 0:
                    qty_bo = 0
                else:
                    qty_bo = qty_available * -1

            row[product_index_index] = product_index
            row[product_on_hand_index] = qty_on_hand
            row[product_reserved_index] = qty_reserved
            row[product_bo_qty_index] = qty_bo
            row[accessory_supplier_index] = additional_product_supplier
            row[accessory_line_no_index] = additional_product_index
            row[main_product_supplier_index] = 0  # Set this column only for
            # Additional product
            row[main_product_line_no_index] = 0  # Set this column only for
            # Additional product
            rows.append(row)

            # If this product has a additional product, we need to add a new
            # list just after the main product.
            # Steps:
            # 3.1: If the product has an additional product, we will execute
            # the view to search data about the additional product
            # 3.2: If the additional product is linked to the supplier of the
            # main product (it means that there is a line in supplier info),
            # we will create a new line
            # 3.3: Search in Odoo for additional information on
            # the additional product
            # 3.4: Add this new line in result
            if additional_product_id:
                # Step 3.1
                data_query = """
                SELECT *
                FROM zelapro_export_cadencier
                WHERE zelapro_export_cadencier.SFDART = (
                    SELECT default_code
                    FROM product_template
                    WHERE id = %s
                  )
                AND zelapro_export_cadencier.SFDSUI = %s;
                """
                self.env.cr.execute(data_query, (additional_product_id,
                                                 supplier_id))
                result = self.env.cr.fetchone()

                if result:
                    # Step 3.2
                    add_row = list(line)
                    # Remove create_date
                    row.pop()
                    add_product_tmpl_id = int(row.pop())

                    add_product_index = product_index + 1

                    # Step 3.3
                    add_product_tmpl = self.env['product.template'].browse(
                        add_product_tmpl_id
                    )
                    add_product_tmpl_values = \
                        add_product_tmpl.read(['qty_available',
                                               'virtual_available',
                                               'immediately_usable_qty',
                                               'additional_product_id'])
                    add_values = add_product_tmpl_values[0]

                    add_qty_on_hand = add_values['qty_available']
                    # Qty reserved == Qty on hand - Qty Forecast
                    add_qty_reserved = \
                        add_qty_on_hand - add_values['virtual_available']

                    # Compute the qty in BO for this product
                    # Take the value of "Qty available"
                    # If the value is less than zero, it means that
                    add_qty_available = add_values['immediately_usable_qty']
                    if add_qty_available >= 0:
                        add_qty_bo = 0
                    else:
                        add_qty_bo = add_qty_available * -1

                    add_row[product_index_index] = add_product_index
                    add_row[product_on_hand_index] = add_qty_on_hand
                    add_row[product_reserved_index] = add_qty_reserved
                    add_row[product_bo_qty_index] = add_qty_bo
                    # Set this column only for main product
                    add_row[accessory_supplier_index] = 0
                    # Set this column only for main product
                    add_row[accessory_line_no_index] = 0
                    add_row[main_product_supplier_index] = supplier_id
                    add_row[main_product_line_no_index] = product_index

                    # Step 3.4
                    rows.append(add_row)

        return header, rows

    @api.multi
    def export_lots(self, min_creation_date_str=None):
        """
        Export lots.
        This export need to retrieve some values from the ORM
        (values not reachable from SQL).

        Step 1:
        To improve the execution time we will export all other values with
        the view SQL 'zelapro_export_lots' (like other exports)

        Step 2:
        Retrieve all required values with the method read on lot

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
                WHERE table_name = 'zelapro_export_lots'
                ORDER BY ordinal_position;
                """
        self.env.cr.execute(columns_query)
        header = [x[0].upper() for x in self.env.cr.fetchall()]
        # Each Zelapro export should have a column create_date
        # However we don't want to have this column in the CSV
        header.remove('CREATE_DATE')

        query = "SELECT %s FROM zelapro_export_lots" % (','.join(header))

        if min_creation_date_str:
            query += " WHERE create_date > '%s'" % \
                     min_creation_date_str
        self.env.cr.execute(query)

        result = self.env.cr.fetchall()

        ####################################
        # Step 2 : Retrieve values on lots #
        ####################################
        domain = [('is_archived', '=', False)]

        if min_creation_date_str:
            domain.append(('creation_date', '>', min_creation_date_str))
        lots = self.env['stock.production.lot'].search(domain)
        lot_values = lots.read(['product_qty'])

        values_by_lot = {}
        for value in lot_values:
            values_by_lot[value['id']] = {
                'product_qty': value['product_qty'],
            }

        ################################################
        # Step 3 : Insert result from step 2 in result #
        ################################################
        header.remove('LOT_ID')
        product_qty_on_lot = header.index(PRODUCT_QTY_ON_LOT_KEY)

        rows = []
        for line in result:
            row = list(line)
            lot_id = int(row.pop())

            if lot_id in values_by_lot:
                value = values_by_lot[lot_id]
                product_qty = value['product_qty']
            else:
                product_qty = 0

            row[product_qty_on_lot] = product_qty
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
