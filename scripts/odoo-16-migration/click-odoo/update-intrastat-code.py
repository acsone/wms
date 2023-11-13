#!/usr/bin/env click-odoo
"""Update the intrastat main code."""
# pylint: disable=undefined-variable
env = env  # noqa


env["product.category"].search([])._compute_intrastat_code_id()
