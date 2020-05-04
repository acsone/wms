odoo.define('website_purchase_review.main_page', function (require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');
    var _t = core._t;
    //Wait for loading
    require('web_editor.base');

    if(!$('.container-fluid').length) {
        return $.Deferred().reject("DOM doesn't contain '.container-fluid'");
    }

    var products_list = [];
    var current_product_id = null;
    var current_products_list = [];

    var pathname = window.location.pathname;
    var vals = pathname.split("/");

    var purchase_order_slug = vals[2].split('-');
    var purchase_order_id = parseInt(purchase_order_slug[purchase_order_slug.length - 1]);
    if (vals.length === 4) {
        var product_slug = vals[3].split('-');
        current_product_id = parseInt(product_slug[product_slug.length - 1]);
    }

    init_listeners();
    // init_shortcuts();
    load_filters();
    load_products_list();
    disable_buttons(true);

    function init_listeners() {
        $('#save_global_values_btn').click(function () {
            save_global_values()
        });

        var products_list_header = $('#products_list_header');
        products_list_header.find('input[type=checkbox]').change(function(){
            refresh_list();
        });
        products_list_header.find('input[type=text]').keyup(function(){
            refresh_list();
        });
        $('#buttons_panel').find('button').click(function () {
            var tagId = $(this).attr('id');
            switch (tagId) {
                case "save_line":
                    // save_line();
                    break;
                case "step_backward":
                    change_product('-1');
                    break;
                case "step_forward":
                    change_product('+1');
                    break;
                case "fast_backward":
                    change_product('start');
                    break;
                case "fast_forward":
                    change_product('end');
                    break;
            }
        });

    }

    function load_filters() {
        var sPageURL = decodeURIComponent(window.location.search.substring(1));
        var sURLVariables = sPageURL.replace(/\+/g, ' ').split('&');
        for (var i = 0; i < sURLVariables.length; i++)  {
            var sParameterValues = sURLVariables[i].split('=');

            switch (sParameterValues[0]) {
                case "product_name":
                    $('#product_name').val(sParameterValues[1]);
                    break;
                default:
                    var field = "#" + sParameterValues[0];
                    $(field).prop('checked', true);
                    break;
            }

        }

    }

    function init_shortcuts() {
        $(document).keydown(function(e) {
            switch (e.which) {
                case (39 && e.altKey):
                    change_product('+1');
                    break;
                case (37 && e.altKey):
                    change_product('-1');
                    break;
                case (39 && e.ctrlKey && e.altKey):
                    change_product('end');
                    break;
                case (37 && e.ctrlKey && e.altKey):
                    change_product('start');
                    break;
            }
        })
    }

    function load_products_list() {
        var PO = new Model('purchase.order');
        PO.call('get_products', [purchase_order_id]).then(function(result) {
            $.each(result, function(index) {
                products_list.push({
                    id: result[index]['id'],
                    name: result[index]['name'],
                    display_name: result[index]['display_name'],
                    ref: result[index]['ref'],
                    ordered_products: result[index]['ordered_product'],
                    with_promo: result[index]['with_promo'],
                    without_promo: result[index]['without_promo'],
                    is_in_bo: result[index]['is_in_bo']
                });
            });

            if (current_product_id === null) {
                current_product_id = products_list[0].id;
            }
            load_stock_graph();
            refresh_list();
            compute_next_product();
            disable_buttons(false);
        });
    }

    function refresh_list() {
        var ordered_product = $('#products_to_order').is(':checked');
        var products_without_promo = $('#products_without_promo').is(':checked');
        var products_with_promo = $('#products_with_promo').is(':checked');
        var product_name = $('#product_name').val();

        current_products_list = products_list.filter(function(product) {
            if (ordered_product && !product.ordered_products) {
                return false;
            }
            if (products_without_promo && !product.without_promo) {
                return false;
            }
            if (products_with_promo && !product.with_promo) {
                return false;
            }
            if (product_name.trim()) {
                var test_name = ~product.name.toLowerCase().indexOf(product_name.toLowerCase());
                var test_ref = ~product.ref.toLowerCase().indexOf(product_name.toLowerCase());

                var name_check = test_name || test_ref;
                if (!name_check) {
                    return false;
                }
            }
            return true;
        });

        var products_list_tag = $('#products_list');
        products_list_tag.empty();

        $.each(current_products_list, function (index) {
            var product_container = $("<div/>");
            var product_tag = $("<input/>", {
                type: 'radio',
                name: 'products_list_item',
                value: current_products_list[index].id
            });

            product_tag.click(function () {
                var productId = parseInt($(this).val());
                load_product(productId);
            });

            product_container.append(product_tag);
            var product_name = null;
            if (current_products_list[index].id === current_product_id) {
                var text = $("<strong/>").text(current_products_list[index].display_name);
                product_name = $("<span/>");
                product_name.append(text);
                product_tag.attr('checked', 'checked');
            } else {
                product_name = $("<span/>").text(current_products_list[index].display_name);
            }

            if (current_products_list[index].is_in_bo) {
                product_container.attr('class', 'text-warning');
            }

            product_container.append(product_name);
            products_list_tag.append(product_container);
        });
    }

    function load_stock_graph() {
        var PP = new Model('product.product');
        PP.call('get_graph_values', [current_product_id])
            .then(function(result) {
                nv.addGraph(function() {
                    var chart = nv.models.discreteBarChart()
                        .x(function(d) {return d.label})
                        .y(function(d) {return d.value})
                        .staggerLabels(true)
                        .valueFormat(d3.format(',.0f'))
                        .showValues(true);

                    d3.select('#stock_graph svg').datum(result).call(chart);

                    nv.utils.windowResize(chart.update);
                })
            });
    }

    function get_next_product(step) {
        //Default product
        var newProductId = products_list[0].id;

        $.each(current_products_list, function (index) {
            if(current_products_list[index].id === current_product_id) {
                switch (step) {
                    case '+1':
                        index++;
                        break;
                    case '-1':
                        index--;
                        break;
                    case 'start':
                        index = 0;
                        break;
                    case 'end':
                        index = current_products_list.length - 1;
                        break;
                }

                if (index >= 0 && index < current_products_list.length) {
                    newProductId = current_products_list[index].id;
                    return false;
                } else {
                    newProductId = current_product_id;
                    return false;
                }
            }
        });

        return newProductId;
    }

    function change_product(step) {
        var newProductId = get_next_product(step);

        if (newProductId) {
            load_product(newProductId);
        }
    }

    function load_product(productId) {
        if (productId === current_product_id) {
            return false;
        }

        var params = {};
        var products_to_order = $('#products_to_order').is(':checked');
        var products_without_promo = $('#products_without_promo').is(':checked');
        var products_with_promo = $('#products_with_promo').is(':checked');
        var product_name = $('#product_name').val();

        if (products_to_order) {
            params['products_to_order'] = true;
        }
        if (products_without_promo) {
            params['products_without_promo'] = true;
        }
        if (products_with_promo) {
            params['products_with_promo'] = true;
        }
        if (product_name.trim()) {
            params['product_name'] = product_name.trim();
        }

        var url = '/purchase_review/' + purchase_order_id + '/' + productId;

        var params_str = $.param(params);
        if (params_str) {
            url += "?" + params_str;
        }

        $(location).attr('href', url);
    }

    function save_global_values() {
        var global_date_planned = $('#global_date_planned').val();
        var global_discount_global = $('#global_discount_global').val();
        var global_promotion_supplier = $('#global_promotion_supplier').val();

        var vals = {
            'global_date_planned': global_date_planned,
            'global_discount_global': parseFloat(global_discount_global),
            'global_promotion_supplier': parseFloat(global_promotion_supplier)
        };

        var PO = new Model('purchase.order');
        PO.call('set_overwrite_values', [purchase_order_id, vals])
            .then(function (result) {
                if (global_date_planned) {
                    $('#date_planned').val(global_date_planned);
                }
                if (global_discount_global) {
                    $('#discount_global').val(global_discount_global);
                }
                if (global_promotion_supplier) {
                    $('#promotion_supplier').val(global_promotion_supplier);
                }
            });
    }

    function compute_next_product() {
        $('#next_product_id').val(get_next_product('+1'));
    }

    function disable_buttons(is_disable) {
        $('#save_line').prop('disabled', is_disable);
        $('#save_global_values_btn').prop('disabled', is_disable);
    }


});
