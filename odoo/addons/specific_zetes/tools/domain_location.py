# -*- coding: utf-8 -*-
import re

from domain_interface import DomainInterface, Parameters
from odoo import _

from .. import constants


class Location(DomainInterface):
    EXAMPLE_REQU = (
        "208092661,2.2.3,3iV_101,REQU_LOCATION,58,1,20170207,"
        "073526,584277331622644,000000001625845,,,,"
        "00000000162584500009,,,A,A,1,0,B2,3265295,"
        "00217,,,,,,,,,,,,,,"
    )
    EXAMPLE_RESP = (
        "208092661,2.2.3,3iV_101,RESP_LOCATION,58,1,"
        "20170207,073438,584277331622644,0,,000000001625845,,"
        "000000001625845,,00000000162584500009,,00,A,A,1,0,B2,"
        "95,,000538,,01,3265295,VIRBAC HPM CAT ADULT NEUTERED 3KG"
        ",,,,,,00219,00157,00000,00000,00000,00000,000522,,,,"
    )
    EXAMPLE_RESU = ""
    REQU = (
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "lineId",
        "itemSeqNum",
        "assignmentType",
        "Cri01",
        "Cri02",
        "Cri03",
        "Cri04",
        "Cri05",
        "Cri06",
        "Cri07",
        "Cri08",
        "Cri09",
        "Cri10",
        "Usf01",
        "Usf02",
        "Usf03",
        "Usf04",
        "Usf05",
        "Usf06",
        "Usf07",
        "Usf08",
        "Usf09",
        "Usf10",
    )
    RESP = (
        "respCode",
        "respMsg",
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "lineId",
        "itemSeqNum",
        "locationStatus",
        "lC1",
        "lC2",
        "lC3",
        "lC4",
        "lC5",
        "lCCD",
        "lCBarcode",
        "quantity",
        "promptInfo",
        "unitOfMeasure",
        "productCode",
        "productDescription",
        "productGroupCode",
        "productProperty1",
        "productProperty2",
        "productProperty3",
        "productBarcode",
        "Usf01",
        "Usf02",
        "Usf03",
        "Usf04",
        "Usf05",
        "Usf06",
        "Usf07",
        "Usf08",
        "Usf09",
        "Usf10",
    )
    RESU = ()

    def requ(self, params):
        """
        Check if the location sent in params exist in Odoo.

        Return a list of existing lots for a stock pack operation (lineId).
        This method is used by Zetes when the picker doesn't find the right
        lot or we need quantity available.
        :param params:
        :return:
        """
        result = Parameters(self, action="resp")

        line_id = params.lineId
        if not line_id:
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _("No picking found"),
                }
            )
            return result.format()

        if isinstance(line_id, int):
            line_id = str(line_id)

        line_id_list = line_id.split("_")
        if len(line_id_list) == 2:
            pack_operation_id = int(line_id_list[0])
            lot_id = int(line_id_list[1])
        else:
            pack_operation_id = int(line_id)
            lot_id = None

        pack_op = self.env["stock.pack.operation"].browse(pack_operation_id)
        if not len(pack_op):
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _("No picking found"),
                }
            )
            return result.format()

        product = pack_op.product_id

        # TODO Please remove me later (when dynamic locations will removed)
        shelf = params.Cri03 or ""
        special_shelf_regex = r"0([A-Z])"
        regex_result = re.match(special_shelf_regex, shelf)
        if regex_result:
            shelf = regex_result.group(1)

        location = self.env["stock.location"].search(
            [
                ("zone", "=", params.Cri01),
                ("corridor", "=", params.Cri02),
                ("shelf", "=", shelf),
                ("height", "=", params.Cri04),
                ("box", "=", params.Cri05),
            ],
            limit=1,
        )

        if location:
            # As soon as we get a matching location, we set it in the context
            # of the product to compute the related quantities available.
            product = product.with_context(location=location.id)

        result.update(
            {
                "respCode": constants.RESPONSE_CODE_OK,
                "headerNum": None,
                "productCode": product.default_code,
                "productDescription": product.name,
                "quantity": product.qty_available,  # Total quantity
                "Usf07": product.virtual_available,  # Stock available
            }
        )

        if not location:
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _(
                        "Location %s%s%s%s%s not found"
                        % (
                            params.Cri01,
                            params.Cri02,
                            params.Cri03,
                            params.Cri04,
                            params.Cri05,
                        )
                    ),
                }
            )
            return result.format()

        if (
            pack_op.picking_id.picking_type_id.zetes_picking_type
            == constants.RANGEMENT_ASSIGNMENT
        ):
            if location.kind != "reserve":
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("This location is not a reserve"),
                    }
                )
                return result.format()

            self.env["pack.operation.reserve.rel"].create(
                {
                    "pack_operation_id": pack_op.id,
                    "reserve_location_id": location.id,
                    "lot_id": lot_id,
                }
            )

        # TODO Please remove me later (when dynamic locations will removed)
        shelf_source = location.shelf
        if len(str(shelf_source)) == 1:
            shelf_source = "0%s" % shelf_source

        result.update(
            {
                "lC1": location.zone,
                "lC2": location.corridor,
                "lC3": shelf_source,
                "lC4": location.height,
                "lC5": location.box,
                "lCCD": location.get_checksum(),
            }
        )

        # Search a specific lot
        if params.Cri07:
            specific_lot = self.env["stock.production.lot"].search(
                [("checksum", "=", params.Cri07), ("product_id", "=", product.id)],
                limit=1,
            )

            if specific_lot:
                if specific_lot.is_expired:
                    result.update(
                        {
                            "respCode": constants.RESPONSE_CODE_ERROR,
                            "respMsg": _(
                                "Lot %s has expired. " "Please contact the manager"
                            )
                            % params.Cri07,
                        }
                    )
                    return result.format()
                result.Usf01 = specific_lot.voice_identifier
            else:
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Lot %s not found. " "Please contact the manager")
                        % params.Cri07,
                    }
                )
                return result.format()

        return result.format()

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        There is no resu request for location
        :param params:
        :return:
        """
        return
