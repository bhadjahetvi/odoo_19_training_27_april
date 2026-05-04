from odoo import models, fields, api
from odoo.exceptions import UserError
from typing import List, cast


class Student(models.Model):
    _name = 'school.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True, tracking=True)
    age = fields.Integer("Age", tracking=True)
    dob = fields.Date("Date of Birth", tracking=True)
    admission_datetime = fields.Datetime("Admission Time", tracking=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender", tracking=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done')
    ], default='draft', tracking=True)

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    subject_ids = fields.Many2many(
        'school.subject',
        string="Subjects",
        tracking=True
    )

    teacher_id = fields.Many2many(
        'school.teacher',
        string="Teacher",
        compute="_compute_teacher",
        store=True
    )

    fees_ids = fields.One2many(
        'school.fees',
        'student_id',
        string="Fee Lines",
        tracking=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        tracking=True
    )

    notes = fields.Text("Notes", tracking=True)
    image = fields.Binary("Image", tracking=True)
    email = fields.Char("Email", tracking=True)
    phone = fields.Char("Phone", tracking=True)

    fees = fields.Monetary(
        string="Total Fees",
        compute="_compute_fees",
        store=True,
        currency_field='currency_id'
    )

    @api.depends('subject_ids.fee')
    def _compute_fees(self):
        for record in self:
            fees_list = cast(List[float], record.subject_ids.mapped('fee'))
            record.fees = sum(fees_list)

    @api.depends('subject_ids.teacher_id')
    def _compute_teacher(self):
        for rec in self:
            rec.teacher_id = rec.subject_ids.mapped('teacher_id')

    def action_confirm(self):
        for rec in self:
            rec.status = 'confirm'

    def action_done(self):
        for rec in self:
            rec.status = 'done'

    def action_reset_to_draft(self):
        for rec in self:
            rec.status = 'draft'

    def action_pay(self):
        self.ensure_one()

        if not self.fees:
            raise UserError("Please set Fees first!")

        if not self.partner_id:
            partner = self.env['res.partner'].create({
                'name': self.name,
                'email': self.email,
                'phone': self.phone,
            })
            self.partner_id = partner.id

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f"{self.name} Fees",
                'quantity': 1,
                'price_unit': self.fees,
            })],
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if vals.get('age', 0) < 18:
                raise UserError("Student age must be at least 5")

            if vals.get('email') and '@' not in vals.get('email'):
                raise UserError("Invalid email format!")

        return super().create(vals_list)

    def write(self, vals):
        for rec in self:

            if rec.status in ['confirm', 'done']:
                allowed_fields = ['status', 'notes']
                restricted_fields = [f for f in vals if f not in allowed_fields]

                if restricted_fields:
                    raise UserError(
                        "After Confirm/Done, only Status and Notes can be changed!"
                    )

            if 'age' in vals and vals['age'] < 18:
                raise UserError("Student age must be at least 5")

            if 'email' in vals and vals['email'] and '@' not in vals['email']:
                raise UserError("Invalid email format!")

        return super().write(vals)


    def unlink(self):
        for rec in self:
            if rec.status == 'done':
                raise UserError("You cannot delete Done records!")
        return super().unlink()