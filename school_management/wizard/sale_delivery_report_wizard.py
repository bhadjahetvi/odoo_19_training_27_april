from odoo import models, fields


class SaleDeliveryReportWizard(models.TransientModel):
    _name = 'sale.delivery.report.wizard'
    _description = 'Sales Delivery Report Wizard'

    report_type = fields.Selection([
        ('by_order', 'By Order'),
        ('by_product', 'By Product'),
        ('by_warehouse', 'By Warehouse')
    ], string='Report Type', required=True, default='by_order')

    def action_print_report(self):
        # DEBUG (optional but useful)
        print("REPORT TYPE SELECTED:", self.report_type)

        report = self.env.ref(
            'school_management.action_sale_delivery_report_xlsx'
        )

        return report.report_action(self)