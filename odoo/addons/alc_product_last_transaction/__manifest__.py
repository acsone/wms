{
    "name": "Alc Product Last Transaction",
    "summary": """Compute the last selling and purchasing date of products.
    By default the computation is done at the current date but a value `history_date`
    can be added to the context to force the computation for a date in the past.""",
    "version": "16.0.1.0.0",
    "category": "Product",
    "author": "CamptoCamp, ACSONE SA/NV",
    "depends": [
        # Others
        "purchase",
        "sale",
    ],
    "installable": True,
    "license": "AGPL-3",
    "pre_init_hook": "pre_init_hook",
}
