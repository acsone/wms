# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleService(Component):
    _inherit = "shopinvader.sale.service"

    def _get_base_search_domain(self):
        # pop shopinvader_backend_id from normalized domain
        # very touchy hack since we expect that the domain is normalized
        # with all criteria linked with AND operator
        domain = super(SaleService, self)._get_base_search_domain()
        domain = [d for d in domain[1:] if d[0] != "shopinvader_backend_id"]
        return domain
