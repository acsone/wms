#!/usr/bin/env python
import logging
import re

import click
import click_odoo

from odoo import Command

_logger = logging.getLogger(__name__)


# re to extract the floats from a string
# formatted as RFA 4,5% or RFA 2,5-5%
# for RFA 4,5% it will return (4.5, 0.0)
# for RFA 2,5-5% it will return (2.5, 5.0)
# for RFA 5% it will return (5.0, 0.0)
# for RFA 5-10% it will return (5.0, 10.0)
AMOUNT_RE = re.compile(r"RFA (\d+(?:,\d+)?)(?:-(\d+(?:,\d+)?))?%")


def get_amount_from_string(string):
    match = AMOUNT_RE.search(string)
    if match:
        amount1 = float(match.group(1).replace(",", ".")) / 100
        amount2 = (
            float(match.group(2).replace(",", ".")) / 100 if match.group(2) else 0.0
        )
        return amount1, amount2
    return (0.0, 0.0)


def _init_rfa(env):
    """Initialize the RFA (Ready For Action) process for all partners."""
    program = env.ref("__setup__.loyalty_program_rfa", raise_if_not_found=False)
    if not program:
        # the reward is without interest at this moment...
        program = env["loyalty.program"].create(
            {
                "name": "RFA 2025",
                "program_type": "year_end_rebate",
                "currency_id": env.ref("base.EUR").id,
                "trigger": "auto",
                "applies_on": "future",
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
                "beneficiary_partner_type": "invoiced_partner",
                "sale_ok": True,
                "rule_ids": [],
                "reward_ids": [
                    Command.create(
                        {
                            "reward_type": "rebate",
                            "required_points": 1,
                            "discount": 0,
                        },
                    )
                ],
                "partner_domain": '[("is_valid_vet_efficiency_member", "=", True)]',
            }
        )
        # add the xml id
        env.cr.execute(
            f"INSERT INTO ir_model_data (name, model, module, res_id) VALUES ('loyalty_program_rfa', 'loyalty.program', '__setup__', {program.id})"
        )
    if True:
        # first remove all rule_ids and partner_ids
        program.write({"rule_ids": [Command.clear()], "partner_ids": [Command.clear()]})
        rfa_vt_groups = env["veterinary.group"].search([("name", "=like", "RFA%")])
        # We write all the partners from the veterinary groups to the program
        # program.write(
        #    {"partner_ids": [Command.set(rfa_vt_groups.mapped("partner_ids").ids)]}
        # )
        partners = rfa_vt_groups.mapped("partner_ids")
        partners.is_exclusive_vet_efficiency_member = True
        partners = partners.filtered(lambda p: p.is_valid_vet_efficiency_member)

        # we create a rule for each group
        for group in rfa_vt_groups:
            amount_min, amount_max = get_amount_from_string(group.name)
            if not amount_min:
                _logger.error(f"Invalid amount for group {group.name}")
                continue
            _logger.info(
                f"Creating rule for group {group.name} with amount {amount_min} to {amount_max}"
            )
            products = group.product_template_ids.product_variant_ids
            if not products:
                _logger.error(f"No products for group {group.name}")
                continue
            program.write(
                {
                    "rule_ids": [
                        Command.create(
                            {
                                "reward_point_amount": amount_min,
                                "reward_point_max_amount": amount_max,
                                "reward_point_mode": "money",
                                "product_ids": [Command.set(products.ids)],
                                "name": group.name,
                                "sequence": group.sequence,
                            }
                        )
                    ]
                }
            )
    _logger.info("RFA process initialized")

    _logger.info(
        "Recomputing loyalty points for all partners and all sale orders from 2025"
    )
    # remove all the loyalty cards
    _logger.info("Removing all loyalty cards")
    env["loyalty.card"].search([("program_id", "=", program.id)]).unlink()

    # recompute the loyalty points
    orders = env["sale.order"].search(
        [
            ("date_order", ">=", "2025-01-01"),
            ("state", "in", ["sale", "done"]),
            ("partner_id", "in", partners.ids),
        ]
    )
    cpt = 0
    total = len(orders)
    _logger.info(f"Recomputing loyalty points for {len(orders)} sale orders")
    for so in orders.with_context(
        ensure_program_valid_at_order_date=True, restricted_program_ids=program.ids
    ):
        cpt += 1
        _logger.info(
            f"Recomputing loyalty points for sale order {so.name} ({cpt}/{total})"
        )
        so._update_programs_and_rewards()
    _logger.info("Recomputing loyalty accruate points for all orders")
    env["sale.order.coupon.points"].search([])._refresh_accrued_points()


@click.command()
@click_odoo.env_options(default_log_level="info")
def init_rfa(env):
    _init_rfa(env)


if __name__ == "__main__":
    init_rfa()
