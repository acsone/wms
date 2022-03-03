/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
import {PackagingQtyPicker} from "/alc_shopfloor_mobile/static/wms/src/components/packaging-qty-picker.js";

const computed = PackagingQtyPicker.extendOptions.computed;
const qty_color_computed = computed.qty_color;

computed.qty_color = function() {
  const result = qty_color_computed.bind(this)();
  const font_style =
    this.qty_todo > 1
      ? "font-weight:950; font-size: 200%; color:rgb(102, 0, 0)"
      : "font-weight:normal ; font-size: 100%; color:black";
  const new_result = result + ";" + font_style;
  return new_result;
};
