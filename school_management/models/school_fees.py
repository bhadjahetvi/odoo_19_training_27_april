from odoo import models, fields

class SchoolFees(models.Model):
    _name = 'school.fees'
    _description = 'School Fees'

    student_id = fields.Many2one('school.student', string="Student")
    amount = fields.Float("Amount")
    invoice_id = fields.Many2one('account.move', string="Invoice")

    def action_create_invoice(self):
        self.ensure_one()

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.env.user.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': self.student_id.name + " Fees",
                'quantity': 1,
                'price_unit': self.amount,
            })],
        })

        self.invoice_id = invoice.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }