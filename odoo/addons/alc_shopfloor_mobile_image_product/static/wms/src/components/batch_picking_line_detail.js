/**
 * Copyright 2022 ACSONE SA/NV (http://www.acsone.eu)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
const template = Vue.component("batch-picking-line-detail").extendOptions.template;
Vue.component("batch-picking-line-detail").extendOptions.template = template.replace(
  "</div>",
  ` <img :src="line.product.image" v-if="line.product.image" class="product_image"/>
    </div>`
);
