/* eslint-disable strict */
/* eslint-disable no-implicit-globals */
var CheckoutPickingDetailMixin = {
    props: {
        info: Object,
        grouped_lines: Array,
        selectable_lines: Array,
        select_options: Object,
    },
    computed: {
        select_opts() {
            // Defining defaults for an Object property
            // works only if you don't pass the property at all.
            // If you pass only one key, you'll lose all defaults.
            const opts = _.defaults({}, this.$props.select_options, {
                showActions: false,
                list_item_component: "checkout-select-content",
            });
            return opts;
        },
    },
    template: `
<div class="detail checkout-picking-detail" v-if="!_.isEmpty(info)">
    <v-card outlined class="main">
        <v-card-title>{{ info.name }}</v-card-title>
        <v-card-subtitle>
            <span class="origin" v-if="info.origin">
                <span>{{ info.origin }}</span>
            </span>
            <span v-if="info.origin && info.partner"> - </span>
            <span class="partner" v-if="info.partner">
                <span>{{ info.partner.name }}</span>
            </span>
        </v-card-subtitle>
    </v-card>

    <manual-select
        :records="selectable_lines || info.move_lines"
        :grouped_records="grouped_lines"
        :options="select_opts"
        />
</div>
`,
};

Vue.component("checkout-picking-detail", {
    mixins: [CheckoutPickingDetailMixin],
});

Vue.component("checkout-select-content", {
    props: {
        record: Object,
        options: Object,
        index: Number,
        count: Number,
    },
    template: `
    <div>
        <div class="has_pack" v-if="record.package_dest">
            <div class="item-counter">
                <span>{{ index + 1 }} / {{ count }}</span>
            </div>
            <span>{{ record.package_dest.name }}</span>
        </div>
        <div class="no_pack" v-if="!record.package_dest">
            <div class="item-counter">
                <span>{{ index + 1 }} / {{ count }}</span>
            </div>
            <span>{{ record.product.display_name }}</span>
            <div class="lot" v-if="record.lot">
                <span class="label">Lot:</span> <span>{{ record.lot.name }}</span>
            </div>
            <div class="qty">
                <span class="label">Qty:</span> <span>{{ record.product.qty }}</span>
            </div>
        </div>
    </div>
  `,
});

Vue.component("checkout-summary-detail", {
    mixins: [CheckoutPickingDetailMixin],
    computed: {
        select_opts() {
            // Defining defaults for an Object property
            // works only if you don't pass the property at all.
            // If you pass only one key, you'll lose all defaults.
            const opts = _.defaults({}, this.$props.select_options, {
                multiple: true,
                initSelectAll: true,
                showCounters: true,
                list_item_component: "checkout-summary-content",
                list_item_extra_component: "checkout-summary-extra-content",
            });
            return opts;
        },
    },
});

Vue.component("checkout-summary-content", {
    props: {
        record: Object,
        options: Object,
        index: Number,
        count: Number,
    },
    template: `
    <div class="summary-content">
        <div class="has-pack" v-if="record.key != 'no-pack'">
            <v-list-item-title>
                <span class="item-counter">
                    <span>{{ index + 1 }} / {{ count }}</span>
                </span>
                {{ record.title }}
            </v-list-item-title>
        </div>
        <div class="no-pack" v-else>
            <div v-for="(subrec, i) in record.records">
                <checkout-summary-product-detail :record="subrec" :index="index" :count="count" />
            </div>
        </div>
    </div>
    `,
});

Vue.component("checkout-summary-product-detail", {
    props: {
        record: Object,
        index: Number,
        count: Number,
    },
    template: `
        <div class="summary-content-item">
            <v-list-item-title>
                <span class="item-counter">
                    <span>{{ index + 1 }} / {{ count }}</span>
                </span>
                {{ record.product.display_name }}
            </v-list-item-title>
            <v-list-item-subtitle>
                <div class="lot" v-if="record.lot">
                    <span class="label">Lot:</span> <span>{{ record.lot.name }}</span>
                </div>
                <div class="qty">
                    <span class="label">Qty:</span> <span>{{ record.product.qty }}</span>
                </div>
            </v-list-item-subtitle>
        </div>
    `,
});

Vue.component("checkout-summary-extra-content", {
    props: {
        record: Object,
    },
    template: `
    <v-expansion-panels flat v-if="record.key != 'no-pack' && record.records_by_pkg_type">
        <v-expansion-panel v-for="pkg_type in record.records_by_pkg_type" :key="pkg_type.key">
            <v-expansion-panel-header>
                <span>{{ pkg_type.title }}</span>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
                <div v-for="(prod, i) in pkg_type.records">
                    <checkout-summary-product-detail :record="prod" />
                </div>
            </v-expansion-panel-content>
        </v-expansion-panel>
    </v-expansion-panels>
    `,
});