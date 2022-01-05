/**
 * Copyright 2021 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

/* eslint-disable strict */
Vue.component("pack-picking-detail", {
  props: ["record"],
  methods: {
    operations_color_klass(rec) {
      let line = rec;
      if (line._is_group) {
        line = line.records[0];
      }
      let klass = "";
      if (this.record.scanned_packs.includes(line.package_dest.id)) {
        klass = "done screen_step_done lighten-1";
      } else {
        klass = "not-done screen_step_todo lighten-1";
      }
      return "move-line-" + klass;
    },
    line_list_options() {
      return {
        card_klass: "loud-labels",
        key_title: "",
        showCounters: true,
        list_item_options: {
          fields: this.line_list_fields(),
          list_item_klass_maker: this.operations_color_klass,
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
        {
          path: "qty_done",
          label: "Qty",
          render_component: "packaging-qty-picker-display",
          render_options: function(record) {
            let opts = {
              init_value: record.qty_done,
              available_packaging: record.product.packaging,
              uom: record.product.uom,
            };
            return opts;
          },
        },
      ];
    },
    grouped_lines() {
      let groups = this.utils.wms.group_by_pack(
        this.record.operations.filter(op => {
          if (op.package_dest != null && op.package_dest.is_internal) {
            return op;
          }
        })
      );
      let self = this;
      _.forEach(groups, function(item) {
        item.group_color = self.record.scanned_packs.includes(item.pack.id)
          ? self.utils.colors.color_for("screen_step_done")
          : self.utils.colors.color_for("screen_step_todo");
      });
      return groups;
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
    <list
        :records="record.operations"
        :grouped_records="grouped_lines()"
        :options="line_list_options()"
        />
  </div>

`,
});
