"""Migrate attachments to S3.

This script is meant to be run after the installation of the attachment_s3 module.
It is based on the _force_storage_to_object_storage() function of attachment_str,
modified to commit regularly and not delete files from the filestore.
"""

# pylint: disable=print-used
# pylint: disable=import-outside-toplevel

import multiprocessing
import os
import signal
import traceback

import psycopg2

dbname = os.environ["DB_NAME"]


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def _migrate_batch(attachment_ids):
    print("migrating attachments", attachment_ids)
    from click_odoo import OdooEnvironment

    from odoo import api

    @api.model
    def _storage(self):
        return "s3"

    with OdooEnvironment(database=dbname) as env:
        env["ir.attachment"]._patch_method("_storage", _storage)
        for attachment_id in attachment_ids:
            try:
                with env.cr.savepoint():
                    # check that no other transaction has
                    # locked the row, don't send a file to storage
                    # in that case
                    env.cr.execute(
                        "SELECT id "
                        "FROM ir_attachment "
                        "WHERE id = %s "
                        "FOR UPDATE NOWAIT",
                        (attachment_id,),
                        log_exceptions=False,
                    )

                    # This is a trick to avoid having the 'datas'
                    # function fields computed for every attachment on
                    # each iteration of the loop. The former issue
                    # being that it reads the content of the file of
                    # ALL the attachments on each loop.
                    env.clear()
                    attachment = env["ir.attachment"].browse(attachment_id)
                    attachment_path = attachment._full_path(attachment.store_fname)
                    if not os.path.exists(attachment_path):
                        print("File", attachment.store_fname, "does not exist")
                        continue
                    attachment._move_attachment_to_store()
            except psycopg2.OperationalError:
                print("Could not migrate attachment", attachment_id, "to s3")
            except Exception:
                traceback.print_exc()
                raise


def _migrate():

    from click_odoo import OdooEnvironment

    with OdooEnvironment(dbname) as env:
        print("migrating files to the s3 object storage")
        # The weird "res_field = False OR res_field != False" domain
        # is required! It's because of an override of _search in ir.attachment
        # which adds ('res_field', '=', False) when the domain does not
        # contain 'res_field'.
        # https://github.com/odoo/odoo/blob/9032617120138848c63b3cfa5d1913c5e5ad76db/odoo/addons/base/ir/ir_attachment.py#L344-L347
        domain = [
            "!",
            ("store_fname", "=like", "s3://%"),
            "|",
            ("res_field", "=", False),
            ("res_field", "!=", False),
        ]
        attachment_ids = env["ir.attachment"].search(domain, order="create_date").ids

    pool = multiprocessing.Pool(5)
    pool.map(_migrate_batch, chunks(attachment_ids, 100))
    pool.close()
    pool.join()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os.environ["ODOO_LOGGING_JSON"] = ""
    _migrate()
