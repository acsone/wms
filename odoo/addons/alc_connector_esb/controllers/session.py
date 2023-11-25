# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import json

from odoo.http import JsonRPCDispatcher, request

from odoo.addons.web.controllers import session


class Session(session.Session):
    def authenticate(self, db, login, password, base_location=None):
        # newpharma is not able to rename the database name into their code
        # so we need to handle it here
        if db == "odoo-prod":
            db = "odoo"
        return super().authenticate(db, login, password, base_location)


class JsonRpc(JsonRPCDispatcher):
    def post_dispatch(self, response):
        # required by newpharama: inject session_id into the response of the authenticate method
        res = super().post_dispatch(response)
        if (
            request.httprequest.path == "/web/session/authenticate"
            and response.status_code == 200
        ):
            # inject the session_id from the cookie into the response This can only be done here
            # since the session rotation occurs into the call to super().post_dispatch() and therefore
            # after the call to the 'get_session_info' method of ir.http. As a consequence, the
            # session_id returned by the 'get_session_info' method is not the one that is actually
            # generated for the current call.
            data = response.json
            data["result"]["session_id"] = request.session.sid
            response.set_data(json.dumps(data))
        return res
