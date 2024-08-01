def pre_init_hook(cr):

    # Create the is_empty column
    cr.execute(
        """
            ALTER TABLE stock_lot
            ADD COLUMN is_empty BOOLEAN DEFAULT TRUE;
        """
    )

    # Update the is_empty value to False for lots linked to quants
    cr.execute(
        """
            UPDATE stock_lot
            SET is_empty = FALSE
            WHERE id IN (
                SELECT DISTINCT lot_id
                FROM stock_quant
                WHERE lot_id IS NOT NULL
            );
        """
    )
