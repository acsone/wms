# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Create optimization resources")
    env = api.Environment(cr, SUPERUSER_ID, {})
    AlcDeliveryResource = env["alc.delivery.resource"]
    resource_by_resource_id = {}
    for (
        resource_id,
        _,
    ) in AlcDeliveryResource._selection_geo_optimization_resource_id():
        resource = AlcDeliveryResource.create(
            {"geo_optimization_resource_id": resource_id}
        )
        resource_by_resource_id[resource_id] = resource

    _logger.info("Update round template")
    cr.execute(
        """INSERT INTO alc_delivery_resource_round_template_rel (round_template_id, alc_delivery_resource_id)
SELECT t.id,
       r.id
FROM round_template t
JOIN alc_delivery_resource r ON r.geo_optimization_resource_id = t.geo_optimization_resource_id"""
    )
    _logger.info("%d round template updated", cr.rowcount)
    _logger.info("Update round instance")
    cr.execute(
        """INSERT INTO alc_delivery_resource_round_instance_rel (round_instance_id, alc_delivery_resource_id)
    SELECT t.id,
           r.id
    FROM round_instance t
    JOIN alc_delivery_resource r ON r.geo_optimization_resource_id = t.geo_optimization_resource_id"""
    )
    _logger.info("%d round instance updated", cr.rowcount)
