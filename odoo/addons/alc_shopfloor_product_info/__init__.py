from . import actions
from . import models


def pre_init_hook(cr):
    cr.execute(
        "ALTER TABLE stock_location ADD COLUMN display_in_shopfloor_product_info bool DEFAULT true"
    )
