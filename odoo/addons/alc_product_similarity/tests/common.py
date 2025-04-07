# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProductSimilarityBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # --- Create attributes

        # animal sizes
        cls.animale_size_l = cls.env["attribute.option"].create(
            {
                "name": "l",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_animal_size_option_ids"
                ).id,
            }
        )
        cls.animale_size_m = cls.env["attribute.option"].create(
            {
                "name": "m",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_animal_size_option_ids"
                ).id,
            }
        )
        cls.animale_size_s = cls.env["attribute.option"].create(
            {
                "name": "m",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_animal_size_option_ids"
                ).id,
            }
        )

        # age categories
        cls.categ_age_junior = cls.env["attribute.option"].create(
            {
                "name": "junior",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_categ_age_option_ids"
                ).id,
            }
        )
        cls.categ_age_adult = cls.env["attribute.option"].create(
            {
                "name": "adult",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_categ_age_option_ids"
                ).id,
            }
        )
        cls.categ_age_senior = cls.env["attribute.option"].create(
            {
                "name": "senior",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_categ_age_option_ids"
                ).id,
            }
        )

        # food_ranges
        cls.food_range_recovery = cls.env["attribute.option"].create(
            {
                "name": "Recovery",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_food_range_option_id"
                ).id,
            }
        )
        cls.food_range_complete = cls.env["attribute.option"].create(
            {
                "name": "Complete",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_food_range_option_id"
                ).id,
            }
        )

        # indications
        cls.indication_allergy = cls.env["attribute.option"].create(
            {
                "name": "Allergy",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_indication_option_ids"
                ).id,
            }
        )
        cls.indication_oral = cls.env["attribute.option"].create(
            {
                "name": "Oral",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_indication_option_ids"
                ).id,
            }
        )
        cls.indication_digestion = cls.env["attribute.option"].create(
            {
                "name": "Digestion",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_indication_option_ids"
                ).id,
            }
        )

        # Presentation
        cls.presentation_croquette = cls.env["attribute.option"].create(
            {
                "name": "Croquette",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_presentation_option_id"
                ).id,
            }
        )
        cls.presentation_pate_bites = cls.env["attribute.option"].create(
            {
                "name": "Pâté / bites",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_presentation_option_id"
                ).id,
            }
        )
        cls.presentation_granules = cls.env["attribute.option"].create(
            {
                "name": "Granules",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_presentation_option_id"
                ).id,
            }
        )

        # active principles
        cls.active_principle_oestriol = cls.env["attribute.option"].create(
            {
                "name": "Oestriol",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_active_principle_option_ids"
                ).id,
            }
        )
        cls.active_principle_paramyxovirus = cls.env["attribute.option"].create(
            {
                "name": "Paramyxovirus",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_active_principle_option_ids"
                ).id,
            }
        )
        cls.active_principle_grapiprant = cls.env["attribute.option"].create(
            {
                "name": "Grapiprant",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_active_principle_option_ids"
                ).id,
            }
        )

        # administration routes
        cls.active_principle_implant = cls.env["attribute.option"].create(
            {
                "name": "Implant",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_administration_route_option_ids"
                ).id,
            }
        )
        cls.active_principle_sabots = cls.env["attribute.option"].create(
            {
                "name": "Sabots",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_administration_route_option_ids"
                ).id,
            }
        )
        cls.active_principle_vagina = cls.env["attribute.option"].create(
            {
                "name": "Voie vaginale",
                "attribute_id": cls.env.ref(
                    "alc_pim_product.attribute_administration_route_option_ids"
                ).id,
            }
        )

        # category
        cls.category_test = cls.env["product.category"].create(
            {
                "name": "Test category",
                "is_business_unit": False,
                "parent_id": cls.env.ref("product.product_category_all").id,
                "property_cost_method": "average",
            }
        )

        # --- Create products
        cls.product_test_food = cls.env["product.product"].create(
            {
                "name": "Test food",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_ali_divers"
                ).id,
                "description_shop_long": "This is a long shop description for this amazing test food!!!",
                "species_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("alc_product_animal_species.dog").id,
                            cls.env.ref("alc_product_animal_species.cat").id,
                            cls.env.ref("alc_product_animal_species.ferret").id,
                        ],
                    )
                ],
                "animal_size_option_ids": [
                    (
                        6,
                        0,
                        [cls.animale_size_l.id, cls.animale_size_m.id],
                    )
                ],
                "categ_age_option_ids": [
                    (
                        6,
                        0,
                        [cls.categ_age_adult.id, cls.categ_age_junior.id],
                    )
                ],
                "food_range_option_id": cls.food_range_complete.id,
                "indication_option_ids": [
                    (
                        6,
                        0,
                        [
                            cls.indication_allergy.id,
                            cls.indication_digestion.id,
                        ],
                    )
                ],
                "presentation_option_id": cls.presentation_croquette.id,
                "active_principle_option_ids": [
                    (
                        6,
                        0,
                        [
                            cls.active_principle_oestriol.id,
                            cls.active_principle_grapiprant.id,
                        ],
                    )
                ],
            }
        )

        cls.product_vitamines = cls.env["product.product"].create(
            {
                "name": "Vitamines",
                "species_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("alc_product_animal_species.dog").id,
                            cls.env.ref("alc_product_animal_species.cat").id,
                            cls.env.ref("alc_product_animal_species.ferret").id,
                            cls.env.ref("alc_product_animal_species.bee").id,
                            cls.env.ref("alc_product_animal_species.cattle").id,
                            cls.env.ref("alc_product_animal_species.chinchilla").id,
                            cls.env.ref("alc_product_animal_species.horse").id,
                            cls.env.ref("alc_product_animal_species.mouse").id,
                            cls.env.ref("alc_product_animal_species.pigeon").id,
                            cls.env.ref("alc_product_animal_species.pig").id,
                        ],
                    )
                ],
                "species_id": cls.env.ref("alc_product_animal_species.all").id,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_vitamines"
                ).id,
                "active_principle_option_ids": [
                    (
                        6,
                        0,
                        [
                            cls.active_principle_oestriol.id,
                            cls.active_principle_grapiprant.id,
                        ],
                    )
                ],
                "categ_ids": [
                    (
                        6,
                        0,
                        [cls.category_test.id],
                    )
                ],
            }
        )

        cls.product_material = cls.env["product.product"].create(
            {
                "name": "Important material",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_materiel"
                ).id,
            }
        )
