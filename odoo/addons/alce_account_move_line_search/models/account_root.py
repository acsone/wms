# Copyright 2024 ACSONE SA/NV

from odoo import tools

from odoo.addons.account.models.account_account import AccountRoot as AccountRootBase


class AccountRoot(AccountRootBase):
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(
            f"""
            CREATE MATERIALIZED VIEW {self._table} AS (
                SELECT DISTINCT ASCII(code) * 1000 + ASCII(SUBSTRING(code,2,1)) AS id,
                       LEFT(code,2) AS name,
                       ASCII(code) AS parent_id,
                       company_id
                FROM account_account WHERE code IS NOT NULL
                UNION ALL
                SELECT DISTINCT ASCII(code) AS id,
                       LEFT(code,1) AS name,
                       NULL::int AS parent_id,
                       company_id
                FROM account_account WHERE code IS NOT NULL
            );
            CREATE INDEX account_root_pkey ON account_root (id);
            CREATE INDEX account_root_parent_id ON account_root (parent_id);
        """
        )

    def refresh_materialized_view(self):
        self.env.cr.execute(f"REFRESH MATERIALIZED VIEW {self._table}")
