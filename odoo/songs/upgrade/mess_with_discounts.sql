-- When the product price category is GMA
-- (and discount3 is not set as catched by second rule)
WITH t_sol1 AS (
SELECT sol.id, sol.discount2, sol.discount3
  FROM sale_order_line AS sol
    INNER JOIN product_product AS pp ON sol.product_id = pp.id
    INNER JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
    INNER JOIN product_price_category AS pcat ON pcat.id = pt.price_category_id
  WHERE pcat.name = 'GMA'
    AND sol.discount2 <> 0
    AND sol.discount3 = 0
)
UPDATE sale_order_line AS t
  SET discount2 = t_sol1.discount3,
      discount3 = t_sol1.discount2
  FROM t_sol1
  WHERE t.id = t_sol1.id;

-- When there is a discount2 and a discount3
WITH t_sol2 AS (
SELECT sol.id, sol.discount2, sol.discount3
  FROM sale_order_line AS sol
    INNER JOIN product_product AS pp ON sol.product_id = pp.id
    INNER JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
  WHERE sol.discount2 <> 0
    AND sol.discount3 <> 0
    AND sol.discount2 <> sol.discount3
)
UPDATE sale_order_line AS t
  SET discount2 = t_sol2.discount3,
      discount3 = t_sol2.discount2
  FROM t_sol2
  WHERE t.id = t_sol2.id;
