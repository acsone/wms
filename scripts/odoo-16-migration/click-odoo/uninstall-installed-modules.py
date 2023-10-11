#!/usr/bin/env click-odoo
"""Uninstall modules that are still in v16 but not needed anymore."""
import sys

env = env  # noqa

uninstall = sys.argv[1]


uninstall_names = uninstall.split(",")

if uninstall_names:
    modules = env["ir.module.module"].search(
        [("name", "in", uninstall_names), ("state", "=", "installed")]
    )
    modules.button_immediate_uninstall()
