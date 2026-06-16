from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order'
    )