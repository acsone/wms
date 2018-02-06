# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from ..adapter import ESBWebServiceAdapter


class ESBWebServiceAdapterSaleOrder(ESBWebServiceAdapter):
    _name = 'esb.saleorder.webservice.adapter'
    _inherit = ['esb.webservice.adapter']
    _usage = 'backend.adapter.saleorder'
    _endpoint = 'sales_order'
