-- ALCYN-2029
-- Stock moves have been created in December 2018 with quantities with 64 digits
-- (without decimals). The moves have been reverted, but these large numbers still
-- provoke computation errors. As the moves with these quantities have been reverted,
-- we can safely put lower arbitrary numbers (they were already erroneous anyway).
-- The 2 quants here are for the same product.

-- instead of 10800000000000002159442686578899338249717564195187607370993762304
UPDATE stock_quant SET qty = 10800000 WHERE id = 177491;

-- instead of 1461501637330903242722238491143009802811953119232
UPDATE stock_quant SET qty = 146150 WHERE id = 188176;

-- recompute quantities from sum of all the quants of the moves in case we have several
-- quants per move
UPDATE stock_move m SET
product_uom_qty = (
  SELECT SUM(q.qty) FROM stock_quant q
  INNER JOIN stock_quant_move_rel rel ON rel.quant_id = q.id WHERE rel.move_id = m.id
  ),
product_qty = (
  SELECT SUM(q.qty) FROM stock_quant q
  INNER JOIN stock_quant_move_rel rel ON rel.quant_id = q.id WHERE rel.move_id = m.id
),
ordered_qty = (
  SELECT SUM(q.qty) FROM stock_quant q
  INNER JOIN stock_quant_move_rel rel ON rel.quant_id = q.id WHERE rel.move_id = m.id
),
-- '* 2' because the weight of a unit for this product is '2'
weight = (
  SELECT SUM(q.qty) FROM stock_quant q
  INNER JOIN stock_quant_move_rel rel ON rel.quant_id = q.id WHERE rel.move_id = m.id
) * 2
FROM stock_quant_move_rel rel, stock_quant quant
WHERE m.id = rel.move_id
AND rel.quant_id = quant.id
AND quant.id IN (177491, 188176);
