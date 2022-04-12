/**
 * Copyright 2022 ACSONE SA/NV (http://www.acsone.eu)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

let methods = Vue.component("detail-product").extendOptions.methods;
Vue.component("detail-product").extendOptions.methods = {
  ...methods,
  ...{
    locations_by_products_options() {
      return {
        main: false,
        key_title: "name",
        klass: "loud-labels",
      };
    },

    available_product_list_options() {
      return {
        main: true,
        key_title: "display_name",
        klass: "loud-labels",
        title_action_field: {
          action_val_path: "default_code",
        },
        fields: this.available_product_list_fields(),
      };
    },
    available_product_list_fields() {
      return [{path: "qty_available", label: "Qty on hand"}];
    },
    lot_detail_options() {
      return {
        main: false,
        key_title: "name",
        fields: this.lot_detail_fields(),
        klass: "loud-labels",
      };
    },
    lot_detail_fields() {
      const self = this;
      return [
        {path: "quantity", label: "Qty in stock"},
        {
          path: "expire_date",
          label: "Expiry date",
          renderer: function(rec, field) {
            return self.utils.display.render_field_date(rec, field);
          },
        },
        {
          path: "removal_date",
          label: "Removal date",
          renderer: function(rec, field) {
            return self.utils.display.render_field_date(rec, field);
          },
        },
      ];
    },
  },
};

Vue.component("detail-product").extendOptions.template = `
  <div :class="$options._componentTag">
    <item-detail-card
        v-bind="$props"
        :options="{main: true, fields: product_detail_fields(), key_title: 'display_name'}"
        card_color="info lighten-3"
        />

    <div class="suppliers mb-4" v-if="_.result(record, 'suppliers', []).length">
        <separator-title>Suppliers</separator-title>
        <item-detail-card
            v-for="supp in record.suppliers"
            :key="'supp' + supp.id"
            :record="supp"
            :options="{no_title: true, fields: supplier_detail_fields()}"
            />
    </div>

    <div class="packaging mb-4" v-if="opts.full_detail && record.packaging">
        <separator-title>Packaging</separator-title>
        <list
            :records="record.packaging"
            :options="{key_title: 'display_name', list_item_fields: packaging_detail_fields()}"
            />
    </div>

    <div class="locations" v-if="record.locations.length">
        <separator-title>Locations</separator-title>
        <v-expansion-panels v-if="record.locations.length > 0" flat :color="utils.colors.color_for('detail_main_card')">
            <v-expansion-panel v-for="(location, index) in record.locations" :key="make_component_key(['location', index])">
              <v-expansion-panel-header>
                  <item-detail-card
                      v-bind="$props"
                      :record="location"
                      :key="make_component_key(['location', location.id])"
                      :options="locations_by_products_options()"
                      :card_color="utils.colors.color_for('detail_main_card')"
                      />
              </v-expansion-panel-header>
              <v-expansion-panel-content v-for="(product, i) in location.products">
                <separator-title>Lots</separator-title>
                <item-detail-card
                v-for="(lot, i) in product.lots"
                :record="lot"
                v-bind="$props"
                :key="make_component_key(['lot', lot.id])"
                :options="lot_detail_options()"
                :card_color="utils.colors.color_for('screen_step_todo')"
                />
              </v-expansion-panel-content>

              </v-expansion-panel>
        </v-expansion-panels>
    </div>

</div>

  `;
