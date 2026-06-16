from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # =========================
    # Advance Payment Relation
    # =========================

    advance_payment_ids = fields.One2many(
        'account.payment',
        'sale_order_id',
        string='Advance Payments'
    )

    advance_payment_count = fields.Integer(
        string='Advance Payment Count',
        compute='_compute_advance_payment'
    )

    total_advance_amount = fields.Float(
        string='Total Advance Amount',
        compute='_compute_advance_payment'
    )

    remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_compute_advance_payment'
    )

    # =========================
    # Compute Advance Payment
    # =========================

    @api.depends(
        'advance_payment_ids.amount',
        'advance_payment_ids.state'
    )
    def _compute_advance_payment(self):

        for rec in self:

            total = sum(
                rec.advance_payment_ids.filtered(
                    lambda p: p.state in ['in_process', 'paid']
                ).mapped('amount')
            )

            rec.total_advance_amount = total

            rec.remaining_amount = (
                rec.amount_total - total
            )

            rec.advance_payment_count = len(
                rec.advance_payment_ids
            )

    # =========================
    # Partner Address Domain
    # =========================

    @api.onchange('partner_id')
    def _onchange_partner_id_domain(self):

        for rec in self:

            if rec.partner_id:

                children = rec.partner_id.child_ids

                invoice_child = children.filtered(
                    lambda c: c.type == 'invoice'
                )

                delivery_child = children.filtered(
                    lambda c: c.type == 'delivery'
                )

                rec.partner_invoice_id = (
                    invoice_child[:1].id
                    if invoice_child
                    else rec.partner_id.id
                )

                rec.partner_shipping_id = (
                    delivery_child[:1].id
                    if delivery_child
                    else rec.partner_id.id
                )

                return {
                    'domain': {
                        'partner_invoice_id': [
                            '|',
                            ('id', '=', rec.partner_id.id),
                            ('parent_id', '=', rec.partner_id.id)
                        ],
                        'partner_shipping_id': [
                            '|',
                            ('id', '=', rec.partner_id.id),
                            ('parent_id', '=', rec.partner_id.id)
                        ],
                    }
                }

            else:

                rec.partner_invoice_id = False
                rec.partner_shipping_id = False

        return {}

    # =========================
    # Open Advance Payment Wizard
    # =========================

    def action_open_advance_payment_wizard(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Advance Payment',
            'res_model': 'advance.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id
            }
        }

    # =========================
    # Open Advance Payment
    # =========================

    def action_open_advance_payment(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Advance Payment',
            'res_model': 'advance.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id
            }
        }

    # =========================
    # Smart Button Action
    # =========================

    def action_view_advance_payments(self):

        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Advance Payments',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {
                'default_sale_order_id': self.id,
            }
        }

    # =========================
    # Pass Sale Order in Invoice
    # =========================

    def _prepare_invoice(self):

        vals = super()._prepare_invoice()

        vals.update({
            'sale_order_id': self.id,
        })

        return vals