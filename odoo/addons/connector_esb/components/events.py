# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ESBEventListener(Component):
    _name = "esb.listener"
    _inherit = ["esb.base", "base.event.listener"]
    _collection = "esb.backend"

    # def on_record_create(self, record, fields=None):
    #     print "%r has been created", record, fields
    #
    # def on_record_write(self, record, fields=None):
    #     print "%r has been updated", record, fields
