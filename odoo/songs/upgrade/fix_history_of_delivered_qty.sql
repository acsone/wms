-- fix delivered qty on closed purchases
WITH t_pol AS (
SELECT pol.id, det.dcfqul
  FROM purchase_order_line AS pol
    INNER JOIN purchase_order AS po ON po.id = pol.order_id
    INNER JOIN db2_pdetcdfo AS det ON det.dcfsui::text = po.name AND det.dcfnli = pol.sequence
  WHERE det.dcfqul <> pol.qty_received AND pol.state = 'done'
)
UPDATE purchase_order_line AS t
  SET qty_received = t_pol.dcfqul,
      qty_invoiced = t_pol.dcfqul
  FROM t_pol
  WHERE t.id = t_pol.id;

-- fix delivered qty on closed sales
WITH t_sol AS (
SELECT sol.id, det.dccqul
  FROM sale_order_line AS sol
    INNER JOIN sale_order AS po ON po.id = sol.order_id
    INNER JOIN db2_pdetcdcl AS det ON det.dccsui::text = po.name AND det.dccnli = sol.sequence
  WHERE det.dccqul <> sol.qty_delivered AND sol.state = 'done'
)
UPDATE sale_order_line AS t
  SET qty_delivered = t_sol.dccqul,
      qty_invoiced = t_sol.dccqul
  FROM t_sol
  WHERE t.id = t_sol.id;

