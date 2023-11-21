from extendable_pydantic import StrictExtendableBaseModel


class Manufacturer(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_res_partner(cls, odoo_rec):
        return cls.model_construct(id=odoo_rec.id, name=odoo_rec.name)
