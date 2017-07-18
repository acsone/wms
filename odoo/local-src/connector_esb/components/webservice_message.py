# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class WebserviceMessage(AbstractComponent):

    _name = 'esb.webservice.message.base'
    _inherit = ['esb.base']

    def _produce_xml(self, data, list_item_el=None):
        producer = self.component(usage='xml.webservice.producer')
        return producer.produce(data, list_item_el=list_item_el)

    def get_message(self, *args, **kwargs):
        raise NotImplementedError
