# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.web.models import ir_http


class Http(ir_http.Http):
    def session_info(self):
        info = super().session_info()
        # field required by newpharma ...
        info["session_id"] = request.session.sid
        return info
