# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.web.controllers import session


class Session(session.Session):
    def authenticate(self, db, login, password, base_location=None):
        # newpharma is not able to rename the database name into their code
        # so we need to handle it here
        if db == "odoo-prod":
            db = "odoo"
        return super().authenticate(db, login, password, base_location)
