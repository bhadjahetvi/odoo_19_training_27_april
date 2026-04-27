from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Subject(models.Model):
    _name = 'school.subject'
    _description = 'Subject'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)

    teacher_id = fields.Many2one(
        'school.teacher',
        string="Teacher",
        required=True,
        tracking=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    fee = fields.Monetary(
        string="Fee",
        currency_field='currency_id',
        required=True,
        tracking=True
    )

    @api.constrains('fee')
    def _check_fee(self):
        for rec in self:
            if rec.fee <= 0:
                raise ValidationError("Fee must be greater than 0!")