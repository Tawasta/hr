# -*- coding: utf-8 -*-


from odoo import fields, models


class HrExpenseSheet(models.Model):

    _inherit = 'hr.expense.sheet'

    product_id = fields.Many2one(
            'product.product',
            string="Product",
            related='expense_line_ids.product_id',
            )

    quantity = fields.Float(
            string='Quantity',
            related='expense_line_ids.quantity',
            )

    unit_amount = fields.Float(
            string='Unit Price',
            related='expense_line_ids.unit_amount',
            )

