from odoo import models, fields, api


class Teacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ---------------- BASIC ---------------- #
    name = fields.Char(required=True)
    age = fields.Integer()
    dob = fields.Date()

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ])

    email = fields.Char()
    phone = fields.Char()

    # ---------------- PROFESSIONAL ---------------- #
    subject = fields.Char()
    salary = fields.Float()
    image = fields.Binary()
    notes = fields.Text()

    # ---------------- STATUS ---------------- #
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done')
    ], default='draft', tracking=True)

    # ---------------- USER ---------------- #
    user_id = fields.Many2one(
        'res.users',
        string="Internal User",
        readonly=True,
        copy=False
    )

    # ---------------- STUDENTS ---------------- #
    student_ids = fields.Many2many(
        'school.student',
        'school_student_teacher_rel',
        'teacher_id',
        'student_id',
        string="Students"
    )

    student_count = fields.Integer(
        compute="_compute_student_count"
    )

    # ---------------- COMPUTE ---------------- #
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)

    # ---------------- BUTTONS ---------------- #
    def action_confirm(self):
        self.write({'status': 'confirm'})

    def action_done(self):
        self.write({'status': 'done'})

    # ---------------- CREATE OVERRIDE ---------------- #
    @api.model_create_multi
    def create(self, vals_list):

        teachers = super().create(vals_list)

        internal_group = self.env.ref('base.group_user')
        teacher_group = self.env.ref(
            'school_management.group_school_teacher'
        )

        for teacher in teachers:

            login = (
                teacher.email or teacher.name or ''
            ).replace(' ', '').lower()

            # Existing user check
            user = self.env['res.users'].search([
                ('login', '=', login)
            ], limit=1)

            # Create user if not exists
            if not user:

                user = self.env['res.users'].create({
                    'name': teacher.name,
                    'login': login,
                    'password': '1234',
                })

            # Assign groups
            user.write({
                'group_ids': [
                    (4, internal_group.id),
                    (4, teacher_group.id),
                ]
            })

            # Link user to teacher
            teacher.user_id = user.id

        return teachers

    # ---------------- SMART BUTTON ---------------- #
    def action_view_students(self):

        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'school.student',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.student_ids.ids)],
            'context': {
                'default_teacher_ids': [(4, self.id)]
            }
        }