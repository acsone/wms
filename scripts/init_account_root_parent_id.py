"""This script init account_root_parent_id for account.move.line."""

env = env  # noqa

cr = env.cr

batch_size = 10000
cr.execute(
    """
    SELECT COUNT(*)
    FROM account_move_line ml
    JOIN account_root root ON ml.account_root_id = root.id
    WHERE ml.account_root_parent_id IS NULL
"""
)
total_rows = cr.fetchone()[0]

num_batches = (total_rows // batch_size) + (1 if total_rows % batch_size != 0 else 0)

for batch_num in range(num_batches):
    offset = batch_num * batch_size
    cr.execute(
        f"""
        UPDATE account_move_line AS ml
        SET account_root_parent_id = root.parent_id
        FROM account_root AS root
        WHERE ml.account_root_id = root.id
        AND ml.account_root_parent_id IS NULL
        AND ml.id IN (
            SELECT id FROM account_move_line
            WHERE account_root_parent_id IS NULL
            ORDER BY id
            LIMIT {batch_size}
        )
    """
    )
    cr.commit()
    print(
        f"Batch {batch_num + 1} of {num_batches} completed. "
        f"Processed {min((batch_num + 1) * batch_size, total_rows)} records."
    )
