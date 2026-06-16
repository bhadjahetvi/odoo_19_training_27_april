from odoo import http
from odoo.http import request


class WebsiteInquiry(http.Controller):

    @http.route(['/inquiry'], type='http', auth="public", website=True)
    def form(self, **kw):

        countries = request.env['res.country'].sudo().search([], order='name')

        return request.render(
            "website_inquiry.inquiry_form_template",
            {
                'countries': countries,
                'error': kw.get('error'),
            }
        )

    @http.route(
        ['/inquiry/submit'],
        type='http',
        auth="public",
        website=True,
        methods=['POST'],
        csrf=True
    )
    def submit(self, **post):

        name = post.get('name')
        email = post.get('email')
        country_id = post.get('country_id')
        phone = post.get('phone')
        gender = post.get('gender')

        # -------------------------
        # BASIC VALIDATION (SERVER SIDE SAFETY)
        # -------------------------
        if not name or not email or not country_id or not phone:
            return request.redirect('/inquiry?error=missing_fields')

        # SAFE country convert
        try:
            country = request.env['res.country'].sudo().browse(int(country_id))
        except:
            return request.redirect('/inquiry?error=invalid_country')

        if not country.exists():
            return request.redirect('/inquiry?error=invalid_country')

        # -------------------------
        # PHONE VALIDATION
        # -------------------------
        country_code = f"+{country.phone_code or ''}"

        # extract entered code if exists
        entered_code = phone.split(' ')[0] if phone else ''

        if country_code and entered_code and entered_code != country_code:
            return request.redirect('/inquiry?error=phone_code')

        # -------------------------
        # CREATE RECORD
        # -------------------------
        request.env['website.inquiry'].sudo().create({
            'name': name,
            'email': email,
            'country_id': country.id,
            'phone': phone,
            'phone_code': country_code,
            'gender': gender,
        })

        # CRM Lead
        request.env['crm.lead'].sudo().create({
            'name': f'Inquiry - {name}',
            'contact_name': name,
            'email_from': email,
            'phone': phone,
        })

        return request.redirect('/inquiry/thankyou')

    @http.route(['/inquiry/thankyou'], type='http', auth="public", website=True)
    def thankyou(self):
        return request.render("website_inquiry.thank_you_template")