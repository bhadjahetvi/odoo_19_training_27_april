from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AdvancePaymentWizard(models.TransientModel):
    _name = 'advance.payment.wizard'
    _description = 'Advance Payment Wizard'

    # =========================
    # Fields
    # =========================

    payment_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    ], string="Payment Type", default='fixed')

    amount = fields.Float(
        string="Amount"
    )

    percentage = fields.Float(
        string="Percentage"
    )

    final_amount = fields.Float(
        string="Final Amount",
        compute="_compute_final_amount",
        store=True
    )

    # =========================
    # Compute Final Amount
    # =========================

    @api.depends('payment_type', 'amount', 'percentage')
    def _compute_final_amount(self):

        sale_order = self.env['sale.order'].browse(
            self.env.context.get('active_id')
        )

        for rec in self:

            if rec.payment_type == 'percentage':

                rec.final_amount = (
                    sale_order.amount_total * rec.percentage
                ) / 100

            else:

                rec.final_amount = rec.amount

    # =========================
    # Create Advance Payment
    # =========================

    def action_create_payment(self):

        sale_order = self.env['sale.order'].browse(
            self.env.context.get('active_id')
        )

        # =========================
        # Validation
        # =========================

        if self.final_amount <= 0:

            raise ValidationError(
                "Amount must be greater than zero."
            )

        # =========================
        # Find Bank Journal
        # =========================

        journal = self.env['account.journal'].search(
            [('type', '=', 'bank')],
            limit=1
        )

        if not journal:

            raise ValidationError(
                "Please create Bank Journal."
            )

        # =========================
        # Find Payment Method
        # =========================

        payment_method_line = (
            journal.inbound_payment_method_line_ids[:1]
        )

        if not payment_method_line:

            raise ValidationError(
                "No inbound payment method found in bank journal."
            )

        # =========================
        # Create Payment
        # =========================

        payment = self.env['account.payment'].create({

            'partner_id': sale_order.partner_id.id,

            'amount': self.final_amount,

            'payment_type': 'inbound',

            'partner_type': 'customer',

            'journal_id': journal.id,

            'payment_method_line_id': payment_method_line.id,

            'date': fields.Date.today(),

            'memo': sale_order.name,

            'sale_order_id': sale_order.id,

        })

        # =========================
        # Post Payment
        # =========================

        payment.action_post()

        # =========================
        # Force Paid State
        # =========================

        payment.write({
            'state': 'paid'
        })

        # =========================
        # Open Payment Form
        # =========================

        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': payment.id,
            'target': 'current',
        }