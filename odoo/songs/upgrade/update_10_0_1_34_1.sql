-- copy vet depot number for non vet into.
-- depot number is APB Authorization instead.

UPDATE res_partner SET apb_authorization = vet_depot_number
  -- specific_partner.partner_category_veterinary is id 1
  -- we search for non veterinary
  WHERE alcyon_category_id != 1
    AND vet_depot_number IS NOT NULL
    AND apb_authorization IS NULL;
