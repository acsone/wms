-- Remove Nbr lignes Picking filter set manually without xmlid and wrong now
DELETE FROM ir_filters
    WHERE model_id = 'stock.pack.operation'
    AND name = 'Nbr lignes Picking'
    AND context LIKE '%' || 'write_uid' || '%';
