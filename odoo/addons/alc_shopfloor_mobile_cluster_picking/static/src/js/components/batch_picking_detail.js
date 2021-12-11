/**
 * Copyright 2021 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

/* eslint-disable strict */
// Extend batch-picking-detail
const batch_picking_detail_component = Vue.component("batch-picking-detail");
const methods = batch_picking_detail_component.extendOptions.methods;
const detail_fields_method = methods.detail_fields;
const screen_title_method = methods.screen_title;
methods.detail_fields = function() {
  const result = detail_fields_method.bind(this)();
  const new_result = [
    ...result,
    {
      path: "delivery_round.name",
      label: this.$t(
        "alc_shopfloor_mobile_cluster_picking.batch_picking_detail.delivery_round"
      ),
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
