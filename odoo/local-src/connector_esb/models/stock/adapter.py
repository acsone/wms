# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from ...components.adapter import ESBWebServiceAdapter


class ESBWebServiceAdapterStockUpdate(ESBWebServiceAdapter):
    _name = 'esb.stockupdate.webservice.adapter'
    _inherit = ['esb.webservice.adapter']
    _endpoint = 'product_stock/'
    _usage = 'backend.adapter.stockupdate'
