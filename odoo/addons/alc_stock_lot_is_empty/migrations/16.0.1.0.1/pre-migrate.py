# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def migrate(cr, version):
    # Drop the existing is_empty column
    cr.execute(
        """
        ALTER TABLE stock_lot
        DROP COLUMN IF EXISTS is_empty;
    """
    )

    # Recreate the is_empty column with default value True
    cr.execute(
        """
        ALTER TABLE stock_lot
        ADD COLUMN is_empty BOOLEAN DEFAULT TRUE;
    """
    )

    # Update the is_empty value to False for lots linked to quants in internal locations
    cr.execute(
        """
        UPDATE stock_lot
        SET is_empty = FALSE
        WHERE id IN (
            SELECT DISTINCT lot_id
            FROM stock_quant
            WHERE lot_id IS NOT NULL
            AND location_id IN (
                SELECT id
                FROM stock_location
                WHERE usage = 'internal'
            )
        );
    """
    )
