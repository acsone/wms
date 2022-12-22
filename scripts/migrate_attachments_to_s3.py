"""Migrate attachments to S3.

This script is meant to be run after the installation of the attachment_s3 module.
It is based on the _force_storage_to_object_storage() function of attachment_str,
modified to commit regularly and not delete files from the filestore.
"""

import logging

import psycopg2

_logger = logging.getLogger(__name__)


# pylint: disable=self-assigning-variable
# pylint: disable=undefined-variable
env = env  # noqa


def _force_storage_to_object_storage():
    _logger.info("migrating files to the object storage")
    storage = env["ir.attachment"]._storage()
    # The weird "res_field = False OR res_field != False" domain
    # is required! It's because of an override of _search in ir.attachment
    # which adds ('res_field', '=', False) when the domain does not
    # contain 'res_field'.
    # https://github.com/odoo/odoo/blob/9032617120138848c63b3cfa5d1913c5e5ad76db/odoo/addons/base/ir/ir_attachment.py#L344-L347
    domain = [
        "!",
        ("store_fname", "=like", "{}://%".format(storage)),
        "|",
        ("res_field", "=", False),
        ("res_field", "!=", False),
    ]
    # We do a copy of the environment so we can workaround the cache issue
    # below. We do not create a new cursor by default because it causes
    # serialization issues due to concurrent updates on attachments during
    # the installation
    with env["ir.attachment"].do_in_new_env() as new_env:
        model_env = new_env["ir.attachment"]
        ids = model_env.search(domain).ids
        for i, attachment_id in enumerate(ids):
            try:
                with new_env.cr.savepoint():
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
                    new_env.clear()
                    attachment = model_env.browse(attachment_id)
                    attachment._move_attachment_to_store()
                if (i + 1) % 100 == 0:
                    _logger.info(
                        "migrated %s/%s attachments to the object storage",
                        i + 1,
                        len(ids),
                    )
                    new_env.cr.commit()
            except psycopg2.OperationalError:
                _logger.error("Could not migrate attachment %s to S3", attachment_id)


if __name__ == "__main__":
    _force_storage_to_object_storage()
