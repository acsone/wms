/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
import {PackagingQtyPicker} from "/shopfloor_mobile/static/wms/src/components/packaging-qty-picker.js";

const computed = PackagingQtyPicker.extendOptions.computed;
const qty_color_computed = computed.qty_color;

computed.qty_color = function () {
  const result = qty_color_computed.bind(this)();
  const font_style = "font-weight:950; font-size: 200%; color:rgb(102, 0, 0)";
  const new_result = result + ";" + font_style;
  return new_result;
};

const unit_color_computed = computed.unit_color;

computed.unit_color = function () {
  const result = unit_color_computed.bind(this)();
  const font_style = "font-weight:950; font-size: 200%; color:rgb(102, 0, 0)";
  const is_not_unit = this.opts.uom.id != 1; // Id of unit of measure "unit" is 1.
  const background_style = is_not_unit
    ? "background-color: orangered!important"
    : "background-color:transparent; ";

  const new_result = result + ";" + font_style + ";" + background_style;
  return new_result;
};
