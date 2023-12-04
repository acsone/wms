from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Case: the shipment advice is blocked due to a move that can't cancel.

    one of the outgoing pickings contains additional products but not available the SA
    needs to cancel it,

    this script force the cancel and set the shipment advice to done and the release
    channel to deliver
    """
    s_id = 49389
    s = env["shipment.advice"].browse(s_id)
    s.name
    assert (
        s.release_channel_id.state == "delivering_error"
    ), "this script is only for delivering error channels"
    s.action_draft()
    s.action_confirm()
    s.action_in_progress()
    s.with_context(force_cancel=True).action_done()
    s.release_channel_id.state = "delivered"
    env.cr.commit()
