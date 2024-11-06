from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    label_product_name = fields.Char(string="Product Name", compute="_compute_label_details")
    label_product_id = fields.Many2one('product.product', string="Product ID", compute="_compute_label_details")
    label_material_name = fields.Char(string="Material Name", compute="_compute_label_details")
    label_material_id = fields.Many2one('product.product', string="Material ID", compute="_compute_label_details")
    label_lot_number = fields.Char(string="Lot Number", compute="_compute_label_details")
    label_date_printing = fields.Date(string="Date of Printing", default=fields.Date.today)
    label_expiration_date = fields.Date(string="Expiration Date", compute="_compute_label_details")
    label_expected_weight = fields.Float(string="Expected Weight")
    label_actual_weight = fields.Float(string="Actual Weight", default=0.0)

    @api.depends('move_lines.product_id', 'move_lines.lot_ids', 'move_lines.product_id.expiration_date')
    def _compute_label_details(self):
        for record in self:
            if record.label_date_printing is None:
                record.label_date_printing = fields.Date.today()

            # Reset values before computing new ones
            record.label_product_name = ''
            record.label_product_id = False
            record.label_material_name = ''
            record.label_material_id = False
            record.label_lot_number = ''
            record.label_expiration_date = False

            # Compute fields based on the first available move line
            move = record.move_lines[:1]
            if move:
                record.label_product_name = move.product_id.name
                record.label_product_id = move.product_id.id
                record.label_material_name = move.product_id.name
                record.label_material_id = move.product_id.id
                record.label_lot_number = move.lot_ids[:1].name if move.lot_ids else ''
                record.label_expiration_date = move.product_id.expiration_date or fields.Date.today() + timedelta(days=30)

            # Set expected and actual weight to 0.0 if not already set
            if record.label_expected_weight is None:
                record.label_expected_weight = 0.0
            if record.label_actual_weight is None:
                record.label_actual_weight = 0.0

    @api.model
    def action_print_inventory_label(self):
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_ids', []))

        _logger.info("Attempting to print inventory labels for pickings: %s", pickings.ids)

        if not pickings:
            _logger.error('No pickings found to print the label.')
            raise UserError('No pickings found to print the label.')

        # Check if all necessary fields are set for printing
        for picking in pickings:
            if not picking.label_expected_weight or not picking.label_actual_weight:
                raise UserError(f'Pick {picking.name} is missing weight information.')

        try:
            report_action = self.env.ref('custom_inventory_label.report_inventory_label').report_action(pickings)
            _logger.info("Successfully generated report for pickings: %s", pickings.ids)
            return report_action
        except Exception as e:
            _logger.error("Error generating report: %s", e)
            raise UserError(f'Error generating report: {str(e)}')