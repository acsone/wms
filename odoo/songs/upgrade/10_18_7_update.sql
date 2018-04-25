-- remove_old_pesky_views
-- The rewrite of shipping_costs caused some problems with the views.
DELETE FROM ir_ui_view where arch_db ~'costs_on_in';

-- change product with ketamine category to stupefiant before removal of the ketamine categ
UPDATE product_template SET categ_id = (SELECT res_id FROM ir_model_data WHERE name = 'product_categ_stupefiant')
  WHERE categ_id = (SELECT res_id FROM ir_model_data WHERE name = 'product_categ_ketamine');
