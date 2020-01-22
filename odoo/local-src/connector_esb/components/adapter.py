# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

import requests

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import (
    ConnectorException,
    RetryableJobError,
)
from simplejson.decoder import JSONDecodeError

_logger = logging.getLogger(__name__)


class ESBWebServiceAdapter(Component):
    """ Generic adapter for ESB.

    You need to inherit from this to configure a specific end-point
    with _endpoint or or maybe _url.
    """

    _name = 'esb.webservice.adapter'
    _inherit = ['base.backend.adapter.crud', 'esb.base']
    _endpoint = ''

    def _get_url(self):
        """ Construct the url for an HTTP request """
        if not (self.backend_record.ws_url and self.backend_record.ws_user):
            raise ConnectorException('Url or username not defined on adapter')
        return (
            self.backend_record.ws_url
            + '/'
            + self.backend_record.ws_user
            + '/'
            + self._endpoint
        )

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def create(self, values):
        """ Create a record on the external system """
        url = self._get_url()
        data = json.dumps(values)
        _logger.debug('calling POST on %s with this data %s', url, values)
        try:
            res = requests.post(
                url,
                data=data,
                headers=self._get_headers(),
                auth=(self.backend_record.ws_user, self.backend_record.ws_pwd),
            )
        except requests.ConnectionError:
            raise RetryableJobError(
                'Connection is not available, the job will be retried later.'
            )
        if res.status_code == 202:
            raise ConnectorException('Error %s on POST' % (res.status_code))
        elif res.status_code == 200:
            try:
                res_data = res.json()
            except JSONDecodeError:
                raise ConnectorException(
                    'Error decoding json response : %s' % (res.text)
                )
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
        try:
            res = requests.put(
                url,
                data=data,
                headers=self._get_headers(),
                auth=(self.backend_record.ws_user, self.backend_record.ws_pwd),
            )
        except requests.ConnectionError:
            raise RetryableJobError(
                'Connection is not available, the job will be retried later.',
            )
        if res.status_code == 202:
            raise ConnectorException('Error %s on PUT' % (res.status_code))
        elif res.status_code == 200:
            try:
                res_data = res.json()
            except JSONDecodeError:
                raise ConnectorException(
                    'Error decoding json response : %s' % (res.text)
                )
            if 'error' in res_data:
                raise ConnectorException('Error on PUT %s' % (res_data))
        else:
            res.raise_for_status()
        return res_data
