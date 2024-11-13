from . import models


def pre_init_hook(cr):
    cr.execute(
        """
        ALTER TABLE account_move_line
        ADD COLUMN account_root_parent_id integer;
    """
    )
    cr.execute(
        """
        UPDATE account_move_line AS ml
        SET account_root_parent_id = root.parent_id
        FROM account_root AS root
        WHERE ml.account_root_id = root.id
        AND  ml.date > '2023-08-31';
        """
    )
    cr.execute(
        """
        CREATE INDEX IF NOT EXISTS account_move_line_account_root_id_index ON
        public.account_move_line USING btree (account_root_id);
        CREATE INDEX IF NOT EXISTS account_move_line_account_root_parent_id_index ON
        public.account_move_line USING btree (account_root_parent_id);
        """
    )
