#!/usr/bin/env python
import logging
import sys

import click
import click_odoo

_logger = logging.getLogger(__name__)


def _cancel_invoices(env):
    """
    Get all invoices created after 2023-01-11 21:00:00.

    by OdooBot (1) and invoicing_mode = ten_days
    """
    invoices = env["account.move"].search(
        [
            ("create_date", ">=", "2024-01-11 20:00:00"),
            ("move_type", "=", "out_invoice"),
            ("create_uid", "=", 1),
            ("partner_id.invoicing_mode", "=", "ten_days"),
            ("state", "=", "posted"),
        ]
    )
    invoices_len = len(invoices)
    i = 1
    for invoice in invoices:
        invoice.button_draft()
        invoice.unlink()
        env.cr.commit()
        sys.stderr.write(f"=== Invoice {i}/{invoices_len} has been deleted. ===\n")
        i += 1
    _logger.info(f"Having deleted {i - 1} invoices.")

    # Set to draft invoices that have been created by a real user
    invoices = env["account.move"].search(
        [
            ("invoice_date", "=", "2024-01-11"),
            ("move_type", "=", "out_invoice"),
            ("create_uid", "!=", 1),
            ("write_uid", "=", 1),
            ("payment_state", "=", "not_paid"),
            ("partner_id.invoicing_mode", "=", "ten_days"),
            ("state", "=", "posted"),
        ]
    )
    i = 1
    invoices_len = len(invoices)
    attachment_obj = env["ir.attachment"]
    for invoice in invoices:
        invoice.button_draft()
        # Remove attachments
        attachments = attachment_obj.search(
            [("res_id", "=", invoice.id), ("res_model", "=", "account.move")]
        )
        attachments.unlink()
        env.cr.commit()
        sys.stderr.write(
            f"=== Invoice {i}/{invoices_len} has been set to draft. === \n"
        )
        i += 1

    _logger.info(f"Having set {i - 1} invoices to draft.")


@click.command()
@click_odoo.env_options()
def main(env):
    _cancel_invoices(env)


if __name__ == "__main__":
    main()
