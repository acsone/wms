# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.modules.module import get_resource_path
from odoo.tests.common import TransactionCase
from shapely.geometry.polygon import Polygon


class TestShapeFileImportWizard(TransactionCase):
    def setUp(self):
        super(TestShapeFileImportWizard, self).setUp()
        self.delivery_plan = self.env["delivery.plan"].create({"name": "test"})
        self.ShapeFileImportWizard = self.env["shape.file.import.wizard"]

    def _do_import(self, shape_filename, delivery_plan_id=None):
        shape_file_path = get_resource_path(
            "alc_geo_delivery_rounds", "tests", "ressources", shape_filename
        )
        with open(shape_file_path, "rb") as f:
            content = base64.encodestring(f.read())

        delivery_plan_to_use = (
            delivery_plan_id if delivery_plan_id else self.delivery_plan.id
        )
        wizard = self.ShapeFileImportWizard.create(
            {"delivery_plan_id": delivery_plan_to_use, "shape_file": content}
        )

        wizard.execute_import()

    def test_template_creation(self):
        delivery_plan = self.env["delivery.plan"].create({"name": "test_creation"})
        self._do_import("shape_test_1.zip", delivery_plan_id=delivery_plan.id)
        template = self.env["round.template"].search(
            [("delivery_plan_id", "=", delivery_plan.id)]
        )
        created_template_name = "D1"

        # Assert Template 1 creation
        self.assertEqual(template.name, created_template_name)
        self.assertEqual(template.geo_optimization_resource_id, created_template_name)

    def test_template_update(self):
        # template 2 already exist on delivery_plan => do update
        polygon = Polygon(
            [
                [3.157493, 50.776306],
                [3.157075, 50.776594],
                [3.156601, 50.777019],
                [3.156126, 50.777434],
                [3.155595, 50.777824],
            ]
        )
        template = self.env["round.template"].create(
            {"name": "D2", "geo_polygon_shape": polygon}
        )  # No shape associated to it
        delivery_plan = self.env["delivery.plan"].create(
            {"name": "test_update", "round_template_ids": [(4, template.id)]}
        )

        self.assertFalse(template.geo_optimization_resource_id)

        self._do_import("shape_test_2.zip", delivery_plan_id=delivery_plan.id)

        # after update : shape does exists on template
        geo_shape_after = isinstance(template.geo_polygon_shape, Polygon)
        self.assertTrue(geo_shape_after)
        self.assertEqual(template.geo_optimization_resource_id, template.name)

    def test_template_deletion(self):
        # template 3 does not exist but template 1 does => delete template 1 on delivery plan
        polygon = Polygon(
            [
                [3.157493, 50.776306],
                [3.157075, 50.776594],
                [3.156601, 50.777019],
                [3.156126, 50.777434],
                [3.155595, 50.777824],
            ]
        )
        template = self.env["round.template"].create(
            {"name": "D1", "geo_polygon_shape": polygon}
        )
        delivery_plan = self.env["delivery.plan"].create(
            {"name": "test_delete", "round_template_ids": [(4, template.id)]}
        )

        self._do_import("shape_test_3.zip", delivery_plan_id=delivery_plan.id)

        # Assert D1 deleted
        templates_attached_to_delivey_plan = delivery_plan.round_template_ids
        names = [t.name for t in templates_attached_to_delivey_plan]
        is_d1_in_templates = "D1" in names
        self.assertFalse(is_d1_in_templates)
