# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    propagate_process_end_date_as_move_date_deadline = fields.Boolean(
        string="Propagate release channel's process end date as move date deadline",
        default=False,
        help="Check this field if you want to propagate the process end date "
        "from the release channel linked to the picking from where the release"
        "of available to promise move process has been triggered and at the origin "
        "of the execution of this route. The process end date will be used as the "
        "deadline of the new move to create.",
    )
