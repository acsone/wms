/**
 * Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
 * @author Simone Orsi <simahawk@gmail.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {ScenarioBaseMixin} from "/shopfloor_mobile_base/static/wms/src/scenario/mixins.js";
import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const ClusterPicking = {
  mixins: [ScenarioBaseMixin],
  template: `
        <Screen :screen_info="screen_info">
            <template v-slot:header>
                <state-display-info :info="state.display_info" v-if="state.display_info"/>
            </template>
            <searchbar
                v-if="state.on_scan"
                v-on:found="on_scan"
                :input_placeholder="search_input_placeholder"
                :input_type="searchbar_input_type"
                />
            <get-work
                v-if="state_is('start')"
                v-on:get_work="state.on_get_work"
                v-on:manual_selection="state.on_manual_selection"
                />
            <batch-picking-detail
                v-if="state_is('confirm_start')"
                :record="state.data"
                v-on:confirm="state.on_confirm"
                v-on:cancel="state.on_cancel"
                />
            <batch-picking-line-detail
                v-if="state_in(['start_operation', 'scan_destination', 'change_pack_lot', 'stock_issue'])"
                :line="state.data"
                :article-scanned="state_is('scan_destination')"
                :show-qty-picker="state_is('scan_destination')"
                />
            <batch-picking-line-actions
                v-if="state_is('start_operation')"
                v-on:action="state.on_action"
                :line="state_get_data('start_operation')"
                />
            <div v-if="state_is('scan_destination')">
                <div class="button-list button-vertical-list full mt-10">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <v-btn @click="state.on_action_full_bin">
                            {{ $t('cluster_picking.btn.action.full_bin.title') }}
                            </v-btn>
                        </v-col>
                    </v-row>
                </div>
            </div>
            <stock-zero-check
                v-if="state_is('zero_check')"
                v-on:action="state.on_action"
                />

            <line-stock-out
                v-if="state_is('stock_issue')"
                v-on:confirm_stock_issue="state.on_confirm_stock_issue"
                />
            <div v-if="state_is('manual_selection')">
                <manual-select
                    v-on:select="state.on_select"
                    v-on:back="state.on_back"
                    :records="state.data.records"
                    :list_item_fields="manual_select_picking_fields"
                    />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <v-btn color="default" @click="state.on_back">Back</v-btn>
                        </v-col>
                    </v-row>
                </div>
            </div>

            <div class="unload-all" v-if="state_is('unload_all')">
                <v-card class="main">
                    <v-card-title>
                        <div class="main-info">
                            <div class="destination">
                                <span class="label">Destination:</span>
                                {{ state.data.location_dest.name }}
                            </div>
                        </div>
                    </v-card-title>
                </v-card>
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <v-btn color="primary" @click="$emit('action', 'action_split')">Split [TODO]</v-btn>
                        </v-col>
                    </v-row>
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-back />
                        </v-col>
                    </v-row>
                </div>
            </div>

        </Screen>
    `,
  computed: {
    searchbar_input_type: function() {
      return "string";
    },
    manual_select_picking_fields: function() {
      return [
        {path: "picking_count", label: "Operations"},
        {path: "move_line_count", label: "Lines"},
      ];
    },
  },
  methods: {
    screen_title: function() {
      if (_.isEmpty(this.current_batch()) || this.state_is("confirm_start"))
        return this.menu_item().name;
      let title = this.current_batch().name;
      const picking = this.current_picking();
      if (picking) {
        title += " > " + picking.name;
      }
      return title;
    },
    current_batch: function() {
      return this.state_get_data("confirm_start");
    },
    current_picking: function() {
      const data = this.state_get_data("start_operation") || {};
      if (!data.picking) {
        return null;
      }
      return data.picking;
    },
    current_doc: function() {
      const picking = this.current_picking();
      if (!picking) {
        return {};
      }
      return {
        record: picking,
        identifier: picking.name,
      };
    },
    action_full_bin: function() {
      this.wait_call(
        this.odoo.call("prepare_unload", {
          picking_batch_id: this.current_batch().id,
        })
      );
    },
  },
  data: function() {
    // TODO: add a title to each screen
    return {
      usage: "cluster_picking",
      initial_state_key: "start",
      scan_destination_qty: 0,
      states: {
        init: {
          enter: () => {
            this.wait_call(this.odoo.call("find_existing_batch"));
          },
        },
        start: {
          on_get_work: evt => {
            this.wait_call(this.odoo.call("find_batch"));
          },
          on_manual_selection: evt => {
            this.wait_call(this.odoo.call("list_batch"));
          },
        },
        manual_selection: {
          on_back: () => {
            this.state_to("start");
            this.reset_notification();
          },
          on_select: selected => {
            this.wait_call(
              this.odoo.call("select", {
                picking_batch_id: selected.id,
              })
            );
          },
          display_info: {
            title: this.$t("cluster_picking.manual_selection.title"),
          },
        },
        confirm_start: {
          on_confirm: () => {
            this.wait_call(
              this.odoo.call("confirm_start", {
                picking_batch_id: this.current_batch().id,
              })
            );
          },
          on_cancel: () => {
            const self = this;
            this.wait_call(
              this.odoo.call("unassign", {
                picking_batch_id: this.current_batch().id,
              })
            ).then(function() {
              self.state_reset_data_all();
            });
          },
        },
        start_operation: {
          display_info: {
            title: this.$t("cluster_picking.start_operation.title"),
            scan_placeholder: this.$t(
              "cluster_picking.start_operation.scan_placeholder"
            ),
          },
          // Here we have to use some info sent back from `select`
          // or from `find_batch` that we pass to scan line
          on_scan: scanned => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "scan_line";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
              barcode: scanned.text,
            };
            if (data.lot) {
              endpoint_data.lot_id = data.lot.id;
            }
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
          // Additional actions
          on_action: action => {
            this.state["on_" + action].call(this);
          },
          on_action_full_bin: () => {
            this.action_full_bin();
          },
          on_action_skip_operation: () => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "skip_operation";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
          on_action_stock_out: () => {
            this.state_set_data(this.state.data, "stock_issue");
            this.state_to("stock_issue");
          },
          on_action_change_pack_or_lot: () => {
            this.state_set_data(this.state.data, "change_pack_lot");
            this.state_to("change_pack_lot");
          },

          on_action_print_label: () => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "print_label";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
            };
            if (data.lot) {
              endpoint_data.lot_id = data.lot.id;
            }
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        scan_destination: {
          display_info: {
            title: this.$t("cluster_picking.scan_destination.title"),
            scan_placeholder: this.$t(
              "cluster_picking.scan_destination.scan_placeholder"
            ),
          },
          events: {
            qty_edit: "on_qty_edit",
          },
          enter: () => {
            this.reset_notification();
            // TODO: shalle we hook v-model for qty input straight to the state data?
            this.scan_destination_qty = this.state_get_data("start_operation").quantity;
          },
          on_qty_edit: qty => {
            this.scan_destination_qty = parseInt(qty, 10);
          },
          on_scan: scanned => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "scan_destination_pack";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
              barcode: scanned.text,
              quantity: this.scan_destination_qty,
            };
            if (data.lot) {
              endpoint_data.lot_id = data.lot.id;
            }
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
          on_action_full_bin: () => {
            this.action_full_bin();
          },
        },
        zero_check: {
          on_action: action => {
            this.state["on_" + action].call(this);
          },
          on_action_confirm_zero: () => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "is_zero";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
              zero: true,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
          on_action_confirm_not_zero: () => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "is_zero";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
              zero: false,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        unload_all: {
          display_info: {
            title: this.$t("cluster_picking.unload_all.title"),
            scan_placeholder: this.$t("scan_placeholder_translation"),
          },
          on_scan: (scanned, confirmation = false) => {
            this.state_set_data({location_barcode: scanned.text});
            let endpoint, endpoint_data;
            endpoint = "set_destination_all";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              barcode: scanned.text,
              confirmation: confirmation,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
          on_action_split: () => {
            let endpoint, endpoint_data;
            endpoint = "unload_split";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        confirm_unload_all: {
          display_info: {
            title: this.$t("cluster_picking.confirm_unload_all.title"),
            scan_placeholder: this.$t("scan_placeholder_translation"),
          },
          on_user_confirm: answer => {
            // TODO: check if this used
            // -> no flag is set to enable the confirmation dialog,
            // we only display a message, unlike `confirm_start`
            if (answer == "yes") {
              // Reuse data from unload_all
              const scan_data = this.state_get_data("unload_all");
              this.state.on_scan(scan_data.location_barcode, true);
            } else {
              this.state_to("scan_destination");
            }
          },
          on_scan: (scanned, confirmation = true) => {
            this.on_state_exit();
            // FIXME: use state_load or traverse the state
            // this.current_state_key = "unload_all";
            // this.state.on_scan(scanned, confirmation);
            this.states["unload_all"].on_scan(scanned, confirmation);
          },
        },
        unload_single: {
          display_info: {
            title: this.$t("cluster_picking.unload_single.title"),
            scan_placeholder: this.$t("cluster_picking.unload_single.scan_placeholder"),
          },
          on_scan: scanned => {
            const data = this.state.data;
            let endpoint, endpoint_data;
            endpoint = "unload_scan_pack";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              package_id: data.package.id,
              barcode: scanned.text,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        unload_set_destination: {
          display_info: {
            title: this.$t("cluster_picking.unload_set_destination.title"),
            scan_placeholder: this.$t("scan_placeholder_translation"),
          },
          on_scan: scanned => {
            const data = this.state.data;
            let endpoint, endpoint_data;
            endpoint = "unload_scan_destination";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              package_id: data.package.id,
              barcode: scanned.text,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        confirm_unload_set_destination: {
          display_info: {
            title: this.$t("cluster_picking.confirm_unload_set_destination.title"),
            scan_placeholder: this.$t("scan_placeholder_translation"),
          },
          on_scan: scanned => {
            const data = this.state.data;
            let endpoint, endpoint_data;
            endpoint = "unload_scan_destination";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              package_id: data.package.id,
              barcode: scanned.text,
              confirmation: true,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        change_pack_lot: {
          display_info: {
            title: this.$t("cluster_picking.change_pack_lot.title"),
            scan_placeholder: this.$t(
              "cluster_picking.change_pack_lot.scan_placeholder"
            ),
          },
          on_scan: scanned => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "change_pack_lot";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
              barcode: scanned.text,
            };
            if (data.lot) {
              endpoint_data.lot_id = data.lot.id;
            }
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        stock_issue: {
          enter: () => {
            this.reset_notification();
          },
          on_confirm_stock_issue: () => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "stock_issue";
            endpoint_data = {
              picking_batch_id: this.current_batch().id,
              operation_id: data.id,
            };
            if (data.lot) {
              endpoint_data.lot_id = data.lot.id;
            }
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
      },
    };
  },
};

process_registry.add("cluster_picking", ClusterPicking);

export default ClusterPicking;
