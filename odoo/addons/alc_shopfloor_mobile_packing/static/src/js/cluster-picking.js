/**
 * Copyright 2021 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const registry_key = "cluster_picking";
const ClusterPickingBase = process_registry.get(registry_key);

let template = ClusterPickingBase.component.template;
ClusterPickingBase.component.template = template.replace(
  "</Screen>",
  `
    <pack-picking-detail
         v-if="state_is('pack_picking')"
         :record="state.data"
    />

</Screen>
`
);

// Keep the pointer to the orginal method
let data_result_method = ClusterPickingBase.component.data;

// Replace the data method with our new method to add
// our new state
let component = ClusterPickingBase.component;
let data = function() {
  // we must bin the original method to this to put it into
  // the object context
  let result = data_result_method.bind(this)();
  // add our new state
  result.states.pack_picking = {
    display_info: {
      title: this.$t("cluster_picking.put_in_pack.title"),
      scan_placeholder: this.$t("cluster_picking.put_in_pack.scan_placeholder"),
    },
    on_scan: scanned => {
      let endpoint, endpoint_data;
      const data = this.state.data;
      endpoint = "put_in_pack";
      endpoint_data = {
        picking_batch_id: this.current_batch().id,
        picking_id: data.id,
        nbr_packages: parseInt(scanned.text, 10),
      };
      this.wait_call(this.odoo.call(endpoint, endpoint_data));
    },
  };
  return result;
};
ClusterPickingBase.component.data = data;
