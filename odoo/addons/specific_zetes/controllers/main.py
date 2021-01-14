# -*- coding: utf-8 -*-
import importlib
import logging

from odoo import SUPERUSER_ID, http
from odoo.http import request

from odoo.addons.web.controllers.main import Home

from .. import constants
from ..tools.domain_interface import Parameters, Savepoint

_logger = logging.getLogger(__name__)


class Zetes(Home):
    """Publish endpoint called by Zetes.

    Example of curl request::

        curl -i -X POST \
        -H "Content-Type:text/plain" \
        -d \
        '6217065310,2.2.3,3iV_101,REQU_ITEMPICK,91,1,20181205,110043,9143439458843589,27013,,,,1,0,,,,,,,,,,1,301828_3897,736,0,,04,,,,' \
        'http://localhost/zetes'

    """

    def _sudo_zetes(self):
        # The request comes from a public user without permissions.
        # The request will be executed as zetes user.
        zetes_user = request.env(user=SUPERUSER_ID).ref("specific_zetes.user_zetes")
        request.uid = zetes_user.id

    @http.route(
        "/zetes", type="http", methods=["POST"], auth="none", website=True, csrf=False
    )
    def wrapper(self, **kw):
        cmd = request.httprequest.data

        _logger.info("Command: " + cmd)

        # For all requests Zetes sends an extra comma.
        # We need to remove this comma before split the request
        params = cmd[:-1].split(",")
        # Split the request in two parts (header and values)
        header = params[: len(constants.HEADER_LABELS)]
        values = params[len(constants.HEADER_LABELS) :]

        # Retrieve the command and the the domain
        # The msgType (command + domain) is always the fourth element
        # e.g: 208030828,2.2.3,3iV_101,REQU_ITEMPICK,30
        # In this case the msgType is REQU_ITEMPICK
        # command: requ
        # domain: itempick
        command, domain = header[constants.METHOD_INDEX].split("_")

        # Create the handler
        # If the domain is itempick the module name will be
        # openerp.addons.specific_zetes.tools.domain_itempick
        module_name = "odoo.addons.specific_zetes.tools.domain_{}".format(
            domain.lower()
        )

        self._sudo_zetes()
        # Retrieve the class inherited from DomainInterface
        # e.g: domain == 'itempick' => Create an instance of Itempick(header)
        module_obj = importlib.import_module(module_name)
        with Savepoint(request.env.cr) as savepoint:
            domain_cls = getattr(module_obj, domain.title())
            instance = domain_cls(header, savepoint)

            # Create the parameter instance with all values received in the
            # request
            parameter_obj = Parameters(instance, action=command.upper(), values=values)
            # Execute the the method
            # e.g: if the msgType is REQU_ITEMPICK
            # domain: itempick
            # action: requ
            # We will execute the method requ on an instance of Itempick
            result = getattr(instance, command.lower())(parameter_obj)

        # If the method return something (action REQU)
        if result and isinstance(result, str):
            # Add a # and two break line to respect Zetes requirement
            _logger.info("Result: " + result)
            result += "#\n\n"
        # If the method return nothing (action RESU)
        else:
            result = ""

        mimetype = "text/plain"

        return request.make_response(result, [("Content-Type", mimetype)])

    # TODO This method is only for TESTS but don't remove it.
    @http.route("/display_values", type="http", auth="public", website=True)
    def display_values(self, **kwargs):
        """
        !!! This method is only for development/test !!!
        This route will return the right format for one or more methods.
        You can pass two parameters to your request:
        - domains: Select one or more domain (assignment, catchweight, ...)
        - actions: Select one or more actions (requ, resp, resu)

        If there is not value for domain and/or actions all values
        will be taken.

        E.g: If I want to have all actions for the domain catchweight:
        /display_values?domains=catchweight

        If I want to have the action resp and resu for the domain itempick
        /display_values?domains=itempick&actions=resp,resu
        :param kwargs:
        :return:
        """
        result = ""

        domains_str = kwargs.get("domains")
        if domains_str:
            domains = domains_str.split(",")
        else:
            domains = [domain[0] for domain in constants.ZETES_DOMAINS]

        actions_str = kwargs.get("actions")
        if actions_str:
            actions = actions_str.split(",")
        else:
            actions = [action[0] for action in constants.ZETES_ACTIONS]

        self._sudo_zetes()
        for domain in domains:
            module_name = "odoo.addons.specific_zetes.tools.domain_{}".format(
                domain.lower()
            )
            module_obj = importlib.import_module(module_name)

            # Create an instance of the domain and call the method _init_
            # A domain (like Print) need a header to create an instance
            # because the _init_ of the domain will try to retrieve
            # the current user (=> picker).
            #
            # E.G.: My domain is print
            # instance = getattr(module_obj, domain.title())
            # => instance = getattr(domain_assignement, 'Print')[1,1,1,1,1]
            # => instance = Print([1,1,1,1,1])
            # In this case the system will try to retrive the user
            # with the code 1 (see USER_INDEX)
            with Savepoint(request.env.cr) as savepoint:
                domain_cls = getattr(module_obj, domain.title())
                instance = domain_cls([1, 1, 1, 1, 1], savepoint)

                for action in actions:
                    parameter_obj = Parameters(instance, action=action.upper())
                    result += "\n" + str(parameter_obj)

        return result
