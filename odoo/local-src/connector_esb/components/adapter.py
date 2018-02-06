# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import json
import logging
import requests

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import ConnectorException

_logger = logging.getLogger(__name__)


class ESBWebServiceAdapter(Component):
    """ Generic adatper for ESB.

    You need to inherit from this to configure a specific end-point
    with _endpoint or or maybe _url.
    """
    _name = 'esb.webservice.adapter'
    _inherit = ['base.backend.adapter.crud', 'esb.base']
    _url = os.getenv('ODOO_ESB_WS_BASE_URL', '')
    _endpoint = ''
    _user = os.getenv('ODOO_ESB_WS_USER', '')
    _pwd = os.getenv('ODOO_ESB_WS_PWD', '')

    def _get_url(self):
        """ Construct the url for an HTTP request """
        if not self._url or not self._user:
            raise ConnectorException('Url or username not defined on adapter')
        return self._url + '/' + self._user + '/' + self._endpoint

    def _get_headers(self):
        return {'Content-Type': 'application/json',
                'Accept': 'application/json'
                }

    def create(self, values):
        """ Create a record on the external system """
        url = self._get_url()
        data = json.dumps(values)
        _logger.debug('calling POST on %s with this data %s', url, values)
        res = requests.post(url,
                            data=data,
                            headers=self._get_headers(),
                            auth=(self._user, self._pwd))
        if res.status_code == 202:
            raise ConnectorException('Error %s on POST' % (res.status_code))
        elif res.status_code == 200:
            res_data = res.json()
            if 'error' in res_data:
                raise ConnectorException('Error on POST %s' % (res_data))
        else:
            res.raise_for_status()
        return res_data

    def write(self, id_, values):
        """ Update a record on the external system """
        url = self._get_url()
        data = json.dumps(values)
        _logger.debug('calling PUT on %s with values %s', url, values)
        res = requests.put(url,
                           data=data,
                           headers=self._get_headers(),
                           auth=(self._user, self._pwd))
        if res.status_code == 202:
            raise ConnectorException('Error %s on PUT' % (res.status_code))
        elif res.status_code == 200:
            res_data = res.json()
            if 'error' in res_data:
                raise ConnectorException('Error on PUT %s' % (res_data))
        else:
            res.raise_for_status()
        return res_data
