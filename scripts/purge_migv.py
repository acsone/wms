"""Remove all journal entries from the MIGV journal.

They correspond to invoices that had no corresponding account moves in v10.
"""
env = env  # noqa

moves = env["account.move"].search([("journal_id", "=", "MIGV")])
# assert len(moves) == 1864
for move in moves:
    print(f"Deleting move {move.id} - {move.name}")
    env.cr.execute("delete from account_move where id=%s", (move.id,))
    env.cr.commit()
