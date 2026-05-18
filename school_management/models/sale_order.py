from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_id_domain(self):
        for rec in self:
            if rec.partner_id:

                children = rec.partner_id.child_ids

                invoice_child = children.filtered(lambda c: c.type == 'invoice')
                delivery_child = children.filtered(lambda c: c.type == 'delivery')

                rec.partner_invoice_id = (
                    invoice_child[:1].id if invoice_child else rec.partner_id.id
                )

                rec.partner_shipping_id = (
                    delivery_child[:1].id if delivery_child else rec.partner_id.id
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