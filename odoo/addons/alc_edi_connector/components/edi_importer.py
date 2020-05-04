# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class EdiImporter(AbstractComponent):
    """ Synchronizer for importing data from a backend to Odoo """

    _name = "edi.importer"
    _inherit = ["edi.synchronizer", "base.importer"]

    def execute(self):
        raise NotImplementedError()
