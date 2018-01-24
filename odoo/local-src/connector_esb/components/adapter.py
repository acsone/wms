# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ESBWebServiceAdapter(Component):
    _name = 'esb.webservice.adapter'
    _inherit = ['base.backend.adapter.crud', 'esb.base']

    def create(self, values):
        """ Create a record on the external system """
        # TODO implement requests.post on their ESB
        # url = self.backend_record.web_service_url
        url = 'http://example.com'
        _logger.info('calling POST on %s with values %s', url, values)
        # TODO raise an error if we get a code 202, the exception must
        # include the detail of the error
        return {
            "erp_id": "42",
            "increment_id": "1000000348",
            "lines": [
                {"line_number": 10, "created_id": 106},
                {"line_number": 20, "created_id": 107},
            ]
        }

    # is id_ required?
    def write(self, id_, values):
        """ Create a record on the external system """
        # TODO implement requests.put on their ESB
        # url = self.backend_record.web_service_url
        url = 'http://example.com'
        _logger.info('calling PUT on %s with values %s', url, values)
        # TODO raise an error if we get a code 202, the exception must
        # include the detail of the error
