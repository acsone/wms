# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import psycopg2
import logging
import traceback

from odoo import api, models

from ..tools import convert_tools

_logger = logging.getLogger(__name__)


class ImportModel(models.AbstractModel):
    _name = 'import.model'
    delimiter = ';'

    columns_mapping = {}

    @api.multi
    def init_csv_file(self, file_path, import_file_id):
        """
        Import initialization
        1. Create the main import logger
        2. Vacuum the import table
        3. Copy the CSV into the import table
        :param file_path: str - The path to the file to import
        :param import_file_id: int - the import file ID
        :return: int - the logger id for this import
        """
        logger = self.env['import.logger'].create({
            'name': self._description or self._name,
            'file': file_path,
            'state': 'progress',
            'import_file_id': import_file_id,
        })
        self.env.cr.commit()

        try:
            self.env.cr.execute('TRUNCATE %s; ALTER SEQUENCE %s '
                                'RESTART WITH 2;' %
                                (self._table, self._table + '_id_seq'))
        except psycopg2.Error as error:
            _logger.exception(
                'Cannot truncate the table %s\n%s' % (self._table, error))
            logger.line_ids.create({
                'name': 'Cannot truncate the table %s' % self._table,
                'level': 'error',
                'traceback': traceback.format_exc()
            })
            return False

        try:
            convert_tools.convert_to_uft_8(file_path)
        except:
            _logger.exception(
                'Cannot convert the file to UTF-8')
            logger.line_ids.create({
                'name': 'Cannot convert the file to UTF-8' % self._table,
                'level': 'error',
                'traceback': traceback.format_exc()
            })
            return False

        with open(file_path, 'r') as file:
            first_line = file.readline()
            first_line = first_line.replace('\r', '').replace('\n', '')

            file_columns = []
            for column in first_line.split(self.delimiter):
                # If the CSV contains text delimiter we need to remote it
                if column[0] == '"' and column[-1] == '"':
                    column = column[1:][:-1]
                file_columns.append(column)

            missing_columns = [mis_column for mis_column in file_columns if
                               mis_column not in self.columns_mapping]
            if missing_columns:
                logger.line_ids.create({
                    'level': 'error',
                    'name': 'There are new columns in the file: %s' %
                            ', '.join(missing_columns),
                    'logger_id': logger.id
                })
                return False

            odoo_columns = [self.columns_mapping[odoo_column] for odoo_column
                            in file_columns]

            copy_query = """
            COPY %s (%s)
            FROM STDIN
            WITH DELIMITER '%s' CSV;
            """ % (self._table, ','.join(odoo_columns), self.delimiter)

            try:
                # Copy the value of the file in the table
                self.env.cr.copy_expert(copy_query, file=file)
            except psycopg2.Error as error:
                _logger.exception('Cannot copy the file %s into %s\n%s' % (
                    file_path, self._table, error))
                logger.line_ids.create({
                    'name': 'Cannot copy the file %s into %s' % (
                        file_path, self._table),
                    'level': 'error',
                    'traceback': traceback.format_exc(),
                    'logger_id': logger.id,
                })
                return False

        self.env.cr.commit()
        return logger.id

    @api.multi
    def execute_import(self, logger_id):
        raise NotImplementedError('Please implement this method')
