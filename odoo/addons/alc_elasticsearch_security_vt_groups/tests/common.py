# Copyright 2022 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.alc_elasticsearch_security.tests.common import TestESRoles


class TestESRolesVTGroups(TestESRoles):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.vt_group = cls.env["veterinary.group"].create({"name": "Bons vétos"})
