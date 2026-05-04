from odoo import models, fields
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sales_limit = fields.Float(string="Sales Limit")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            partner = order.partner_id

            if not partner.sales_limit:
                continue

            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done']),
                ('id', '!=', order.id)
            ])

            total_amount = sum(orders.mapped('amount_total')) + order.amount_total

            if total_amount > partner.sales_limit:
                raise ValidationError(
                    f"Sales limit exceeded!\n\n"
                    f"Customer: {partner.name}\n"
                    f"Limit: {partner.sales_limit}\n"
                    f"Current Total: {total_amount}"
                )

        return super().action_confirm()