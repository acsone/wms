import {GenericStatesMixin, ScenarioBaseMixin} from "./mixins.js";
import {process_registry} from '../services/process_registry.js';

export var Checkout = Vue.component('checkout', {
    mixins: [ScenarioBaseMixin, GenericStatesMixin],
    template: `
        <Screen :title="screen_info.title" :klass="screen_info.klass">
            <!-- FOR DEBUG -->
            <!-- {{ current_state_key }} -->
            <template v-slot:header>
                <user-information
                    v-if="!need_confirmation && user_notification.message"
                    v-bind:info="user_notification"
                    />
                <state-display-info :info="state.display_info" v-if="state.display_info"/>
            </template>
            <searchbar
                v-if="state_in(['select_document', 'select_line'])"
                v-on:found="on_scan"
                :input_placeholder="search_input_placeholder"
                />
            <div v-if="state_is('select_document')">
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <v-btn depressed color="primary" @click="$emit('action', 'manual_selection')">Manual selection</v-btn>
                        </v-col>
                    </v-row>
                </div>
            </div>

            <div v-if="state_is('select_line')">
                <checkout-picking-detail
                    v-if="state_is('select_line')"
                    :info="state.data"
                    v-on:select="state.on_select"
                    v-on:back="state.on_back"
                    />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <v-btn depressed color="primary" @click="$emit('action', 'summary')">Summary</v-btn>
                        </v-col>
                    </v-row>
                </div>
            </div>

        </Screen>
        `,

    /* <manual-select
        v-if="state_is('manual_selection')"
        v-on:select="state.on_select"
        v-on:back="state.on_back"
        :records="state.data.lines"
        :key_value="'id'"
        :list_item_content_component="'TODO'"
        /> */
    computed: {
        picking_id: function () {
            return this.erp_data.data.select_line.id;
        },
    },
    methods: {
        record_by_id: function (records, _id) {
            return _.first(_.filter(records, {'id': _id}));
        },
    },
    data: function () {
        return {
            'usage': 'checkout',
            'initial_state_key': 'select_document',
            'states': {
                'select_document': {
                    display_info: {
                        'title': 'Start by scanning something',
                        'scan_placeholder': 'Scan pack / picking / location',
                    },
                    enter: () => {
                        this.reset_erp_data('data');
                    },
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.call('scan_document', {'barcode': scanned.text}),
                        );
                    },
                    on_manual_selection: (evt) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.call('list_stock_picking'),
                        );
                    },
                },
                'manual_selection': {
                    on_back: () => {
                        this.go_state('start');
                        this.reset_notification();
                    },
                    on_select: (selected) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.call('select', {
                                'picking_id': selected,
                            }),
                        );
                    },
                    display_info: {
                        'title': 'Select a picking and start',
                    },
                },
                'select_line': {
                    display_info: {
                        'title': 'Pick the product by scanning something',
                        'scan_placeholder': 'Scan pack / product / lot',
                    },
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.call('scan_line', {
                                'picking_id': this.picking_id,
                                'barcode': scanned.text,
                            }),
                        );
                    },
                    on_select: (selected) => {
                        if (!selected) {
                            return;
                        }
                        const line = this.record_by_id(this.state.data.lines, selected);
                        this.go_state(
                            'wait_call',
                            this.odoo.call('select_line', {
                                'picking_id': this.picking_id,
                                'move_line_id': line.id,
                                'package_id': line.pack ? line.pack.id : null,
                            }),
                        );
                    },
                    on_back: () => {
                        this.go_state('start');
                        this.reset_notification();
                    },
                    on_summary: () => {
                        throw 'NOT IMPLEMENTED';
                    },
                },
                'select_pack': {
                    display_info: {
                        'title': 'Select pack',
                    },
                    on_qty_update: (qty) => {
                        this.scan_destination_qty = parseInt(qty);
                    },
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.call('scan_pack_action', {
                                'move_line_id': this.state.data.id,
                                'barcode': scanned.text,
                                'quantity': this.scan_destination_qty,
                            }),
                        );
                    },
                    on_action: (action) => {
                        this.state['on_' + action].call(this);
                    },
                    on_select_line: () => {
                        throw 'NOT IMPLEMENTED';
                        this.go_state(
                            'wait_call',
                            this.odoo.call('set_line_qty', {
                                'move_line_id': this.state.data.id,
                            }),
                        );
                    },
                    on_new_pack: () => {
                        throw 'NOT IMPLEMENTED';
                    },
                    on_existing_pack: () => {
                        throw 'NOT IMPLEMENTED';
                    },
                    on_without_pack: () => {
                        throw 'NOT IMPLEMENTED';
                    },
                },
                'change_qty': {
                    display_info: {
                        'title': 'Change quantity',
                    },
                    on_qty_update: (qty) => {
                        this.state.data.qty = parseInt(qty);
                    },
                    on_action: (action) => {
                        this.state['on_' + action].call(this);
                    },
                    on_change_qty: () => {
                        throw 'NOT IMPLEMENTED';
                        this.go_state(
                            'wait_call',
                            this.odoo.call('set_custom_qty', {
                                'move_line_id': this.state.data.id,
                                'quantity': this.state.data.qty,
                            }),
                        );
                    },
                },
                'select_dest_package': {
                    display_info: {
                        'title': 'Select destination package',
                    },
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.call('scan_dest_package', {
                                'barcode': scanned.text,
                            }),
                        );
                    },
                    on_action: (action) => {
                        this.state['on_' + action].call(this);
                    },
                    on_set_package: (pkg) => {
                        throw 'NOT IMPLEMENTED';
                        this.go_state(
                            'wait_call',
                            this.odoo.call('set_dest_package', {
                                'move_line_id': this.state.data.id,
                                'package_id': pkg.id,
                            }),
                        );
                    },
                },
                'summary': {
                    display_info: {
                        'title': 'Summary',
                    },
                    on_action: (action) => {
                        this.state['on_' + action].call(this);
                    },
                    on_pkg_change_type: (pkg) => {
                        throw 'NOT IMPLEMENTED';
                    },
                    on_pkg_destroy: (pkg) => {
                        throw 'NOT IMPLEMENTED';
                    },
                    on_mark_as_done: (pkg) => {
                        throw 'NOT IMPLEMENTED';
                    },
                },
                'change_package_type': {
                    display_info: {
                        'title': 'Change package type',
                    },
                    on_action: (action) => {
                        this.state['on_' + action].call(this);
                    },
                    on_do_it: (pkg) => {
                        throw 'NOT IMPLEMENTED';
                    },
                },
            },
        };
    },
});


process_registry.add('checkout', Checkout);
