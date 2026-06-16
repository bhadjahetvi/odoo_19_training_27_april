import csv
import io
import base64
import logging

from datetime import timedelta

from odoo import models, api

_logger = logging.getLogger(__name__)


class WeeklySaleReport(models.Model):
    _inherit = 'sale.order'

    @api.model
    def generate_weekly_sale_report(self):
        _logger.info("Weekly Sale Report Cron Started")

        orders = self.search(
            [('state', 'in', ['sale', 'done'])],
            order='date_order asc'
        )

        if not orders:
            _logger.info("No Sale Orders Found")
            return False

        # First and last sale order dates
        first_date = orders[0].date_order.date()
        last_date = orders[-1].date_order.date()

        # Start from Monday of first week
        start_week = first_date - timedelta(days=first_date.weekday())

        # End on Sunday of last week
        end_week = last_date + timedelta(days=(6 - last_date.weekday()))

        # Create week buckets
        week_data = {}

        current_week = start_week
        while current_week <= end_week:
            week_data[current_week] = {
                'total_amount': 0.0,
                'total_orders': 0,
            }
            current_week += timedelta(days=7)

        # Calculate totals
        for order in orders:
            order_date = order.date_order.date()

            week_start = order_date - timedelta(
                days=order_date.weekday()
            )

            week_data[week_start]['total_amount'] += order.amount_total
            week_data[week_start]['total_orders'] += 1

        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            'Week Start',
            'Week End',
            'Total Sale Orders',
            'Total Amount'
        ])

        for week_start in sorted(week_data.keys()):
            week_end = week_start + timedelta(days=6)

            writer.writerow([
                week_start.strftime('%d/%m/%Y'),
                week_end.strftime('%d/%m/%Y'),
                week_data[week_start]['total_orders'],
                round(week_data[week_start]['total_amount'], 2)
            ])

        csv_content = output.getvalue()
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'Weekly_Sale_Report.csv',
            'type': 'binary',
            'datas': base64.b64encode(
                csv_content.encode('utf-8')
            ),
            'mimetype': 'text/csv',
        })

        _logger.info(
            "Weekly Sale Report Created Successfully. Attachment ID: %s",
            attachment.id
        )

        return attachment