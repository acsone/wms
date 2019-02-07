-- Rewrite imported purchase_order_lines
--
-- for all purchase lines imported in done state
-- and thus having no move attached to them
--
-- Set qty_invoived = received_qty
-- and qty_to_invoice = ordered - received
WITH t_pol_done AS(
SELECT pol.id FROM purchase_order_line pol
  INNER JOIN purchase_order po ON po.id = pol.order_id
  LEFT JOIN stock_move as m ON m.purchase_line_id = pol.id
  WHERE po.name !~ '^PO'
   AND po.state = 'done'
   AND m.id IS NULL
   AND pol.qty_invoiced != qty_received
)
UPDATE purchase_order_line AS t
  SET qty_invoiced = qty_received,
      qty_to_invoice = product_qty - qty_received
  FROM t_pol_done
  WHERE t.id = t_pol_done.id;
