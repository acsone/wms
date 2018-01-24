# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SaleExportMapper(Component):
    _name = 'esb.sale.order.export.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'sale.order'

    direct = [
        ('name', 'name')
    ]

    @mapping
    def compute_stuff(self, record):
        # TODO
        pass


class SaleWebServiceExporter(Component):

    _name = 'esb.sale.order.webservice.exporter'
    _inherit = 'esb.webservice.exporter'
    _apply_on = 'sale.order'

    def _get_external_id(self):
        """Return the id for the export

        To implement in subclasses. For instance for a sales order, the
        external id is sale.esb_ref.
        """
        return self.record.esb_ref

    def _postprocess_create_result(self, result):
        """Write locally the ids of the export record

        The response of the ESB webservice should be:

         {"erp_id": "42",
          "increment_id": "1000000348",
          "lines": [
              {"line_number": 10 , "created_id": 106},
              {"line_number": 20 , "created_id": 107},
          ]
         }

        """
        external_id = result['increment_id']
        self.record.with_context(no_connector_export=True).write({
            'esb_ref': external_id
        })
        # TODO write external ids of the lines in the odoo lines
