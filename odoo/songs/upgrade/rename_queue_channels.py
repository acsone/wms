# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


@anthem.log
def post(ctx):
    rename_queue_channels(ctx)
    merge_delivery_channels(ctx)
    remove_obsolete_channels(ctx)


rename_mapping = [
    ('root.background.sale_confirm', 'root.priority.sale_confirm'),
    ('root.invoice_validation', 'root.background.invoice_validation'),
    ('root.background.delivery', 'root.background.stock_picking_deliver'),
    # ('root.background.deliver',
    #  'root.background.stock_picking_deliver'),
    ('root.action_assign', 'root.background.stock_reassign_trial'),
    ('root.action_assign', 'root.background.stock_picking_assign'),
    ('root.invoice_creation', 'root.background.invoice_creation'),
    ('root.update_po', 'root.background.update_po'),
    ('root.esb', 'root.background.esb'),
    ('root.background.invoice', 'root.background.invoice_print'),
    ('root.background.invoice', 'root.background.invoice_send'),
]

to_remove = [
    'root.invoices_creation',
    'root.inventory_init',
    'root.db2.generate_jobs',
    'root.db2.create_or_update',
    'root.db2.fetch',
    'root.db2',
]


@anthem.log
def rename_queue_channels(ctx):
    Channel = ctx.env['queue.job.channel']

    prio_chan = Channel.search([('complete_name', '=', 'root.priority')])
    if not prio_chan:
        root = Channel.search([('complete_name', '=', 'root')])
        prio_chan = Channel.create({'name': 'priority', 'parent_id': root.id})

    main_chan = {
        'root.priority': prio_chan,
        # we assume this one already exists
        'root.background': Channel.search(
            [('complete_name', '=', 'root.background')]
        ),
    }

    for old_name, new_name in rename_mapping:
        chan = Channel.search([('complete_name', '=', old_name)])
        if chan:
            path = new_name.split('.')
            name = path[-1]
            parent_name = '.'.join(path[:-1])
            chan.write({'name': name, 'parent_id': main_chan[parent_name].id})


@anthem.log
def merge_delivery_channels(ctx):
    """merge delivery and deliver channels

    root.background.delivery
    and
    root.background.deliver

    become root.background.stock_picking_deliver
    """

    functions = ctx.env['queue.job.function'].search(
        [('channel_id.complete_name', '=', 'root.background.deliver')]
    )
    channel = ctx.env['queue.job.channel'].search(
        [('complete_name', '=', 'root.background.stock_picking_deliver')]
    )
    functions.write({'channel_id': channel.id})


@anthem.log
def remove_obsolete_channels(ctx):
    Function = ctx.env['queue.job.function']
    funcs = Function.search([('channel_id.complete_name', 'in', to_remove)])
    funcs.unlink()
    Channel = ctx.env['queue.job.channel']
    channels = Channel.search([('complete_name', 'in', to_remove)])
    channels.unlink()
