from collections.abc import Hashable

from odoo import api, fields, models, tools


class AlcProductCharacteristic(models.Model):
    _name = "alc.product.characteristic"
    _description = "Product Characteristic"

    vector_index = fields.Integer(string="Vector Index", required=True)
    characteristic_res_model = fields.Char(required=True)
    characteristic_res_id = fields.Many2oneReference(
        model_field="characteristic_res_model"
    )
    # characteristic_weight = fields.Float(required=True, default=1) -> #TODO: think about the necessary changes to support this field in the methods below

    _sql_constraints = [
        (
            "unique_model_and_id",
            "unique(characteristic_res_model, characteristic_res_id)",
            "A characteristic cannot reference the same record in the same model more than once.",
        ),
        (
            "unique_vector_index",
            "unique(vector_index)",
            "There cannot be two characteristics pointing to the same index in the vector.",
        ),
        (
            "check_vector_index_positive",
            "vector_index > 0",
            "A vector index must be > 0",
        ),
        # (
        #     "check_characteristic_weight_positive",
        #     "characteristic_weight > 0",
        #     "characteristic_weight must be > 0",
        # ),
    ]

    def _to_cache_key(self) -> Hashable:
        """Returns the cache key for a characteristic from this model."""
        self.ensure_one()
        return (self.characteristic_res_model, self.characteristic_res_id)

    def _record_to_cache_key(self, record) -> Hashable:
        """Returns the cache key for a characteristic from another model."""
        return (record._name, record.id)

    @api.model
    @tools.ormcache()
    def _get_vector_index_map(self):
        records = self.search([])
        return {r._to_cache_key(): r.vector_index for r in records}

    def _get_empty_index(self):
        """
        Get an empty index by returning the smallest positive integer in the range [0, max(indices) + 1].

        that is not present in the given list.
        """
        indices = self._get_vector_index_map().values()
        if not indices:
            return 0
        for i, index in enumerate(sorted(indices)):
            if i != index:
                return i
        return len(indices)

    @api.model
    def _get_vector_index(self, record):
        """Get the index of the given characteristic in the characteristics vector of product.product.

        This function creates the enrty in db if no line exists yet in the table.
        """
        if len(record) != 1:
            raise ValueError(
                f"There should be exactly one record but given {len(record)}."
            )

        index_map = self._get_vector_index_map()
        index = index_map.get(self._record_to_cache_key(record), -1)

        # when index for this characteristic is not yet in db, create the entry
        if index < 0:
            index = self._get_empty_index()
            self.create(
                [
                    {
                        "characteristic_res_model": record._name,
                        "characteristic_res_id": record.id,
                        "vector_index": index,
                    }
                ]
            )

        return index

    @api.model
    def get_vector_indices(self, records):
        """Get the indices of the given characteristics in the characteristics vector of product.product.

        This function creates the enrties in db if no line exists yet in the table.
        """
        return {r: self._get_vector_index(r) for r in records}

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
