/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const registry_key = "cluster_picking";
const ClusterPickingBase = process_registry.get(registry_key);

const template = ClusterPickingBase.component.template;
ClusterPickingBase.component.template = template.replace(
  '<Screen :screen_info="screen_info">',
  `<Screen :screen_info="screen_info">
   <picking-detail
   v-show="state_in(['start_line', 'scan_destination', 'change_pack_lot', 'stock_issue'])"
   :record="state.data.picking"
   />
`
);
