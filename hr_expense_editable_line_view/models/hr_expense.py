# -*- coding: utf-8 -*-


from odoo import fields, models


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
