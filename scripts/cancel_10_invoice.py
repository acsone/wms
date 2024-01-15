#!/usr/bin/env python
import click
import click_odoo


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
    for invoice in invoices:
        invoice.button_cancel()
        invoice.button_draft()
        invoice.unlink()
        env.cr.commit()


@click.command()
@click_odoo.env_options()
def main(env):
    _cancel_invoices(env)


if __name__ == "__main__":
    main()
