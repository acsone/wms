# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    render_qweb_pdf_batch_size = fields.Integer(
        "Number of records per batch for rendering QWeb PDF",
        default=30,
        config_parameter="alc_report_qweb_pdf_batch.render_qweb_pdf_batch_size",
        help="Number of records per batch for rendering QWeb PDF. "
        "This field will limit the number of files pass to the "
        "wkhtmltopdf runtime at same time and therefore lower "
        "the risk of exceed of some limits",
    )
