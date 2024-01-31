#!/usr/bin/env python
import logging

import click
import click_odoo

_logger = logging.getLogger(__name__)


# /!\ Do not forget to provide the two args -d for the database AND -c for the config file
# containing the fs_storage information.


def _batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def _regenerate_invoices_pdf(env, date_from):
    env.cr.execute(
        """
            SELECT array_agg(am.id)
              FROM account_move AS am
         LEFT JOIN ir_attachment ON ir_attachment.res_id = am.id
                   AND ir_attachment.res_model = 'account.move'
             WHERE am.create_date >= '%s'
                   AND am.move_type IN ('out_invoice', 'out_refund')
                   AND am.state = 'posted'
                   AND ir_attachment.id IS NULL
         """
        % date_from
    )
    ids = env.cr.fetchone()
    if ids:
        invoice_ids = ids[0]
        if invoice_ids:
            number_of_invoices_per_batch = 10
            batches = list(_batched(invoice_ids, number_of_invoices_per_batch))
            number_of_invoices = len(invoice_ids)
            number_of_batches = len(batches)
            batch_number = 0
            _logger.info(
                f"Regenerating {number_of_invoices} invoices in {number_of_batches} batch(es) of maximum {number_of_invoices_per_batch} invoices"
            )
            for ids_batch in batches:
                batch_number += 1
                _logger.info(
                    f"Regenerating invoices pdf from batch {batch_number} of {number_of_batches}"
                )
                env["ir.actions.report"].sudo()._render_qweb_pdf(
                    env.ref("account.account_invoices_without_payment"), ids_batch
                )
                env.cr.commit()
                _logger.info(f"Committed batch {batch_number} of {number_of_batches}")


@click.command()
@click_odoo.env_options()
def main(env):
    _regenerate_invoices_pdf(env, "2023-12-05")


if __name__ == "__main__":
    main()
