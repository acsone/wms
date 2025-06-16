from odoo import api, fields, models, tools


class AlcProductCharacteristic(models.Model):
    _name = "alc.product.characteristic"
    _description = "Product Characteristic"

    vector_index = fields.Integer(string="Vector Index", required=True)
    value_res_model = fields.Char(required=True)
    value_res_id = fields.Many2oneReference(
        required=True, model_field="value_res_model"
    )
    field_id = fields.Many2one(
        "ir.model.fields", store=True, ondelete="cascade", string="Field", required=True
    )
    field_weight = fields.Float(required=True, default=1)

    _sql_constraints = [
        (
            "unique_field_value",
            "UNIQUE(field_id, value_res_id)",
            "A field cannot reference the same record of the same model more than once.",
        ),
        (
            "unique_vector_index",
            "UNIQUE(vector_index)",
            "There cannot be two characteristics pointing to the same index in the vector.",
        ),
        (
            "check_vector_index_non_negative",
            "CHECK(vector_index >= 0)",
            "A vector index must be >= 0",
        ),
        (
            "check_field_weight_positive",
            "CHECK(field_weight > 0)",
            "field_weight must be > 0",
        ),
    ]

    @api.model
    def _get_effective_id(self, record):
        """
        Returns the effective integer ID of the given record.

        This method provides a consistent integer identifier for a record,
        whether it has been committed to the database (and thus has a real
        database ID) or is a new record still in the current transaction
        (represented by an Odoo `NewId` object).

        This method prevents issues caused by `models.NewId` objects being coerced into `0`
        when converted to an integer, which can lead to unique constraint violations or other unexpected behavior.
        """
        record.ensure_one()

        if isinstance(record.id, models.NewId):
            return record.id.origin

        return record.id

    def _to_cache_key(self):
        """Returns the cache key for a characteristic from this model."""
        self.ensure_one()
        return (
            self.value_res_model,
            self.value_res_id,
            self.field_id.id,
        )

    def _record_to_cache_key(self, record, field_name):
        """Returns the cache key for a characteristic from another model."""
        field_id = self.env["ir.model.fields"]._get("product.product", field_name).id
        return (record._name, self._get_effective_id(record), field_id)

    @api.model
    @tools.ormcache()
    def _get_vector_index_map(self):
        records = self.search([])
        return {
            r._to_cache_key(): {
                "index": r.vector_index,
                "weight": r.field_weight,
            }
            for r in records
        }

    def _get_empty_index(self):
        """
        Gets an empty index by returning the smallest positive integer in the range [0, max(indices) + 1].

        that is not present in the given list.
        """
        indices = [x["index"] for x in self._get_vector_index_map().values()]
        if not indices:
            return 0
        for i, index in enumerate(sorted(indices)):
            if i != index:
                return i
        return len(indices)

    @api.model
    def _get_vector_index_and_weight(self, record, field_name, field_weight=None):
        """
        Gets the index of the given characteristic in the characteristics vector of product.product.

        This function creates the entry in db if no line exists yet in the table.
        """
        if len(record) != 1:
            raise ValueError(
                f"There should be exactly one record but given {len(record)}."
            )

        index_map = self._get_vector_index_map()
        cache_key = self._record_to_cache_key(record, field_name)
        _, _, field_id = cache_key
        index_and_weight = index_map.get(
            cache_key,
            {
                "index": -1,
                "weight": field_weight if field_weight else 1,
            },
        )
        index = index_and_weight["index"]

        # when index for this characteristic is not yet in db, create the entry
        if index < 0:
            index = self._get_empty_index()
            try:
                self.create(
                    [
                        {
                            "value_res_model": record._name,
                            "value_res_id": self._get_effective_id(record),
                            "field_id": field_id,
                            "field_weight": index_and_weight["weight"],
                            "vector_index": index,
                        }
                    ]
                )
            except Exception as e:
                raise e

        return (index, index_and_weight["weight"])

    @api.model
    def get_vector_indices_and_weights(
        self,
        records,
        fields_names,
        fields_weights=None,
    ):
        """
        Get the indices of the given characteristics in the characteristics vector of product.product.

        This function creates the entries in db if no line exists yet in the table.
        """
        if fields_weights is None:
            fields_weights = [1 for _ in range(len(records))]
        return {
            (r, name): self._get_vector_index_and_weight(r, name, weight)
            for r, name, weight in zip(
                records, fields_names, fields_weights, strict=True
            )
        }

    @api.model
    def get_number_indexed_characteristics(self):
        """Returns the number of characteristics currently indexed (ie the number of records in this model)."""
        return len(self._get_vector_index_map())

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._get_vector_index_map.clear_cache(self)
        return res

    def write(self, vals):
        res = super().write(vals)
        self._get_vector_index_map.clear_cache(self)
        return res

    def unlink(self):
        res = super().unlink()
        self._get_vector_index_map.clear_cache(self)
        return res
