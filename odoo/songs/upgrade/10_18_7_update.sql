-- remove_old_pesky_views
-- The rewrite of shipping_costs caused some problems with the views.
DELETE FROM ir_ui_view where arch_db ~'costs_on_in';
