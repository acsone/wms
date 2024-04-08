from collections import defaultdict

env = env  # noqa

# first we collent all the invoice lines in invoice for a different payment mode

query = """
select distinct
    aml.id,
    aml.move_id
    -- so_partner.name as "'Client B2C",
    -- inv_partner.name as "VT",
    -- am.date as "Invoice Date",
    -- am.name as "Invoice",
    -- inv_pm.name ->> 'en_US' as "Invoice Payment Mode",
    -- so.name as "Sale Order",
    -- so_pm.name ->> 'en_US' as "Sale Order Payment Mode"
    -- so_pm.id as "Sale Order Payment Mode ID",
    -- inv_pm.id as "Invoice Payment Mode ID"
from
    account_move_line aml
    join account_move am on am.id = aml.move_id
    join sale_order_line_invoice_rel solir on solir.invoice_line_id = aml.id
    join sale_order_line sol on sol.id = solir.order_line_id
    join sale_order so on so.id = sol.order_id
    join account_payment_mode so_pm on so_pm.id = so.payment_mode_id
    join account_payment_mode inv_pm on inv_pm.id = am.payment_mode_id
    join res_partner so_partner on so_partner.id = so.partner_id
    join res_partner inv_partner on inv_partner.id = am.partner_id
WHERE
    am.payment_mode_id != so.payment_mode_id
    and aml.create_date >= '2023-10-01'
    and so_partner.is_b2c_customer = true
    and so_pm.id in (1, 5) and inv_pm.id in (1, 5)
Order by
    aml.move_id
"""
env.cr.execute(query)

lines_by_invoice = defaultdict(list)
for rec_id, move_id in env.cr.fetchall():
    lines_by_invoice[move_id].append(rec_id)

# for each invoice we will create a credit note with the same payment mode as the invoice
# for each invoice lines

for move_id, line_ids in lines_by_invoice.items():
    original_move = env["account.move"].browse(move_id)
    reversal_wizard = env["account.move.reversal"]
    vals = reversal_wizard.with_context(active_ids=move_id).default_get(
        ["move_ids", "company_id", "refund_method"]
    )
    reversal = reversal_wizard.create(
        {
            "move_ids": [(4, move_id)],
            "reason": "Paiement erroné",
            "journal_id": original_move.journal_id.id,
        }
    )
    new_move_id = reversal.reverse_moves()["res_id"]

    # now we only need to keep the invoice lines we want to reverse
    reversal_move = env["account.move"].browse(new_move_id)
    sale_line_ids = env["account.move.line"].browse(line_ids).mapped("sale_line_ids")
    for line in reversal_move.invoice_line_ids:
        if line.sale_line_ids not in sale_line_ids:
            line.unlink()
    # get all impacted sale orders
    sale_orders = sale_line_ids.mapped("order_id")
    # write a note on the invoice to refer to the sale orders
    document_msg = (
        "<p>Remboursement des ventes concernant un autre mode de paiement:<p>"
    )
    document_msg += f'<ul>{"".join(f"<li>{document._get_html_link()}</li>" for document in sale_orders)}</ul>'
    document_msg += (
        f"<p>Mode de paiement utilisé: {original_move.payment_mode_id.name}</p>"
    )
    document_msg += (
        f"<p>Mode de paiement attendu: {sale_orders[0].payment_mode_id.name}</p>"
    )
    reversal_move.message_post(body=document_msg)
    print(
        f"Reversed {original_move.name} into {reversal_move.name} with id {new_move_id}"
    )
env.cr.commit()
