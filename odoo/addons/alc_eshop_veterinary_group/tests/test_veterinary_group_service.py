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
        cls.VeterinaryGroup.search([]).unlink()
        cls.group_a = cls.VeterinaryGroup.create(
            {
                "name": "group_a",
                "color": "#123212",
                "sequence": 10,
                "is_alcyonnaire": True,
            }
        )

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

    def test_search(self):
        with self.veterinary_group_service(None) as service:
            res = service.dispatch("search")
        self.assertTrue(res)
        self.assertEqual(1, res.get("size"))
        self.assertEqual(self.group_a.id, res["data"][0]["id"])
