from odoo import models, fields


class WebsiteInquiry(models.Model):
    _name = "website.inquiry"
    _description = "Website Inquiry"

    name = fields.Char(required=True)
    email = fields.Char()
    country_id = fields.Many2one('res.country')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    phone = fields.Char()
    phone_code = fields.Char()