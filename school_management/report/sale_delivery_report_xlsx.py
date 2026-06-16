from odoo import models


class SaleDeliveryReportXlsx(models.AbstractModel):
    _name = 'report.school_management.sale_delivery_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):

        sheet = workbook.add_worksheet('Delivery Report')

        # =========================================================
        # REPORT TYPE NAME (NEW ADDITION)
        # =========================================================
        report_type = getattr(wizard, 'report_type', False)

        report_name_map = {
            'by_order': 'BY ORDER REPORT',
            'by_product': 'BY PRODUCT REPORT',
            'by_warehouse': 'BY WAREHOUSE REPORT'
        }

        report_title = report_name_map.get(report_type, 'UNKNOWN REPORT')

        # =========================================================
        # FORMATS
        # =========================================================
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center'
        })

        header_format = workbook.add_format({
            'bold': True
        })

        # =========================================================
        # TITLE ROW (NEW)
        # =========================================================
        sheet.merge_range('A1:G1', report_title, title_format)

        # =========================================================
        # HEADERS
        # =========================================================
        headers = [
            'Order ID',
            'Delivery Number',
            'Product',
            'Warehouse',
            'Sale Order Confirm Date',
            'Order Delivery Date',
            'Total Time'
        ]

        for col, h in enumerate(headers):
            sheet.write(2, col, h, header_format)

        row = 3

        # =========================================================
        # COMMON DOMAIN
        # =========================================================
        domain = [('state', '=', 'sale')]
        orders = self.env['sale.order'].search(domain)

        # =========================================================
        # BY ORDER
        # =========================================================
        if report_type == 'by_order':

            for order in orders:

                picking = self.env['stock.picking'].search([
                    ('origin', '=', order.name),
                    ('state', '=', 'done')
                ], limit=1, order='date_done desc')

                delivery_number = picking.name if picking else ''

                products = ", ".join(
                    order.order_line.filtered(
                        lambda l: l.product_id
                    ).mapped('product_id.name')
                )

                confirm_date = order.date_order
                delivery_date = picking.date_done if picking else False

                total_time = ""
                if confirm_date and delivery_date:
                    diff = delivery_date - confirm_date
                    total_time = f"{diff.days} Days"

                sheet.write(row, 0, order.name or '')
                sheet.write(row, 1, delivery_number)
                sheet.write(row, 2, products)
                sheet.write(row, 3,
                            order.warehouse_id.name if order.warehouse_id else 'My Company')
                sheet.write(row, 4, str(confirm_date) if confirm_date else '')
                sheet.write(row, 5, str(delivery_date) if delivery_date else '')
                sheet.write(row, 6, total_time)

                row += 1

        # =========================================================
        # BY PRODUCT
        # =========================================================
        elif report_type == 'by_product':

            for order in orders:

                picking = self.env['stock.picking'].search([
                    ('origin', '=', order.name),
                    ('state', '=', 'done')
                ], limit=1, order='date_done desc')

                delivery_number = picking.name if picking else ''

                for line in order.order_line:

                    if not line.product_id:
                        continue

                    confirm_date = order.date_order
                    delivery_date = picking.date_done if picking else False

                    total_time = ""
                    if confirm_date and delivery_date:
                        diff = delivery_date - confirm_date
                        total_time = f"{diff.days} Days"

                    sheet.write(row, 0, order.name or '')
                    sheet.write(row, 1, delivery_number)
                    sheet.write(row, 2, line.product_id.name)
                    sheet.write(row, 3,
                                order.warehouse_id.name if order.warehouse_id else 'My Company')
                    sheet.write(row, 4, str(confirm_date) if confirm_date else '')
                    sheet.write(row, 5, str(delivery_date) if delivery_date else '')
                    sheet.write(row, 6, total_time)

                    row += 1

        # =========================================================
        # BY WAREHOUSE
        # =========================================================
        elif report_type == 'by_warehouse':

            warehouses = {}

            for order in orders:
                wh_name = order.warehouse_id.name if order.warehouse_id else 'My Company'

                if wh_name not in warehouses:
                    warehouses[wh_name] = []

                warehouses[wh_name].append(order)

            for wh_name, wh_orders in warehouses.items():

                for order in wh_orders:

                    picking = self.env['stock.picking'].search([
                        ('origin', '=', order.name),
                        ('state', '=', 'done')
                    ], limit=1, order='date_done desc')

                    delivery_number = picking.name if picking else ''

                    products = ", ".join(
                        order.order_line.filtered(
                            lambda l: l.product_id
                        ).mapped('product_id.name')
                    )

                    confirm_date = order.date_order
                    delivery_date = picking.date_done if picking else False

                    total_time = ""
                    if confirm_date and delivery_date:
                        diff = delivery_date - confirm_date
                        total_time = f"{diff.days} Days"

                    sheet.write(row, 0, order.name or '')
                    sheet.write(row, 1, delivery_number)
                    sheet.write(row, 2, products)
                    sheet.write(row, 3, wh_name)
                    sheet.write(row, 4, str(confirm_date) if confirm_date else '')
                    sheet.write(row, 5, str(delivery_date) if delivery_date else '')
                    sheet.write(row, 6, total_time)

                    row += 1