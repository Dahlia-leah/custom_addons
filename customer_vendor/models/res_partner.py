from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    CUSTOMER = 'customer'
    VENDOR = 'vendor'
    BOTH = 'both'

    customer_vendor_type = fields.Selection([
        (CUSTOMER, 'Customer'),
        (VENDOR, 'Vendor'),
        (BOTH, 'Both')
    ], string="Customer/Vendor Type", default=CUSTOMER, required=True)

    @api.model
    def create(self, vals):
        # Create the partner and update ranks
        partner = super(ResPartner, self).create(vals)
        if 'customer_vendor_type' in vals:
            self._update_ranks(partner, vals['customer_vendor_type'])
        return partner

    def write(self, vals):
        # Update partner and ranks if customer_vendor_type is changed
        res = super(ResPartner, self).write(vals)
        if 'customer_vendor_type' in vals:
            for record in self:
                self._update_ranks(record, vals['customer_vendor_type'])
        return res

    def _update_ranks(self, partner, vendor_type):
        """Update customer and supplier ranks based on the selected vendor_type."""
        if vendor_type == self.CUSTOMER:
            partner.customer_rank = 1
            partner.supplier_rank = 0
        elif vendor_type == self.VENDOR:
            partner.customer_rank = 0
            partner.supplier_rank = 1
        elif vendor_type == self.BOTH:
            partner.customer_rank = 1
            partner.supplier_rank = 1
        else:
            partner.customer_rank = 0
            partner.supplier_rank = 0

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """Override name_search to filter partners by type based on context."""
        if args is None:
            args = []
        if name:
            args += [('name', operator, name)]

        partner_type = self.env.context.get('partner_type_filter')
        if partner_type == self.CUSTOMER:
            args += [('customer_rank', '>', 0)]
        elif partner_type == self.VENDOR:
            args += [('supplier_rank', '>', 0)]

        return super(ResPartner, self).name_search(name, args=args, operator=operator, limit=limit)
