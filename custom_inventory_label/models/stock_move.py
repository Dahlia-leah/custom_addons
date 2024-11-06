from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    label_product_name = fields.Char(string="Product Name", compute="_compute_label_details", store=True)
    label_product_id = fields.Many2one('product.product', string="Product ID", compute="_compute_label_details", store=True)
    label_material_name = fields.Char(string="Material Name", compute="_compute_label_details", store=True)
    label_material_id = fields.Many2one('product.product', string="Material ID", compute="_compute_label_details", store=True)
    label_lot_number = fields.Char(string="Lot Number", compute="_compute_label_details", store=True)
    label_batch_number = fields.Char(string="Batch Number", compute="_compute_label_details", store=True)
    label_date_printing = fields.Date(string="Date of Printing", default=fields.Date.today)
    label_expiration_date = fields.Date(string="Expiration Date", compute="_compute_label_details", store=True)
    label_expected_weight = fields.Float(string="Expected Weight", default=0.0)
    label_actual_weight = fields.Float(string="Actual Weight", default=0.0)
    receiver_signature = fields.Binary(string="Receiver's Signature", help="Signature of the receiver")
    supervisor_signature = fields.Binary(string="Supervisor's Signature", help="Signature of the supervisor")

    @api.depends('product_id', 'lot_ids')
    def _compute_label_details(self):
        for record in self:
            product = record.product_id
            lot = record.lot_ids[:1]  # Select the first lot if available

            record.label_product_name = product.name or ''
            record.label_product_id = product.id
            record.label_material_name = product.name or ''
            record.label_material_id = product.id
            record.label_lot_number = lot.name if lot else ''
            record.label_batch_number = lot.name if lot else ''
            record.label_expiration_date = (lot.expiration_date or
                                            (fields.Date.today() + timedelta(days=30)))

    def action_print_inventory_label(self):
        moves = self.env['stock.move'].browse(self.env.context.get('active_ids', []))
        _logger.info("Printing inventory labels for moves: %s", moves.ids)

        if not moves:
            raise UserError('No stock moves selected for label printing.')

        for move in moves:
            if (move.picking_type_id.id != 19 or
                move.location_id.id != 44 or
                move.location_dest_id.id != 45 or
                move.state != 'assigned'):
                raise UserError(f"Move {move.name}: Conditions not met for label printing.")
            if move.label_expected_weight <= 0.0 or move.label_actual_weight <= 0.0:
                raise UserError(f"Move {move.name}: Weight information is incomplete.")
            if not move.product_id or move.product_id.qty_available <= 0:
                raise UserError(f"Move {move.name}: Insufficient stock for label printing.")

        try:
            report_action = self.env.ref('custom_inventory_label.report_inventory_label').report_action(moves)
            _logger.info("Report generated successfully for moves: %s", moves.ids)
            return report_action
        except Exception as e:
            _logger.error("Error generating report: %s", e)
            raise UserError(f"Error generating report: {str(e)}")
