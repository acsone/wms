# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def _stock_location_fields(cr):
    # set usage as view where act_as_view is set
    query = """
        UPDATE stock_location
        SET usage = 'view'
        WHERE act_as_view = TRUE
    """
    cr.execute(query)


def migrate(cr, version):
    _stock_location_fields(cr)
