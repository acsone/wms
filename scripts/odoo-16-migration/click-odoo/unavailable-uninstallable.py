"""Set modules that are not available in the addons path to uninstallable state."""

import ast
from pathlib import Path

from odoo.modules import get_module_path


def is_available(module_name: str) -> bool:
    module_path = get_module_path(module_name)
    if not module_path:
        return False
    for manifest in ("__manifest__.py", "__openerp__.py"):
        manifest_path = Path(module_path, manifest)
        if not manifest_path.is_file():
            continue
        manifest_data = ast.literal_eval(manifest_path.read_text(encoding="utf-8"))
        if manifest_data.get("installable", True):
            return True
    return False


def main():
    to_mark_uninstallable = []

    module_names = env["ir.module.module"].search([]).mapped("name")  # noqa: F821
    for module_name in module_names:
        if not is_available(module_name):
            to_mark_uninstallable.append(module_name)

    print("marking modules as uninstallable:", to_mark_uninstallable)
    env.cr.execute(  # noqa: F821
        """
        UPDATE ir_module_module
        SET state='uninstallable'
        WHERE name IN %(module_names)s
        """,
        {"module_names": tuple(to_mark_uninstallable)},
    )


main()
