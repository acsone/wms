import {ScenarioBaseMixin} from "./mixins.js";
import {process_registry} from "../services/process_registry.js";

export var ZonePicking = Vue.component("zone-picking", {
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
            <div v-if="state_is('select_picking_type')">
                <manual-select
                    v-on:select="state.on_select"
                    :records="state.data.picking_types"
                    :list_item_fields="manual_select_picking_type_fields()"
                    :options="{showActions: false}"
                    />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-back />
                        </v-col>
                    </v-row>
                </div>
            </div>

            <div v-if="state_is('select_line')">
                <manual-select
                    :records="state.data.move_lines"
                    :options="select_line_move_line_detail_options()"
                    :key="make_state_component_key(['manual-select'])"
                    />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="toggle_sort_lines_by()">{{ sort_lines_by_btn_label }}</btn-action>
                        </v-col>
                    </v-row>
                    <!-- TODO: this btn should be available only if there are lines already processed -->
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="state.on_unload_at_destination()">Unload at destination</btn-action>
                        </v-col>
                    </v-row>
                </div>
            </div>

            <detail-picking
                v-if="state_is('set_line_destination')"
                :record="state.data.move_line.picking"
                :card_color="utils.colors.color_for('screen_step_done')"
                />
            <item-detail-card
                v-if="state_in(['set_line_destination', 'change_pack_lot'])"
                :key="make_state_component_key(['detail-move-line-loc', state.data.move_line.id])"
                :record="state.data.move_line"
                :options="{main: true, key_title: 'location_src.name', title_action_field: {action_val_path: 'location_src.barcode'}}"
                :card_color="utils.colors.color_for('screen_step_done')"
                />
            <item-detail-card
                v-if="state_in(['set_line_destination', 'stock_issue', 'change_pack_lot'])"
                :key="make_state_component_key(['detail-move-line-product', state.data.move_line.id])"
                :record="state.data.move_line"
                :options="utils.misc.move_line_product_detail_options(state.data.move_line, {fields: [{path: 'picking.name', label: 'Picking'}]})"
                :card_color="utils.colors.color_for(state_in(['set_line_destination']) ? 'screen_step_done': 'screen_step_todo')"
                />
            <v-card v-if="state_in(['set_line_destination', 'change_pack_lot'])"
                    class="pa-2" :color="utils.colors.color_for('screen_step_todo')">
                <packaging-qty-picker :options="utils.misc.move_line_qty_picker_options(state.data.move_line)" />
            </v-card>
            <item-detail-card
                v-if="state_in(['change_pack_lot'])"
                :key="make_state_component_key(['detail-move-line-dest-pack', state.data.move_line.id])"
                :record="state.data.move_line"
                :options="{main: true, key_title: 'package_dest.name'}"
                :card_color="utils.colors.color_for('screen_step_todo')"
                />
            <div v-if="state_is('set_line_destination')">
                <line-actions-popup
                    :line="state.data.move_line"
                    :actions="[
                        {name: 'Declare stock out', event_name: 'action_stock_out'},
                        {name: 'Change pack or lot', event_name: 'action_change_pack_lot'},
                    ]"
                    :key="make_state_component_key(['line-actions', state.data.move_line.id])"
                    v-on:action="state.on_action"
                    />
            </div>

            <div v-if="state_in(['unload_all'])">
                <picking-summary
                    :record="state.data.move_lines[0].picking"
                    :records="state.data.move_lines"
                    :records_grouped="picking_summary_records_grouped(state.data.move_lines)"
                    :list_options="picking_summary_move_line_list_options(state.data.move_lines)"
                    :key="make_state_component_key(['picking-summary'])"
                    />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="state.on_action_split()">Split</btn-action>
                        </v-col>
                    </v-row>
                </div>
            </div>

            <div v-if="state_in(['unload_single', 'unload_set_destination'])">
                <user-information
                    v-if="state.data.full_order_picking"
                    :message="{body: 'Full order picking, no more operation.'}"
                    />
                <picking-summary
                    :record="state.data.move_line.picking"
                    :records="[state.data.move_line]"
                    :records_grouped="picking_summary_records_grouped([state.data.move_line])"
                    :list_options="picking_summary_move_line_list_options([state.data.move_line])"
                    :key="make_state_component_key(['picking-summary'])"
                    />
                <item-detail-card
                    :key="make_state_component_key(['detail-move-line-dest-pack', state.data.move_line.id])"
                    :record="state.data.move_line"
                    :options="{main: true, key_title: 'package_dest.name'}"
                    :card_color="utils.colors.color_for('screen_step_todo')"
                    class="mt-2"
                    />
            </div>

            <stock-zero-check
                v-if="state_is('zero_check')"
                v-on:action="state.on_action"
                />

            <line-stock-out
                v-if="state_is('stock_issue')"
                v-on:confirm_stock_issue="state.on_confirm_stock_issue"
                />

        </Screen>
        `,
    methods: {
        screen_title: function() {
            const record = this.current_picking_type();
            if (!record) return this.menu_item().name;
            return record.name;
        },
        // TODO: if we have this working we can remove the picking detail?
        current_doc: function() {
            const record = this.current_picking_type();
            return {
                record: record,
            };
        },
        current_picking_type: function() {
            if (
                ["start", "scan_location", "select_picking_type"].includes(
                    this.current_state_key
                )
            ) {
                return {};
            }
            const data = this.state_get_data("select_line");
            if (_.isEmpty(data) || _.isEmpty(data.picking_type)) {
                return {};
            }
            return data.picking_type;
        },
        current_zone_location: function() {
            if (["start", "scan_location"].includes(this.current_state_key)) {
                return {};
            }
            const data = this.state_get_data("select_picking_type");
            if (_.isEmpty(data) || _.isEmpty(data.zone_location)) {
                return {};
            }
            return data.zone_location;
        },
        manual_select_picking_type_fields: function() {
            return [
                {path: "lines_count", renderer: this.render_lines_count},
                {
                    path: "priority_lines_count",
                    renderer: this.render_priority_lines_count,
                },
            ];
        },
        render_lines_count(record, field) {
            return this.$t("picking_type.lines_count", record);
        },
        render_priority_lines_count(record, field) {
            return this.$t("picking_type.priority_lines_count", record);
        },
        select_line_move_line_detail_options: function() {
            let options = {
                key_title: "location_src.name",
                group_color: this.utils.colors.color_for("screen_step_todo"),
                title_action_field: {action_val_path: "product.barcode"},
                showActions: false,
                list_item_options: {
                    bold_title: true,
                    fields: [
                        {path: "product.display_name"},
                        {path: "package_src.name", label: "Pack"},
                        {path: "lot.name", label: "Lot"},
                        {
                            path: "priority",
                            render_component: "priority-widget",
                            render_options: function(record) {
                                return {priority: parseInt(record.priority || "0", 10)};
                            },
                        },
                    ],
                },
            };
            return options;
        },
        select_line_move_line_records_grouped(move_lines) {
            return this.utils.misc.group_lines_by_location(move_lines, {});
        },
        toggle_sort_lines_by() {
            this.order_lines_by =
                this.order_lines_by == "priority" ? "location" : "priority";
            return this.list_move_lines(this.current_picking_type().id);
        },
        list_move_lines(picking_type_id) {
            return this.wait_call(
                this.odoo.call("list_move_lines", {
                    zone_location_id: this.current_zone_location().id,
                    picking_type_id: picking_type_id,
                    order: this.order_lines_by,
                })
            );
        },
        scan_source(barcode) {
            return this.wait_call(
                this.odoo.call("scan_source", {
                    zone_location_id: this.current_zone_location().id,
                    picking_type_id: this.current_picking_type().id,
                    barcode: barcode,
                })
            );
        },
        picking_summary_records_grouped(move_lines) {
            const self = this;
            return this.utils.misc.group_lines_by_location(move_lines, {
                group_key: "location_dest",
                // group_no_title: true,
                prepare_records: _.partialRight(
                    this.utils.misc.group_by_pack,
                    "package_src"
                ),
            });
        },
        picking_summary_move_line_list_options: function(move_lines) {
            return {
                group_color: this.state_in(["unload_set_destination"])
                    ? this.utils.colors.color_for("screen_step_done")
                    : this.utils.colors.color_for("screen_step_todo"),
                list_item_options: {
                    actions: [],
                    fields: this.picking_summary_move_line_detail_fields(),
                    list_item_klass_maker: this.utils.misc.move_line_color_klass,
                },
            };
        },
        picking_summary_move_line_detail_fields: function() {
            return [{path: "package_src.name", klass: "loud"}];
        },
    },
    computed: {
        sort_lines_by_btn_label() {
            return this.order_lines_by == "priority"
                ? this.$t("order_lines_by.location")
                : this.$t("order_lines_by.priority");
        },
    },
    data: function() {
        return {
            usage: "zone_picking",
            initial_state_key: "scan_location",
            order_lines_by: "priority",
            states: {
                scan_location: {
                    display_info: {
                        title: "Start by scanning a location",
                        scan_placeholder: "Select a zone",
                    },
                    on_scan: scanned => {
                        this.wait_call(
                            this.odoo.call("scan_location", {barcode: scanned.text})
                        );
                    },
                },
                select_picking_type: {
                    display_info: {
                        title: "Select operation type",
                    },
                    on_select: selected => {
                        this.list_move_lines(selected.id);
                    },
                },
                select_line: {
                    display_info: {
                        title: "Select move",
                        scan_placeholder: "Scan pack or location",
                    },
                    events: {
                        select: "on_select",
                    },
                    on_scan: scanned => {
                        this.scan_source(scanned.text);
                    },
                    on_select: selected => {
                        this.scan_source(selected.barcode || selected.name);
                    },
                    on_unload_at_destination: () => {
                        this.wait_call(
                            this.odoo.call("prepare_unload", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                            })
                        );
                    },
                },
                set_line_destination: {
                    display_info: {
                        title: "Set destination",
                        scan_placeholder: "Scan location or package",
                    },
                    on_scan: scanned => {
                        const data = this.state.data;
                        this.wait_call(
                            this.odoo.call("set_destination", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                                move_line_id: data.id,
                                barcode: scanned.text,
                                confirmation: data.confirmation_required,
                            })
                        );
                    },
                    on_action: action => {
                        this.state["on_" + action.event_name].call(this);
                    },
                    on_action_stock_out: () => {
                        this.state_set_data(this.state.data, "stock_issue");
                        this.state_to("stock_issue");
                    },
                    on_action_change_pack_lot: () => {
                        this.state_set_data(this.state.data, "change_pack_lot");
                        this.state_to("change_pack_lot");
                    },
                },

                // ---> TODO: pretty equal to cluster picking: shall we move to mixin?
                unload_all: {
                    display_info: {
                        title: "Unload all bins",
                        scan_placeholder: "Scan location",
                    },
                    on_scan: scanned => {
                        this.state_set_data({location_barcode: scanned.text});
                        this.wait_call(
                            this.odoo.call("set_destination_all", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                                barcode: scanned.text,
                                confirmation: this.state.data.confirmation_required,
                            })
                        );
                    },
                    on_action_split: () => {
                        this.wait_call(
                            this.odoo.call("unload_split", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                            })
                        );
                    },
                },
                unload_single: {
                    display_info: {
                        title: "Unload single pack",
                        scan_placeholder: "Scan pack",
                    },
                    on_scan: scanned => {
                        this.wait_call(
                            this.odoo.call("unload_scan_pack", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                                package_id: this.state.data.move_line.package_src.id,
                                barcode: scanned.text,
                            })
                        );
                    },
                },
                unload_set_destination: {
                    display_info: {
                        title: "Set destination",
                        scan_placeholder: "Scan location",
                    },
                    on_scan: scanned => {
                        this.wait_call(
                            this.odoo.call("unload_scan_destination", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                                package_id: this.state.data.move_line.package_src.id,
                                barcode: scanned.text,
                                confirmation: this.state.data.confirmation_required,
                            })
                        );
                    },
                },
                change_pack_lot: {
                    display_info: {
                        title: "Change pack or lot",
                        scan_placeholder: "Scan pack or lot",
                    },
                    on_scan: scanned => {
                        this.wait_call(
                            this.odoo.call("change_pack_lot", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                                move_line_id: this.state.data.id,
                                barcode: scanned.text,
                            })
                        );
                    },
                },
                stock_issue: {
                    enter: () => {
                        this.reset_notification();
                    },
                    on_action: action => {
                        this.state["on_" + action].call(this);
                    },
                    on_confirm_stock_issue: () => {
                        this.wait_call(
                            this.odoo.call("stock_issue", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                                move_line_id: this.state.data.id,
                            })
                        );
                    },
                    on_back: () => {
                        this.state_set_data({});
                        this.reset_notification();
                        this.state_to("start_line");
                    },
                },
                zero_check: {
                    on_action: action => {
                        this.state["on_" + action].call(this);
                    },
                    is_zero: zero_flag => {
                        this.wait_call(
                            this.odoo.call("is_zero", {
                                zone_location_id: this.current_zone_location().id,
                                picking_type_id: this.current_picking_type().id,
                                move_line_id: this.state.data.id,
                                zero: zero_flag,
                            })
                        );
                    },
                    on_action_confirm_zero: () => {
                        this.state.is_zero(true);
                    },
                    on_action_confirm_not_zero: () => {
                        this.state.is_zero(false);
                    },
                },
            },
        };
    },
});

process_registry.add("zone_picking", ZonePicking, {
    demo_src: "demo/demo.zone_picking.js",
});