# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class ImportMapper(AbstractComponent):
    _name = "esb.import.mapper"
    _inherit = ["esb.base", "base.import.mapper"]
    _usage = "import.mapper"


class ESBImporter(AbstractComponent):

    _name = "esb.importer"
    _inherit = ["base.importer", "esb.base"]
    _usage = "record.importer"
