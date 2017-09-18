# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class ImportLoggerLine(models.Model):
    _description = "Logger line for imports"
    _name = "import.logger.line"

    log_level = [
        ('stat', 'Stat'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    name = fields.Char('Message', required=True)
    level = fields.Selection(log_level, string='Level',
                             default='warning', required=True)
    logger_id = fields.Many2one('import.logger', string='Logger',
                                required=True, ondelete='cascade',
                                index=True)
    line = fields.Char('Line')
    traceback = fields.Text('Traceback')


class ImportLogger(models.Model):
    _description = "Logger for Imports"
    _name = "import.logger"
    _order = 'date_start DESC'

    LOGGER_STATE = [('progress', 'In Progress'),
                    ('success', 'Success'),
                    ('warning', 'Warning'),
                    ('skip', 'Skipped'),
                    ('error', 'Error')]

    name = fields.Char('Name', required=True)
    file = fields.Char('File', required=False)
    date_start = fields.Datetime('Date start',
                                 default=lambda self: fields.Datetime.now())
    date_end = fields.Datetime('Date end')
    line_ids = fields.One2many('import.logger.line',
                               'logger_id', string='Lines',
                               ondelete='cascade')
    import_file_id = fields.Many2one('import.file', string='File')
    state = fields.Selection(LOGGER_STATE)
    info = fields.Text('Information')
