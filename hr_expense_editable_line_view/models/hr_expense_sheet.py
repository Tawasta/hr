# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):

    _inherit = 'hr.expense.sheet'

    state = fields.Selection(selection=[
        ('draft', 'To Submit'),
        ('reported', 'Reported'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused'),
        ('refused', 'Refused'),
        ],
        default='draft',
        )

    @api.multi
    def write(self, vals):
        res = super(HrExpenseSheet, self).write(vals)
        for line in self.expense_line_ids:
            line.state = self.state
        return res

    @api.multi
    def reset_expense_sheets(self):
        res = super(HrExpenseSheet, self).reset_expense_sheets()
        self.write({'state': 'draft'})
        for line in self.expense_line_ids:
            line.write({'state': 'draft'})
        return

    @api.multi
    def submit_expenses(self):
        hr_expense = self.env['hr.expense']
        if any(expense.state != 'draft' for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report!"))
        return self.write({'state': 'submit'})

class HrExpense(models.Model):

    _inherit = 'hr.expense'

    state = fields.Selection(selection=[
        ('draft', 'To Submit'),
        ('reported', 'Reported'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused'),
        ('refused', 'Refused'),
        ],
        default='draft',
        )
