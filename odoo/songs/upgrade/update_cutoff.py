# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import anthem

from odoo import fields


@anthem.log
def delete_existing_cutoff_entries(ctx, cutoff):
    """Delete existing accounting entries"""
    # Cancel cutoff entry
    entry = cutoff.move_id
    entry.button_cancel()
    # Cancel reversal entry (april reversal is on the move and may reversal on
    # the cutoff)
    reversal_entry = cutoff.move_reversal_id or entry.reversal_id
    reversal_entry.button_cancel()
    # Delete reconciliation
    reconciled_lines_action = entry.open_reconcile_view()
    reconciled_lines_ids = reconciled_lines_action.get('domain')[0][2]
    reconciled_lines = ctx.env['account.move.line'].browse(
        reconciled_lines_ids
    )
    for account in reconciled_lines.mapped('account_id'):
        account_lines = reconciled_lines.filtered(
            lambda l: l.account_id == account
        )
        unreconcile_wiz = (
            ctx.env['account.unreconcile']
            .with_context(active_ids=account_lines.ids)
            .create({})
        )
        unreconcile_wiz.trans_unrec()
    entry_names = {'entry': entry.name, 'reversal': reversal_entry.name}
    # Delete reversal entry
    reversal_entry.unlink()
    # Delete cutoff entry
    entry.unlink()
    return entry_names


@anthem.log
def update_cutoff_lines(ctx, cutoff):
    """Update existing lines with qties processed on last day of the month"""
    # Reset it to draft
    cutoff.back2draft()
    for i, cutoff_line in enumerate(cutoff.line_ids):
        with ctx.log(
            'Processing cutoff lines: %s / %s' % (i + 1, len(cutoff.line_ids))
        ):
            po_line = cutoff_line.purchase_line_id
            from_string = fields.Date.from_string
            moves_on_date = po_line.move_ids.filtered(
                lambda m: from_string(m.date)
                == from_string(cutoff.cutoff_date)
            )
            for move in moves_on_date:
                move_qty = move.product_uom_qty
                if move.product_uom != po_line.product_uom:
                    move_qty = move.product_uom._compute_quantity(
                        move.product_uom_qty, po_line.product_uom
                    )
                if move.picking_id.picking_type_code == 'incoming':
                    received_qty = cutoff_line.received_qty + move_qty
                elif move.picking_id.picking_type_code == 'outgoing':
                    received_qty = cutoff_line.received_qty - move_qty
                # As quantity is not computed automatically in
                #  account_cutoff_accrual_picking, we calc it here, so that
                #  _calc_cutoff_amount is triggered
                quantity = received_qty - cutoff_line.invoiced_qty
                cutoff_line.write(
                    {'received_qty': received_qty, 'quantity': quantity}
                )


@anthem.log
def regenerate_cutoff_entries(ctx, cutoff, entry_names):
    """Regenerate and post accounting entries"""
    # Ensure automatic reversal is marked
    cutoff.auto_reverse = True
    # Generate entries
    cutoff.create_move()
    # Update name and post cutoff entry
    cutoff.move_id.name = entry_names.get('entry')
    cutoff.move_id.post()
    # Post cutoff entry reversal
    cutoff.move_reversal_id.name = entry_names.get('reversal')
    cutoff.move_reversal_id.post()


@anthem.log
def main(ctx):
    """Fix cutoff entries with missing moves on last day of the month"""
    cutoff_dates = ['2019-04-30', '2019-05-31']
    for date in cutoff_dates:
        with ctx.log('Fixing cutoff from %s' % date):
            # Get the cutoff record
            cutoff = ctx.env['account.cutoff'].search(
                [('cutoff_date', '=', date), ('type', '=', 'accrued_expense')]
            )
            entry_names = delete_existing_cutoff_entries(ctx, cutoff)
            update_cutoff_lines(ctx, cutoff)
            regenerate_cutoff_entries(ctx, cutoff, entry_names)
