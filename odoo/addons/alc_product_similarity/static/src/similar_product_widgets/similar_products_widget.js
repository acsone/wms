/** @odoo-module **/

import {Component, onMounted, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

class SimilarProductsWidget extends Component {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.action = useService("action"); // Use the action service
    this.state = useState({
      similarProducts: [],
    });

    this.onSimilarProductClick = this.onSimilarProductClick.bind(this);

    onMounted(async () => {
      await this.loadSimilarProducts();
    });
  }

  async loadSimilarProducts() {
    if (this.props.value && this.props.value.length > 0) {
      try {
        const products = await this.orm.searchRead(
          "product.product",
          [["id", "in", this.props.value]],
          ["name", "list_price", "image_128"]
        );
        this.state.similarProducts = products;
      } catch (error) {
        console.error("Failed to load similar products:", error);
      }
    }
  }

  onSimilarProductClick(productId) {
    this.action.doAction({
      type: "ir.actions.act_window",
      res_model: "product.product",
      res_id: productId,
      views: [[false, "form"]],
      target: "current",
    });
  }

  updateValue(ev) {
    this.props.update(ev.target.value);
  }
}

SimilarProductsWidget.template = "alc_product_similarity.similar_products_widget";
SimilarProductsWidget.components = {};

SimilarProductsWidget.props = {
  ...standardFieldProps,
  value: {type: Array, optional: true},
  update: {type: Function},
};

registry.category("fields").add("similar_products_widget", SimilarProductsWidget);
