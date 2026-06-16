from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    # =========================
    # Sale Order Relation
    # =========================

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        compute='_compute_sale_order',
        store=True
    )

    # =========================
    # Advance Payments
    # =========================

    advance_payment_ids = fields.One2many(
        'account.payment',
        'sale_order_id',
        string='Advance Payments',
        compute='_compute_advance_payments'
    )

    advance_amount = fields.Float(
        string='Advance Amount',
        compute='_compute_advance_payments'
    )

    remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_compute_advance_payments'
    )

    # =========================
    # Get Sale Order From Invoice Lines
    # =========================

    @api.depends('invoice_line_ids.sale_line_ids')
    def _compute_sale_order(self):

        for rec in self:

            sale_orders = rec.invoice_line_ids.sale_line_ids.order_id

            rec.sale_order_id = (
                sale_orders[:1].id
                if sale_orders
                else False
            )

    # =========================
    # Compute Advance Payments
    # =========================

    @api.depends('partner_id', 'sale_order_id')
    def _compute_advance_payments(self):

        for rec in self:

            payments = self.env['account.payment'].search([
                ('partner_id', '=', rec.partner_id.id),
                ('sale_order_id', '=', rec.sale_order_id.id),
                ('state', 'in', ['in_process', 'paid']),
            ])

            rec.advance_payment_ids = payments

            total = sum(
                payments.mapped('amount')
            )

            rec.advance_amount = total

            rec.remaining_amount = (
                rec.amount_total - total
            )