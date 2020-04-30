# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class EdiExporter(AbstractComponent):
    """ Synchronizer for importing data from a backend to Odoo """

    _name = 'edi.exporter'
    _inherit = ['edi.synchronizer', 'base.exporter']

    def execute(self, record):
        raise NotImplementedError()
