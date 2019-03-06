# -*- coding: utf-8 -*-
# © 2018 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import unicodedata

from odoo import models


class ResCompany(models.Model):
    _inherit = 'res.company'

    @staticmethod
    def convert_to_ascii(str_to_convert):
        """
        This method is used by label reports. I use the model res.company
        to have an access to this method in each report (object res_company).

        This method will replace each special character and convert
        to ascii (requested by printers).
        :param str_to_convert:
        :return:
        """
        if not isinstance(str_to_convert, unicode):
            str.decode('uft-8')

        return unicodedata.normalize('NFKD', str_to_convert).encode(
            'ascii', 'ignore'
        )
