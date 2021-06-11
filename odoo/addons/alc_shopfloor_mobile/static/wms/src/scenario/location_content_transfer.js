/**
 * Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
 * @author Simone Orsi <simahawk@gmail.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {ScenarioBaseMixin} from "/shopfloor_mobile_base/static/wms/src/scenario/mixins.js";
import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const LocationContentTransfer = {
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
                />
            <div class="button-list button-vertical-list full" v-if="state_is('scan_location')">
                <v-row align="center">
                    <v-col class="text-center" cols="12">
                        <v-btn color="default" @click="state.on_back">Back</v-btn>
                    </v-col>
                </v-row>
            </div>
            <get-work
                v-if="state_is('start')"
                v-on:get_work="state.on_get_work"
                v-on:manual_selection="state.on_manual_selection"
                />
            <div v-if="state_in(['start_single', 'scan_destination', 'scan_destination_all']) && wrapped_context().has_records">

                <item-detail-card
                    v-if="wrapped_context().location_src"
                    :key="make_state_component_key(['detail-move-line-loc-src', wrapped_context().location_src.id])"
                    :record="wrapped_context().location_src"
                    :options="{main: true, key_title: 'name', title_action_field: {action_val_path: 'barcode'}}"
                    :card_color="utils.colors.color_for(state_in(['start_single', 'scan_destination', 'scan_destination_all']) ? 'screen_step_done': 'screen_step_todo')"
                    />

                <div v-for="rec in wrapped_context().records">
                    <item-detail-card
                        :key="make_state_component_key(['detail-move-line-product', rec.id, rec.lot && rec.lot.id])"
                        :record="rec"
                        :options="utils.wms.move_line_product_detail_options(rec, {fields: [{path: 'picking.name', label: 'Picking'}]})"
                        :card_color="utils.colors.color_for(state_in(['scan_destination', 'scan_destination_all']) ? 'screen_step_done': 'screen_step_todo')"
                        />

                    <v-card v-if="(rec.type == 'lot' || rec.type == 'product') && state_is('scan_destination')"
                            class="pa-2" :color="utils.colors.color_for('screen_step_todo')">
                        <packaging-qty-picker
                            :key="make_state_component_key(['packaging-qty-picker', rec.id, rec.lot && rec.lot.id])"
                            :options="utils.wms.move_line_qty_picker_options(rec)"
                            />
                    </v-card>

                    <line-actions-popup
                        v-if="!wrapped_context()._multi"
                        :line="rec"
                        :actions="line_actions()"
                        :key="make_state_component_key(['line-actions', rec.id, rec.lot && rec.lot.id])"
                        v-on:action="on_line_action"
                        />
                </div>

                <item-detail-card
                    v-if="wrapped_context().location_dest"
                    :key="make_state_component_key(['detail-move-line-loc-dest', wrapped_context().location_dest.id])"
                    :record="wrapped_context().location_dest"
                    :options="{main: true, key_title: 'name', title_action_field: {action_val_path: 'barcode'}}"
                    :card_color="utils.colors.color_for('screen_step_todo')"
                    />
            </div>
            <line-stock-out
                v-if="state_is('stock_issue')"
                v-on:confirm_stock_issue="state.on_confirm_stock_issue"
                />
            <div class="button-list button-vertical-list full">
                <v-row align="center" v-if="state_is('scan_destination_all')">
                    <v-col class="text-center" cols="12">
                        <btn-action @click="state.on_split_by_line">Process by line</btn-action>
                    </v-col>
                </v-row>
            </div>
        </Screen>
        `,
  methods: {
    screen_title: function() {
      if (!this.has_picking()) return this.menu_item().name;
      return this.current_picking().name;
    },
    // TODO: if we have this working we can remove the picking detail?
    current_doc: function() {
      const picking = this.current_picking();
      return {
        record: picking,
        identifier: picking.name,
      };
    },
    // TODO: ask Joél if this is needed
    current_picking: function() {
      const data = this.state_get_data("start");
      if (_.isEmpty(data) || _.isEmpty(data.operation.picking)) {
        return {};
      }
      return data.operation.picking;
    },
    has_picking: function() {
      return !_.isEmpty(this.current_picking());
    },
    /**
     * As we can get `operation` for single items
     * and `operations`  for multiple items,
     * this function tries to make such data homogenous.
     * We'll work alway with multiple records and loop on them.
     * TODO: this should be computed to be cached.
     */
    wrapped_context: function() {
      const data = this.state.data;
      let res = {
        has_records: true,
        records: [].concat(data.operations || []),
        location_src: null,
        location_dest: null,
        _multi: true,
      };
      if (_.isEmpty(res.records)) {
        res.records = [data.operation];
        res._multi = false;
      }
      res.has_records = res.records.length > 0;
      res.location_src = res.has_records ? res.records[0].location_src : null;
      res.location_dest = res.has_records ? res.records[0].location_dest : null;
      return res;
    },
    move_line_detail_list_options: function(move_line) {
      return this.utils.wms.move_line_product_detail_options(move_line, {
        loud_labels: true,
        fields_blacklist: ["product.qty_available"],
        fields: [{path: "location_src.name", label: "From"}],
      });
    },
    line_actions: function() {
      let actions = [
        {name: "Postpone line", event_name: "action_postpone"},
        {name: "Declare stock out", event_name: "action_stock_out"},
        {name: "Declare overstock", event_name: "action_overstock"},
      ];
      return actions;
    },
    // Common actions
    on_line_action: function(action) {
      this["on_" + action.event_name].call(this);
    },
    on_action_postpone: function() {
      let endpoint, endpoint_data;
      const data = this.state.data;
      endpoint = "postpone_line";
      endpoint_data = {
        location_id: data.operation.location_src.id,
        operation_id: data.operation.id,
      };

      this.wait_call(this.odoo.call(endpoint, endpoint_data));
    },

    on_action_overstock: function() {
      let endpoint, endpoint_data;
      const data = this.state.data;
      endpoint = "overstock_line";
      endpoint_data = {
        location_id: data.operation.location_src.id,
        operation_id: data.operation.id,
      };

      this.wait_call(this.odoo.call(endpoint, endpoint_data));
    },

    on_action_stock_out: function() {
      this.state_set_data(this.state.data, "stock_issue");
      this.state_to("stock_issue");
    },
  },
  data: function() {
    const self = this;
    return {
      usage: "location_content_transfer",
      initial_state_key: "start",
      scan_destination_qty: 0,
      states: {
        start: {
          on_get_work: evt => {
            this.wait_call(this.odoo.call("start_or_recover"));
          },
          on_manual_selection: evt => {
            this.state_to("scan_location");
          },
        },
        scan_location: {
          display_info: {
            title: "Start by scanning a location",
            scan_placeholder: "Scan location",
          },
          on_scan: scanned => {
            this.wait_call(this.odoo.call("scan_location", {barcode: scanned.text}));
          },
          on_back: evt => {
            this.state_to("start");
            this.reset_notification();
          },
        },
        scan_destination_all: {
          display_info: {
            title: "Scan destination location for all items",
            scan_placeholder: "Scan location",
          },
          on_scan: scanned => {
            const data = this.state.data;
            this.wait_call(
              this.odoo.call("set_destination_all", {
                location_id: data.location.id,
                barcode: scanned.text,
                confirmation: data.confirmation_required,
              })
            );
          },
          on_split_by_line: () => {
            const location = this.state.data.location;
            this.wait_call(this.odoo.call("go_to_single", {location_id: location.id}));
          },
        },
        start_single: {
          display_info: {
            scan_placeholder: "Scan pack / product / lot",
          },
          on_scan: scanned => {
            let endpoint, endpoint_data;
            const data = this.state.data;
            endpoint = "scan_line";
            endpoint_data = {
              operation_id: data.operation.id,
              location_id: data.operation.location_src.id,
              barcode: scanned.text,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
        scan_destination: {
          enter: () => {
            this.reset_notification();
          },
          display_info: {
            title: "Set a qty and scan destination location",
            scan_placeholder: "Scan location",
          },
          events: {
            qty_edit: "on_qty_update",
          },
          on_qty_update: qty => {
            this.scan_destination_qty = parseInt(qty, 10);
          },
          on_scan: scanned => {
            let endpoint, endpoint_data;
            const data = this.state.data;

            endpoint = "set_destination_line";
            endpoint_data = {
              operation_id: data.operation.id,
              location_id: data.operation.location_src.id,
              barcode: scanned.text,
              confirmation: data.confirmation_required,
              quantity: this.scan_destination_qty,
            };
            if (data.operation.type === "lot") {
              endpoint_data.lot_id = data.operation.lot.id;
            }

            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
          on_split_by_line: () => {
            const location = this.state.data.operations[0].location_src;
            this.wait_call(this.odoo.call("go_to_single", {location_id: location.id}));
          },
        },
        stock_issue: {
          enter: () => {
            this.reset_notification();
          },
          on_confirm_stock_issue: () => {
            let endpoint, endpoint_data;
            const data = this.state.data;

            endpoint = "stock_out_line";
            endpoint_data = {
              operation_id: data.operation.id,
              location_id: data.operation.location_src.id,
            };
            this.wait_call(this.odoo.call(endpoint, endpoint_data));
          },
        },
      },
    };
  },
};

process_registry.add("location_content_transfer", LocationContentTransfer);

export default LocationContentTransfer;
