# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class ImportFileTest(TransactionCase):
    post_install = True
    at_install = False

    def test_get_filename_pattern(self):
        """
        Test the method get_filename_pattern
        :return:
        """
        import_obj = self.env['import.file']

        date_overwrite_str = '2017-01-31'
        date_overwrite = datetime.strptime(date_overwrite_str, '%Y-%m-%d')

        # Try a simple file (without date)
        simple_filename = 'MyFile.csv'
        result = import_obj.get_filename_pattern(
            simple_filename,
            now_overwrite=date_overwrite
        )
        self.assertEqual(result, 'MyFile.csv')

        # Try a filename with a date at the end of filename
        filename_with_date = 'MyFile_%Y_%m_%d.csv'
        result = import_obj.get_filename_pattern(
            filename_with_date,
            now_overwrite=date_overwrite
        )
        self.assertEqual(result, 'MyFile_2017_01_31.csv')

        # Try a filename with a date at the beginning of filename
        filename_with_date_2 = '%Y%m%d_MyFile.csv'
        result = import_obj.get_filename_pattern(
            filename_with_date_2,
            now_overwrite=date_overwrite
        )
        self.assertEqual(result, '20170131_MyFile.csv')

        # Try a filename with only a date
        filename_with_date = '%d/%m/%Y.csv'
        result = import_obj.get_filename_pattern(
            filename_with_date,
            now_overwrite=date_overwrite
        )
        self.assertEqual(result, '31/01/2017.csv')

        # Try a filename without extension
        wrong_filename = 'MyFile'
        with self.assertRaises(UserError):
            import_obj.get_filename_pattern(
                wrong_filename
            )

        today_filename = '%Y%m%d_MyFile.csv'
        today_str = datetime.now().strftime('%Y%m%d')
        result = import_obj.get_filename_pattern(today_filename)
        self.assertEqual(result, '%s_MyFile.csv' % today_str)
