/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const registry_key = "cluster_picking";
const ClusterPickingBase = process_registry.get(registry_key);

let template = ClusterPickingBase.component.template;
ClusterPickingBase.component.template = template.replace(
  "</Screen>",
  `
        <div class="button-list button-vertical-list full" v-if="state_is('change_pack_lot')">
        <v-row align="center">
            <v-col class="text-center" cols="12">
                <btn-back />
            </v-col>
        </v-row>
        </div>
 </Screen>
 `
);
