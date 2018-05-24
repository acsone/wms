-- Compute removal_date and alert_date
-- the rule is simpler to realise with an SQL query
update stock_production_lot set removal_date=life_date ::timestamp - interval '91 days', alert_date=life_date::timestamp - interval '1 days';
