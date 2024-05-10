def migrate(cr, version=None):
    SQL = """
        UPDATE stock_picking
        SET rank = null
        WHERE grn_id is null and rank is not null and state not in ('done', 'cancel')
        and picking_type_id in (select id from stock_picking_type where code ='incoming')
        """
    cr.execute(SQL)
