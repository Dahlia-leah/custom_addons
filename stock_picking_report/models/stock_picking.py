from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging

# Setting up a logger to record important information and errors
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.move'  # Inheriting from the 'stock.move' model to extend its functionality

    # Fields to store data retrieved from an external source
    external_weight = fields.Char(string='External Weight', readonly=True)  # External weight, read-only
    external_unit = fields.Char(string='External Unit', readonly=True)  # Unit of the weight, read-only
    time_printing = fields.Datetime(string="Time of Printing", default=fields.Datetime.now)  # Time of printing, default to now
    expiration_time = fields.Integer(
        string="Expiration Time",
        related='product_id.product_tmpl_id.expiration_time',  # Related field to fetch expiration time from product template
        readonly=True,  # Read-only because it's computed from another field
        help="Expiration time of the product, as specified in the product template."  # Help text for guidance
    )

    def fetch_and_print_report(self):
        """Fetch weight data from the external API and update fields."""
        remote_server_url = 'http://127.0.0.1:5001/balance'  # URL of the external API to fetch weight data

        try:
            # Making a GET request to the external API
            response = requests.get(remote_server_url, timeout=5)
            if response.status_code == 200:  # Checking if the response is successful
                data = response.json()  # Parsing the JSON response
                _logger.info(f"API response: {data}")

                # Extracting unit and weight from the response
                unit = data.get('unite', '')  # Fetch 'unite' from the response, default to an empty string if not found
                weight = data.get('value', '')  # Fetch 'value' from the response, default to an empty string if not found

                # Updating fields if weight is available
                if weight:
                    self.write({
                        'external_weight': weight,  # Updating the external weight field
                        'external_unit': unit  # Updating the external unit field
                    })
                    _logger.info("Updated fields with external weight and unit.")
                else:
                    _logger.warning("No weight received, fields will remain empty.")
                    self.write({'external_weight': '', 'external_unit': ''})  # Clearing fields if no weight is received
            else:
                _logger.error(f"Failed to fetch data: {response.status_code}")
                self.write({'external_weight': '', 'external_unit': ''})  # Clearing fields on failed response

        # Handling exceptions related to the API request
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error connecting to API: {e}")
            self.write({'external_weight': '', 'external_unit': ''})  # Clearing fields on connection error

        # Calling the report action to print the report
        return self.action_print_report()

    def action_print_report(self):
        # Reference the report action for stock picking and execute it
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)  # Trigger the report action
        else:
            raise UserError("Report action not found.")  # Raise an error if the report action is not found
