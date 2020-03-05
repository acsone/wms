# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class EdiBBase(AbstractComponent):

    _name = 'edi.base'
    _inherit = 'base.connector'
    _collection = 'edi.backend'
