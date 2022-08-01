# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestVeterinaryGroupService(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestVeterinaryGroupService, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()
        cls.VeterinaryGroup = cls.env["veterinary.group"]
        cls.group_a = cls.VeterinaryGroup.create(
            {
                "name": "group_a",
                "display_color": "#123212",
                "sequence": 10,
                "is_alcyonnaire": True,
            }
        )
        vals_partner = {"name": "P", "veterinary_group_ids": [(6, 0, cls.group_a.ids)]}
        cls.partner = cls.env["res.partner"].create(vals_partner)
        vals_group_b = {
            "name": "group_b",
            "display_color": "#123212",
            "sequence": 5,
            "is_alcyonnaire": False,
        }
        cls.group_b = cls.VeterinaryGroup.create(vals_group_b)

    # pylint: disable=method-required-super
    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

    @classmethod
    @contextmanager
    def veterinary_group_service(cls, authenticated_partner_id):
        env = cls.env(
            context=dict(
                cls.env.context, authenticated_partner_id=authenticated_partner_id,
            )
        )
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
        )
        yield work.component(usage="veterinary_groups")

    def test_no_partner_search(self):
        with self.veterinary_group_service(None) as service:
            res = service.dispatch("search")
        self.assertEqual(0, res["size"])

    def test_search(self):
        with self.veterinary_group_service(self.partner.id) as service:
            res = service.dispatch("search")
        self.assertEqual(1, res["size"])
        self.assertEqual(self.group_a.id, res["data"][0]["id"])
        self.assertEqual("group_a", res["data"][0]["name"])
        self.assertEqual(10, res["data"][0]["sequence"])
        self.assertEqual(True, res["data"][0]["is_alcyonnaire"])
        self.assertEqual("#123212", res["data"][0]["color"])

        self.partner.write({"veterinary_group_ids": [(4, self.group_b.id)]})
        with self.veterinary_group_service(self.partner.id) as service:
            res = service.dispatch("search")
        self.assertEqual(2, res["size"])
