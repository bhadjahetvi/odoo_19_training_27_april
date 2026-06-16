from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):

        # Validate delivery first
        res = super().button_validate()

        for picking in self:

            # Only outgoing deliveries
            if picking.picking_type_id.code != 'outgoing':
                continue

            # Find related Sale Order
            sale_order = self.env['sale.order'].search([
                ('name', '=', picking.origin)
            ], limit=1)

            if not sale_order:
                continue

            # -----------------------------------------
            # RECOMPUTE DELIVERED QTY
            # -----------------------------------------

            for line in sale_order.order_line:

                # Skip note/section lines
                if line.display_type:
                    continue

                # Recompute delivered qty
                line._compute_qty_delivered()

            # -----------------------------------------
            # HANDLE COMBO PRODUCTS ONLY
            # -----------------------------------------

            for line in sale_order.order_line:

                # Skip lines without product
                if not line.product_id:
                    continue

                # Find combo child lines
                child_lines = sale_order.order_line.filtered(
                    lambda l: l.linked_line_id == line
                )

                # Only for combo parent
                if child_lines:

                    # Total child delivered qty
                    total_delivered = sum(
                        child_lines.mapped('qty_delivered')
                    )

                    # Update combo parent delivered qty
                    line.qty_delivered = total_delivered

            # -----------------------------------------
            # CHECK INVOICEABLE LINES
            # -----------------------------------------

            invoiceable_lines = sale_order.order_line.filtered(
                lambda l:
                l.qty_delivered > 0 and
                l.qty_invoiced < l.qty_delivered
            )

            if not invoiceable_lines:
                continue

            # -----------------------------------------
            # CREATE INVOICE
            # -----------------------------------------

            invoices = sale_order._create_invoices()

            # Auto post invoice
            for invoice in invoices:
                invoice.action_post()

        return res