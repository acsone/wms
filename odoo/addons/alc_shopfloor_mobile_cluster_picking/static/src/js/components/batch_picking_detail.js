/**
 * Copyright 2021 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

// Extend batch-picking-detail
const batch_picking_detail_component = Vue.component("batch-picking-detail");
const methods = batch_picking_detail_component.extendOptions.methods;
const detail_fields_method = methods.detail_fields;
methods.detail_fields = function () {
  const result = detail_fields_method.bind(this)();
  const new_result = [
    ...result,
    {
      path: "release_channels",
      label: this.$t(
        "alc_shopfloor_mobile_cluster_picking.batch_picking_detail.release_channels"
      ),
      renderer: function (rec, field) {
        return rec.release_channels.map((d) => d.name).join(" | ");
      },
    },
    {
      path: "device",
      label: this.$t(
        "alc_shopfloor_mobile_cluster_picking.batch_picking_detail.device"
      ),
    },
  ];
  return new_result;
};
