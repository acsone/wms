export var PackagingQtyPicker = Vue.component("packaging-qty-picker", {
    props: {
        input_type: {
            type: String,
            default: "text", // Avoid default browser spinner
        },
        init_value: {
            type: Number,
            default: 0,
        },
        min: {
            type: Number,
            default: 0,
        },
        max: {
            type: Number,
            default: undefined,
        },
        mode: {
            type: String,
            default: "",
        },
        available_packaging: {
            type: Array,
            default: function() {
                return [];
            },
        },
        show_pkg_size: {
            type: Boolean,
            default: true,
        },
    },
    data: function() {
        return {
            value: 0,
            original_value: 0,
            orig_qty_by_pkg: {},
            qty_by_pkg: {},
        };
    },
    methods: {
        on_change_pkg_qty: function(event) {
            const input = event.target;
            let new_qty = parseInt(input.value, 10);
            const data = $(input).data();
            const origvalue = data.origvalue || 0;
            // Check max qty reached
            const future_qty = this.value + data.pkg.qty * (new_qty - origvalue);
            if (new_qty && future_qty > this.original_value) {
                // restore qty just in case we can get here
                new_qty = origvalue;
                event.preventDefault();
                // Make it red and shake it
                $(input)
                    .closest(".inner-wrapper")
                    .addClass("error shake-it")
                    .delay(800)
                    .queue(function() {
                        // End animation
                        $(this)
                            .removeClass("error shake-it", 2000, "easeInOutQuad")
                            .dequeue();
                        // Restore value
                        $(input).val(new_qty);
                    });
            }
            // Trigger update
            this.$set(this.qty_by_pkg, data.pkg.id, new_qty);
            // Set new orig value
            $(input).data("origvalue", new_qty);
        },
        sorted_packaging: function() {
            return _.reverse(_.sortBy(this.available_packaging, _.property("qty")));
        },
        packaging_by_id: function(id) {
            return _.find(this.available_packaging, ["id", parseInt(id, 10)]);
        },
        /**
         *
        Calculate quantity by packaging.

        Limitation: fractional quantities are lost.

        :prod_qty:
        :min_unit: minimal unit of measure as a tuple (qty, name).
                   Default: to UoM unit.
        :returns: list of tuple in the form [(qty_per_package, package_name)]

         * @param {*} prod_qty total qty to satisfy.
         * @param {*} min_unit minimal unit of measure as a tuple (qty, name).
                   Default: to UoM unit.
        */
        product_qty_by_packaging: function() {
            return this._product_qty_by_packaging(this.sorted_packaging(), this.value);
        },
        /**
         * Produce a list of tuple of packaging qty and packaging name.
         * TODO: refactor to handle fractional quantities (eg: 0.5 Kg)
         *
         * @param {*} pkg_by_qty packaging records sorted by major qty
         * @param {*} qty total qty to satisfy
         */
        _product_qty_by_packaging: function(pkg_by_qty, qty) {
            const self = this;
            let res = {};
            // const min_unit = _.last(pkg_by_qty);
            pkg_by_qty.forEach(function(pkg) {
                let qty_per_pkg = 0;
                [qty_per_pkg, qty] = self._qty_by_pkg(pkg.qty, qty);
                if (qty_per_pkg) res[pkg.id] = qty_per_pkg;
                if (!qty) return;
            });
            return res;
        },
        /**
         * Calculate qty needed for given package qty.
         *
         * @param {*} pkg_by_qty
         * @param {*} qty
         */
        _qty_by_pkg: function(pkg_qty, qty) {
            const precision = 3; // TODO: get it from product UoM
            let qty_per_pkg = 0;
            // TODO: anything better to do like `float_compare`?
            while (_.round(qty - pkg_qty, precision) >= 0.0) {
                qty -= pkg_qty;
                qty_per_pkg += 1;
            }
            return [qty_per_pkg, qty];
        },
        _compute_qty: function() {
            const self = this;
            let value = 0;
            _.forEach(this.qty_by_pkg, function(qty, id) {
                value += self.packaging_by_id(id).qty * qty;
            });
            return value;
        },
        compute_qty: function(newVal, oldVal) {
            this.value = this._compute_qty();
        },
    },
    watch: {
        value: {
            handler: function(newVal, oldVal) {
                this.$root.trigger("qty_edit", this.value);
            },
        },
    },
    created: function() {
        this.original_value = parseInt(this.init_value, 10);
        this.value = parseInt(this.init_value, 10);
    },
    mounted: function() {
        const self = this;
        this.$watch(
            "qty_by_pkg",
            function() {
                self.compute_qty();
            },
            {deep: true}
        );
        this.qty_by_pkg = this.product_qty_by_packaging();
        // hooking via `v-on:change` we don't get the full event but only the qty :/
        // And forget about using v-text-field because it loses the full event object
        $(".pkg-value", this.$el).change(this.on_change_pkg_qty);
        $(".pkg-value", this.$el).on("focus click", function() {
            $(this).select();
        });
    },
    computed: {
        /**
         * Collect qty of contained packaging inside bigger packaging.
         * Eg: "1 Pallet" contains "4 Big boxes".
         */
        contained_packaging: function() {
            const self = this;
            let res = {};
            const packaging = this.sorted_packaging();
            _.forEach(packaging, function(pkg, i) {
                if (packaging[i + 1]) {
                    const next_pkg = packaging[i + 1];
                    res[pkg.id] = {
                        pkg: next_pkg,
                        qty: self._qty_by_pkg(next_pkg.qty, pkg.qty)[0],
                    };
                }
            });
            return res;
        },
    },
    template: `
<div :class="[$options._componentTag, mode ? 'mode-' + mode: '']">
    <v-row class="unit-value">
        <v-col class="current-value">
            <v-text-field :type="input_type" v-model="value" readonly="readonly" />
        </v-col>
        <v-col class="init-value">
            <v-text-field :type="input_type" v-model="original_value" readonly="readonly" disabled="disabled" />
        </v-col>
    </v-row>
    <v-row class="packaging-value">
        <v-col class="packaging" v-for="pkg in sorted_packaging()">
            <div class="inner-wrapper">
                <div class="input-wrapper">
                    <input type="text" class="pkg-value"
                        :value="qty_by_pkg[pkg.id] || 0"
                        :data-pkg="JSON.stringify(pkg)"
                        />
                </div>
                <div class="pkg-name"> {{ pkg.name }}</div>
                <div v-if="contained_packaging[pkg.id]" class="pkg-qty">({{ contained_packaging[pkg.id].qty }} {{ contained_packaging[pkg.id].pkg.name }})</div>
            </div>
        </v-col>
    </v-row>
</div>
`,
});