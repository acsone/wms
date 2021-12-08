/**
 * Copyright 2021 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

/* eslint-disable strict */
Vue.component("pack-picking-detail", {
  props: ["record"],
  methods: {
    line_list_options() {
      return {
        card_klass: "loud-labels",
        key_title: "",
        list_item_options: {
          fields: this.line_list_fields(),
          list_item_klass_maker: this.utils.wms.move_line_color_klass,
        },
      };
    },
    line_list_fields() {
      return [
        {
          path: "product.display_name",
          action_val_path: "product.default_code",
          klass: "loud",
        },
        {
          path: "package_src.name",
          label: "Pack",
          action_val_path: "package_src.name",
        },
        {path: "lot.name", label: "Lot", action_val_path: "lot.name"},
        {path: "qty_done", label: "Qty"},
      ];
    },
    grouped_lines() {
      return this.utils.wms.group_by_pack(
        this.record.operations.filter(op => {
          if (op.package_dest.is_internal) {
            return op;
          }
        })
      );
    },
  },
  template: `
  <div class="review">
    <v-card class="main">
        <v-card-title>
            <div class="main-info">
                    {{ record.name }} : {{ record.partner.name }}
            </div>
        </v-card-title>
    </v-card>
    <div class="lines" v-if="(record.operations || []).length">
            <div v-for="group in grouped_lines()">
                <separator-title>
                    {{group.title}}
                </separator-title>
                <list
                    :records="group.records"
                    :key="'group-' + group.key"
                    :options="line_list_options()"
                    />
            </div>
        </div>
  </div>

`,
});
