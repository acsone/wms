-- Remove Nbr lignes Picking filter set manually without xmlid and wrong now
DELETE FROM ir_filters
    WHERE model_id = 'stock.pack.operation'
    AND name = 'Nbr lignes Picking'
    AND context LIKE '%' || 'write_uid' || '%';

-- stock.pack.operation actions created manually, replaced by an action in addon
DELETE FROM ir_actions WHERE id in (619, 608);

-- stock.pack.operation menu created manually, replaced by a menu in addon
DELETE FROM ir_ui_menu WHERE id = 447;
