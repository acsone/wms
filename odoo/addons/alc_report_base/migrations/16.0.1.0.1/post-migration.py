# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # restore web.external_layout
    file_path = "migrations/16.0.1.0.1/web_external_layout_template.xml"
    openupgrade.load_data(env.cr, "alc_report_base", file_path, mode="init")
