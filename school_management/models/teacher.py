from odoo import models, fields


class Teacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # BASIC INFO
    name = fields.Char("Name", required=True, tracking=True)
    age = fields.Integer("Age", tracking=True)
    dob = fields.Date("Date of Birth", tracking=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender", tracking=True)

    # CONTACT
    email = fields.Char("Email", tracking=True)
    phone = fields.Char("Phone", tracking=True)

    # EXTRA
    subject = fields.Char("Subject", tracking=True)
    salary = fields.Float("Salary", tracking=True)
    image = fields.Binary("Image", tracking=True)
    notes = fields.Text("Notes", tracking=True)

    # ✅ CORRECT RELATION
    student_ids = fields.One2many(
        'school.student',
        'teacher_id',
        string="Students"
    )

    student_count = fields.Integer(
        string="Student Count",
        compute="_compute_student_count"
    )

    # STATUS
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done')
    ], default='draft', tracking=True)

    # ---------------- COMPUTE ---------------- #

    def _compute_student_count(self):
        for teacher in self:
            teacher.student_count = len(teacher.student_ids)

    # ---------------- BUTTONS ---------------- #

    def action_confirm(self):
        for rec in self:
            rec.status = 'confirm'

    def action_done(self):
        for rec in self:
            rec.status = 'done'

    def action_view_students(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'school.student',
            'view_mode': 'list,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id},
        }