# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ElasticsearchConnectorComponent(Component):
    _inherit = "elasticsearch.se.connector"
    _record_id_key = "id"
