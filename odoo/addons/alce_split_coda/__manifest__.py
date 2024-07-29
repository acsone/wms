# Copyright 2018 Okia SPRL
# Copyright 2023 ACSONE SA/NV

{
    "name": "Split CODA",
    "version": "16.0.1.0.0",
    "author": "Okia, ACSONE SA/NV",
    "category": "Accounting",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # l10n_be_coda is an Odoo enterprise module
    "depends": [
        # fmt: off
        # Others
        "l10n_be_coda",
        # fmt: on
    ],
    "data": [],
    "installable": True,
    "license": "Other proprietary",
}
