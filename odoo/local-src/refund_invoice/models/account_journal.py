# -*- coding: utf-8 -*-
# Copyright 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(selection_add=[
        ('sale_refund', 'Sale refund'),
        ('purchase_refund', 'Purchase refund')])
