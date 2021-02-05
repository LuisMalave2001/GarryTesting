odoo.define('pos_pr.screens.invoice_payment_receipt', function (require) {

    const screens = require('point_of_sale.screens');
    const core = require('web.core');
    const gui = require('point_of_sale.gui');

    const QWeb = core.qweb;
    const _t = core._t;
    const reports = require('pos_pr.components.reports');

    const InvoicePaymentReceiptScreenWidget = screens.ScreenWidget.extend({
        template: 'InvoicePaymentReceiptScreenWidget',
        show: function (refresh, data) {
            this._super.apply(this, arguments);

            this._render_change();

            const paymentGroup = this.pos.gui.get_current_screen_param('paymentGroup');
            const invoiceAddress = this.pos.gui.get_current_screen_param('invoiceAddress');

            this.receipt_template = new reports.InvoicePaymentReceiptment(this, {
                paymentGroup: paymentGroup,
                customer: invoiceAddress || this.pos.get_client(),
            }, false);
            this.receipt_template_copy = new reports.InvoicePaymentReceiptment(this, {
                paymentGroup: paymentGroup,
                customer: invoiceAddress || this.pos.get_client(),
                copy: true,
            });

            const changeValueEl = this.el.querySelector('.change-value');
            if (changeValueEl) {
                changeValueEl.innerText = this.format_currency(paymentGroup.payment_change);
            }

            this.receipt_template.renderElement();
            this.receipt_template_copy.renderElement();
            this.cssPageRuleElement = this._create_css_page_rule();
            this.render_receipt();
            this.handle_auto_print();
        },

        _render_change: function (){
            const change = this.pos.gui.get_current_screen_param('changeAmount') || 0;
            this.el.querySelector('.change-value').innerText = this.format_currency(change);
        },

        hide: function () {
            this._super.apply(this, arguments);
            if (this.cssPageRuleElement) {
                this.cssPageRuleElement.remove();
                this.cssPageRuleElement = null;
            }
        },

        _create_css_page_rule: function () {
            const styleElement = document.createElement('STYLE');

            styleElement.innerHTML = `      
                @page {
                    size: auto;
                    margin: 1cm;
                }
            `;

            styleElement.ref = 'js_receipt_css_page_rule';
            return styleElement;
        },

        handle_auto_print: function () {
            if (this.should_auto_print() && !this.pos.get_order().is_to_email()) {
                this.print();
                if (this.should_close_immediately()) {
                    this.click_next();
                }
            } else {
                this.lock_screen(false);
            }
        },

        should_auto_print: function () {
            return this.pos.config.iface_print_auto && !this.pos.get_order()._printed;
        },

        should_close_immediately: function () {
            var order = this.pos.get_order();
            var invoiced_finalized = order.is_to_invoice() ? order.finalized : true;
            return this.pos.proxy.printer && this.pos.config.iface_print_skip_screen && invoiced_finalized;
        },

        lock_screen: function (locked) {
            this._locked = locked;
            if (locked) {
                this.$('.next').removeClass('highlight');
            } else {
                this.$('.next').addClass('highlight');
            }
        },

        print_web: function () {
            if ($.browser.safari) {
                document.execCommand('print', false, null);
            } else {
                try {
                    window.print();
                } catch (err) {
                    if (navigator.userAgent.toLowerCase().indexOf("android") > -1) {
                        this.gui.show_popup('error', {
                            'title': _t('Printing is not supported on some android browsers'),
                            'body': _t('Printing is not supported on some android browsers due to no default printing protocol is available. It is possible to print your tickets by making use of an IoT Box.'),
                        });
                    } else {
                        throw err;
                    }
                }
            }
            this.pos.get_order()._printed = true;
        },

        print_html: function () {
            const receipt = this.get_receipt_template_as_html();
            this.pos.proxy.printer.print_receipt(receipt);
            this.pos.get_order()._printed = true;
        },

        print: function () {
            const self = this;

            if (!this.pos.proxy.printer) { // browser (html) printing

                // The issue here and the explanation of this weird code is in
                // point_of_sale/static/src/js/screens.js:1737 on Odoo 13 at 2020-09-11 7:40 P.M
                this.lock_screen(true);

                setTimeout(function () {
                    self.lock_screen(false);
                }, 1000);

                this.print_web();
            } else {
                // proxy (html) printing
                this.print_html();
                this.lock_screen(false);
            }
        },

        click_next: function () {
            this.pos.gui.show_screen('products');
        },

        renderElement: function () {
            const self = this;
            this._super();
            this.$('.next').click(function () {
                if (!self._locked) {
                    self.click_next();
                }
            });
            this.$('.button.print').click(function () {
                if (!self._locked) {
                    self.print();
                }
            });
        },

        render_receipt: function () {
            this.$('[ref="pos_payment_receipt_container"]').empty()
                .append(this.receipt_template.el)
                .append(this.receipt_template_copy.el)
                .append(this.cssPageRuleElement);
        },

        get_receipt_template_as_html: function () {
            this.receipt_template.renderElement();
        }
    });
    gui.define_screen({name: 'invoicePaymentReceipt', widget: InvoicePaymentReceiptScreenWidget});

    return {
        InvoicePaymentReceiptScreenWidget
    }
});
