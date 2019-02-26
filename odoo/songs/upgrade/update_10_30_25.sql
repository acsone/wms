-- fix 'date_order' of sales orders which has been
-- set at 12:00:00 (UTC) for all orders imported from
-- magento in PR https://github.com/camptocamp/alcyon_odoo/pull/1394
UPDATE sale_order
SET date_order = create_date
WHERE create_date >= '2019-02-25 00:00:00'
AND date_order::varchar LIKE '% 12:00:00';
