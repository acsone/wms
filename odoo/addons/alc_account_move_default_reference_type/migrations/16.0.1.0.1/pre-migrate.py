# Copyright 2024 ACSONE SA/NV


def migrate(cr, version):
    cr.execute(
        """
    UPDATE account_move
    SET reference_type='none'
    WHERE move_type NOT IN ('out_invoice', 'out_refund') AND reference_type='structured'
    """
    )
