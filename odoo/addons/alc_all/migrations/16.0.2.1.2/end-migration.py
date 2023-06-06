from openupgradelib import openupgrade


def _remove_unused_priority(env, xml_id):
    obj = env.ref(xml_id, raise_if_not_found=False)
    if obj:
        obj.unlink()


@openupgrade.migrate()
def migrate(env, version):
    _remove_unused_priority(
        env, "specific_account.selection__stock_picking__priority__2"
    )
    _remove_unused_priority(
        env, "specific_account.selection__stock_picking__priority__3"
    )
