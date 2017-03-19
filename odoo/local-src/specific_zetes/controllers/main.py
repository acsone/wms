# -*- coding: utf-8 -*-
import importlib

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home

from ..tools.domain_interface import Parameters, HEADER_LABELS


class Zetes(Home):
    @http.route('/zetes',
                type='http',
                methods=['POST'],
                auth='none',
                website=True,
                csrf=False)
    def wrapper(self, **kw):
        cmd = request.httprequest.data

        params = cmd[:-1].split(',')
        # Split the request in two parts (header and values)
        header = params[:len(HEADER_LABELS)]
        values = params[len(HEADER_LABELS):]

        # Retrieve the command and the the domain
        # e.eg: REQU_USERCONTEXT
        # command: requ
        # domain: usercontext
        command, domain = header[3].split('_')

        # Create the handler
        module_name = \
            'openerp.addons.specific_zetes.tools.domain_{}'.format(
                domain.lower())
        module = importlib.import_module(module_name)
        instance = getattr(module, domain.title())(header)

        parameter_obj = Parameters(instance,
                                   action=command.upper(),
                                   values=values)
        result = getattr(instance, command.lower())(parameter_obj)

        if result and isinstance(result, str):
            # Add a # and two break line to respect Zetes requirement
            result += '#\n\n'
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
            module = importlib.import_module(module_name)
            instance = getattr(module, domain.title())([1,1,1,1,1])

            for action in actions:
                parameter_obj = Parameters(instance, action=action.upper())
                result += '\n' + str(parameter_obj)

        return result
