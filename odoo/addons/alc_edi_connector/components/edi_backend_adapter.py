# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class EdiBackendAdapter(AbstractComponent):
    _name = "edi.backend.adapter"
    _inherit = ["base.backend.adapter", "edi.base"]

    def push(self, content):
        raise NotImplementedError()

    def pull(self):
        raise NotImplementedError()

    def test_connection(self):
        raise NotImplementedError()
