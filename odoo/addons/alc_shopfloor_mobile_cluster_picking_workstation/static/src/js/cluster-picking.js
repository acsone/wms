/**
 * Copyright 2021 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const registry_key = "cluster_picking";
const ClusterPickingBase = process_registry.get(registry_key);

const data_result_method = ClusterPickingBase.component.data;
const data = function () {
  // We must bin the original method to this to put it into
  // the object context
  const result = data_result_method.bind(this)();
  // Add our new state
  result.states.scan_workstation = {
    display_info: {
      title: this.$t("cluster_picking.select_workstation.title"),
      scan_placeholder: this.$t("cluster_picking.select_workstation.scan_placeholder"),
    },
    on_scan: (scanned) => {
      let endpoint, endpoint_data;
      endpoint = "scan_workstation";
      endpoint_data = {
        picking_batch_id: this.current_batch().id,
        barcode: scanned.text,
      };
      this.wait_call(this.odoo.call(endpoint, endpoint_data));
    },
  };
  return result;
};

ClusterPickingBase.component.data = data;
