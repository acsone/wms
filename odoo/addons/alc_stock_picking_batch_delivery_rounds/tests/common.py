# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_picking_batch_creation.tests.common import (
    AlcClusterPickingCommonFeatures,
)


class ClusterPickingDeliveryCommonFeatures(AlcClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(ClusterPickingDeliveryCommonFeatures, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, test_queue_job_no_delay=True, mail_notrack=True
            )
        )
        cls.operator_1 = cls.env.user.copy()
        cls.operator_2 = cls.operator_1.copy()
        cls.delivery_template1 = cls.env["round.template"].create(
            {
                "name": "Unittest delivery template 1",
                "allow_cluster_picking": True,
                "operator_ids": [(4, cls.operator_1.id), (4, cls.operator_2.id)],
            }
        )
        cls.delivery_round1 = cls.env["round.instance"].create(
            {
                "template_id": cls.delivery_template1.id,
                "date": "2021-10-01",
                "time_leave_planned": 8,
                "state": "draft",
            }
        )

        cls.delivery_template2 = cls.env["round.template"].create(
            {
                "name": "Unittest delivery template 2",
                "allow_cluster_picking": True,
                "operator_ids": [(4, cls.operator_1.id)],
            }
        )
        cls.delivery_round2 = cls.env["round.instance"].create(
            {
                "template_id": cls.delivery_template2.id,
                "date": "2021-08-12",
                "time_leave_planned": 10,
                "state": "draft",
            }
        )
        cls.pick1 = cls._create_picking_pick_and_assign(
            cls.picking_type_medoc.id, priority="0", products=cls.p1 | cls.p2
        )
        cls.pick2 = cls._create_picking_pick_and_assign(
            cls.picking_type_medoc.id, products=cls.p2
        )
        cls.pick3 = cls._create_picking_pick_and_assign(
            cls.picking_type_medoc.id, priority="3", products=cls.p1 | cls.p2
        )
        cls.pick4 = cls._create_picking_pick_and_assign(
            cls.picking_type_ali.id, products=cls.p3 | cls.p4
        )
        cls.pick5 = cls._create_picking_pick_and_assign(
            cls.picking_type_ali.id, priority="3", products=cls.p4
        )
        cls.pick6 = cls._create_picking_pick_and_assign(
            cls.picking_type_ali.id, priority="0", products=cls.p3 | cls.p4
        )
        pickings = cls.pick6
        cls.delivery_round1._assign_pickings(pickings)
