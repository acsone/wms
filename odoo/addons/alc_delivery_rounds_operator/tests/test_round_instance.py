# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestRoundInstance(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestRoundInstance, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.operator_1 = cls.env.user.copy()
        cls.operator_2 = cls.operator_1.copy()
        cls.operators = cls.operator_2 | cls.operator_1
        cls.delivery_template = cls.env["round.template"].create(
            {
                "name": "Unittest delivery template",
                "operator_ids": [(6, 0, cls.operators.ids)],
            }
        )

    def test_00(self):
        """
            Data:
                A round template with 2 operators
            Test case:
                Create a delivery instance for the template
            Expected result:
                operator_ids are filled from the template into the instance
        """
        round_instance = self.env["round.instance"].create(
            {"template_id": self.delivery_template.id, "date": "2017-01-01"}
        )
        self.assertEqual(round_instance.operator_ids, self.operators)
