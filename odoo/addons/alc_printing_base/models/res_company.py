# © 2018 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import unicodedata

from odoo.addons.base.models.res_company import Company


class ResCompany(Company):
    @staticmethod
    def convert_to_ascii(str_to_convert):
        """
        This method is used by label reports.

        I use the model res.company
        to have an access to this method in each report (object res_company).

        This method will replace each special character and convert
        to ascii (requested by printers).
        :param str_to_convert:
        :return: bytes
        """
        if not isinstance(str_to_convert, str):
            str_to_convert = ""
        return unicodedata.normalize("NFKD", str_to_convert).encode("ascii", "ignore")
