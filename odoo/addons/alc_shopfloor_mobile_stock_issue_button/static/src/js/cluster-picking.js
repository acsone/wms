/**
 * Copyright 2022 ACSONE SA/NV
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
  const scan_dest_fct = result.states.scan_destination;
  const self = this;
  scan_dest_fct.on_action_stock_out = function () {
    self.state_set_data(self.state.data, "stock_issue");
    self.state_to("stock_issue");
  };
  result.states.scan_destination = scan_dest_fct;
  return result;
};

const template = ClusterPickingBase.component.template;
ClusterPickingBase.component.template = template.replace(
  "</Screen>",
  `
    <div v-if="state_is('scan_destination')">
    <div class="button-list button-vertical-list full mt-10">
        <v-row align="center">
            <v-col class="text-center" cols="12">
                <v-btn @click="state.on_action_stock_out">
                {{ $t('cluster_picking.btn.action.stock_issue.title') }}
                </v-btn>
            </v-col>
        </v-row>
    </div>
    </div>
</Screen>
`
);
ClusterPickingBase.component.data = data;
