# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    # Ensures the vector extension is installed
    cr.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # To avoid lengthy computations by the ML model during installation on these computed fields, create the embedding vector columns beforehand.
    cr.execute(
        """
        ALTER TABLE product_product
        ADD COLUMN IF NOT EXISTS description_vector vector(384),
        ADD COLUMN IF NOT EXISTS characteristics_vector vector(1000);
        """
    )
