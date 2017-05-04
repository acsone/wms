# -*- coding: utf-8 -*-
import importlib
import logging

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home

from ..tools.domain_interface import Parameters, HEADER_LABELS

_logger = logging.getLogger(__name__)


class Zetes(Home):
    @http.route('/zetes',
                type='http',
                methods=['POST'],
                auth='none',
                website=True,
                csrf=False)
    def wrapper(self, **kw):
        cmd = request.httprequest.data

        _logger.info('Command: ' + cmd)

        # For all requests Zetes sends an extra comma.
        # We need to remove this comma before split the request
        params = cmd[:-1].split(',')
        # Split the request in two parts (header and values)
        header = params[:len(HEADER_LABELS)]
        values = params[len(HEADER_LABELS):]

        # Retrieve the command and the the domain
        # The msgType (command + domain) is always the fourth element
        # e.g: 208030828,2.2.3,3iV_101,REQU_ITEMPICK,30
        # In this case the msgType is REQU_ITEMPICK
        # command: requ
        # domain: itempick
        command, domain = header[3].split('_')

        # Create the handler
        # If the domain is itempick the module name will be
        # openerp.addons.specific_zetes.tools.domain_itempick
        module_name = \
            'openerp.addons.specific_zetes.tools.domain_{}'.format(
                domain.lower())
        # Retrieve the class inherited from DomainInterface
        # e.g: domain == 'itempick' => Create an instance of Itempick(header)
        module_obj = importlib.import_module(module_name)
        instance = getattr(module_obj, domain.title())(header)

        # Create the parameter instance with all values received in the request
        parameter_obj = Parameters(instance,
                                   action=command.upper(),
                                   values=values)
        # Execute the the method
        # e.g: if the msgType is REQU_ITEMPICK
        # domain: itempick
        # action: requ
        # We will execute the method requ on an instance of Itempick
        result = getattr(instance, command.lower())(parameter_obj)

        # If the method return something (action REQU)
        if result and isinstance(result, str):
            # Add a # and two break line to respect Zetes requirement
            _logger.info('Result: ' + result)
            result += '#\n\n'
        # If the method return nothing (action RESU)
        else:
            result = ''

        mimetype = 'text/plain'

        return request.make_response(result, [('Content-Type', mimetype)])

    @http.route('/display_values', type='http',
                auth="public", website=True)
    def display_values(self, **kwargs):
        result = ''

        domains_str = kwargs.get('domains')
        if domains_str:
            domains = domains_str.split(',')
        else:
            domains = ['assignment', 'catchweight', 'itempick',
                       'location', 'refdata', 'usercontext']

        actions_str = kwargs.get('actions')
        if actions_str:
            actions = actions_str.split(',')
        else:
            actions = ['requ', 'resp', 'resu']

        for domain in domains:
            module_name = \
                'openerp.addons.specific_zetes.tools.domain_{}'.format(
                    domain.lower())
            module_obj = importlib.import_module(module_name)
            instance = getattr(module_obj, domain.title())([1, 1, 1, 1, 1])

            for action in actions:
                parameter_obj = Parameters(instance, action=action.upper())
                result += '\n' + str(parameter_obj)

        return result
