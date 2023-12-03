from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Case: Internal pickings are in a different channel than the outgoing.

    this script is used with Click Odoo, the purpose is to unrelease internal pickings
    assigned to the wrong release channel.
    The script first looks for the internal pickings assigned to the channel,
    then retrieves the corresponding outgoing pickings.
    It filters those pickings that are in a different channel and proceeds to call
    the unrelease.
    In the end, we expect all internal pickings in the wrong channel to be canceled.
    """
    channel_id = 170
    internal_pickings = (
        env["stock.release.channel"]
        .browse(channel_id)
        .picking_ids.filtered(
            lambda p: p.picking_type_code == "internal" and p.state == "assigned"
        )
    )
    out_pickings = internal_pickings.move_ids.move_dest_ids.picking_id
    out_pickings_to_unrlease = out_pickings.filtered(
        lambda p: p.release_channel_id.id != channel_id
    )
    out_pickings_to_unrlease.move_ids.filtered("unrelease_allowed").unrelease()
