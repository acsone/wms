# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo.fields import Command

_logger = logging.getLogger(__name__)


def _create_reserve_rule(env):
    _logger.info("Create reservation rules")

    rule_aliments = env["stock.reserve.rule"].create(
        {
            "name": "Pick Aliments",
            "sequence": 1,
            "picking_type_ids": [
                Command.set(
                    [
                        env.ref(
                            "alc_stock_picking_type_aliment.stock_picking_type_ali"
                        ).id
                    ]
                )
            ],
            "location_id": env.ref("stock.stock_location_stock").id,
        }
    )

    rule_m = env["stock.reserve.rule"].create(
        {
            "name": "Pick M",
            "sequence": 2,
            "picking_type_ids": [Command.set([24])],
            "location_id": env.ref("stock.stock_location_stock").id,
        }
    )

    rule_frigo = env["stock.reserve.rule"].create(
        {
            "name": "Pick Frigo",
            "sequence": 3,
            "picking_type_ids": [
                Command.set([env.ref("__setup__.stock_picking_type_froid").id])
            ],
            "location_id": env.ref("stock.stock_location_stock").id,
        }
    )

    rule_materiel = env["stock.reserve.rule"].create(
        {
            "name": "Pick Matériel",
            "sequence": 4,
            "picking_type_ids": [
                Command.set([env.ref("__setup__.stock_picking_type_materiel").id])
            ],
            "location_id": env.ref("stock.stock_location_stock").id,
        }
    )

    # Removal rules

    # Aliments
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Achetés/Vendus",
            "rule_id": rule_aliments.id,
            "sequence": 1,
            "location_id": env.ref("__setup__.stock_location_onorder").id,
            "removal_strategy": "default",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Pallet",
            "rule_id": rule_aliments.id,
            "sequence": 2,
            "location_id": env.ref("__setup__.stock_location_ali").id,
            "removal_strategy": "empty_bin",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Box",
            "rule_id": rule_aliments.id,
            "sequence": 3,
            "location_id": env.ref("__setup__.stock_location_ali").id,
            "removal_strategy": "packaging",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Défaut",
            "rule_id": rule_aliments.id,
            "sequence": 4,
            "location_id": env.ref("__setup__.stock_location_ali").id,
            "removal_strategy": "default",
        }
    )

    # M
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Achetés/Vendus",
            "rule_id": rule_m.id,
            "sequence": 1,
            "location_id": env.ref("__setup__.stock_location_onorder").id,
            "removal_strategy": "default",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Box",
            "rule_id": rule_m.id,
            "sequence": 2,
            "location_id": env.ref("__setup__.stock_location_medoc").id,
            "removal_strategy": "packaging",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Défaut",
            "rule_id": rule_m.id,
            "sequence": 3,
            "location_id": env.ref("__setup__.stock_location_medoc").id,
            "removal_strategy": "default",
        }
    )

    # Frigo
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Achetés/Vendus",
            "rule_id": rule_frigo.id,
            "sequence": 1,
            "location_id": env.ref("__setup__.stock_location_onorder").id,
            "removal_strategy": "default",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Box",
            "rule_id": rule_frigo.id,
            "sequence": 2,
            "location_id": env.ref("__setup__.stock_location_frigo").id,
            "removal_strategy": "packaging",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Défaut",
            "rule_id": rule_frigo.id,
            "sequence": 3,
            "location_id": env.ref("__setup__.stock_location_frigo").id,
            "removal_strategy": "default",
        }
    )

    # Matériel
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Achetés/Vendus",
            "rule_id": rule_materiel.id,
            "sequence": 1,
            "location_id": env.ref("__setup__.stock_location_onorder").id,
            "removal_strategy": "default",
        }
    )
    env["stock.reserve.rule.removal"].create(
        {
            "name": "Box",
            "rule_id": rule_materiel.id,
            "sequence": 2,
            "location_id": env.ref("__setup__.stock_location_materiel").id,
            "removal_strategy": "default",
        }
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_reserve_rule(env)
