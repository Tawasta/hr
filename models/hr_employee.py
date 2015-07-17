# -*- coding: utf-8 -*-
from openerp import models, api, fields

import logging
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    group_sales = fields.Selection(
        selection='get_group_sales',
        inverse='set_group_sales',
        string='Sales role'
    )

    group_hr = fields.Selection(
        selection='get_group_hr',
        inverse='set_group_hr',
        string='Human relations role',
        required=True,
    )

    @api.onchange('name')
    def onchange_name(self):
        groups = []

        groups.append(
            self.get_group_by_name('See all Leads', 'Sales').id or False)
        groups.append(
            self.get_group_by_name('Employee', 'Human Resources').id or False)

    @api.model
    def create(self, vals):
        ''' Creates an user and sets default permission rights '''

        if not self.user_id:
            vals = self.create_user(vals)

        return super(HrEmployee, self).create(vals)

    def create_user(self, vals):
        users_object = self.env['res.users']

        user_vals = {
            'login': vals['work_email'],
            'name': vals['name'],
            'groups_id': {(6, False, self.get_default_groups())}
        }

        user_id = users_object.sudo().create(user_vals)

        vals['user_id'] = user_id.id
        vals['address_home_id'] = user_id.partner_id.id

        return vals

    '''
    SALES
    '''
    def get_group_sales(self):
        group = [
            ('salesperson', 'Salesperson'),
            ('salesmanager', 'Manager'),
        ]

        return group

    def set_group_sales(self):
        if not self.group_sales:
            group = False

        elif self.group_sales == 'salesperson':
            group = self.get_group_by_name("See all Leads", "Sales")

        elif self.group_sales == 'salesmanager':
            group = self.get_group_by_name("Manager", "Sales")

        sales_groups = self.get_groups_by_category_name("Sales")

        ''' Unset current sale groups '''
        for sales_group in sales_groups:
            self.user_id.groups_id = [(3, sales_group.id)]

        ''' Set the new sale group '''
        if group:
            self.user_id.groups_id = [(4, group.id)]

    '''
    HUMAN RESOURCES
    '''
    def get_group_hr(self):
        group = [
            ('employee', 'Employee'),
            ('officer', 'Officer'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_hr(self):
        category_name = "Human Resources"

        if not self.group_hr:
            group = False

        elif self.group_hr == 'employee':
            group = self.get_group_by_name("Employee", category_name)

        elif self.group_hr == 'officer':
            group = self.get_group_by_name("Officer", category_name)

        elif self.group_hr == 'manager':
            group = self.get_group_by_name("Manager", category_name)

        hr_groups = self.get_groups_by_category_name(category_name)

        ''' Unset current sale groups '''
        for hr_group in hr_groups:
            _logger.warn("Unsetting %s", hr_group.id)
            self.user_id.groups_id = [(3, hr_group.id)]

        ''' Set the new sale group '''
        if group:
            self.user_id.groups_id = [(4, group.id)]

    def get_group_by_name(self, group_name, category_name):
        # Gets security group by group name
        groups_obj = self.env['res.groups']

        groups = self.get_groups_by_category_name(category_name)

        group = groups_obj.search([('name', 'ilike', group_name),
                                   ('id', 'in', groups.ids)])

        return group

    def get_groups_by_category_name(self, category_name):
        # Gets security groups by category name
        groups_obj = self.env['res.groups']

        groups = groups_obj.search(
            [('category_id.name', 'ilike', category_name)]
        )

        return groups

    def get_default_groups(self):
        groups = []

        groups.append(
            self.get_group_by_name('See all Leads', 'Sales').id or False)
        groups.append(
            self.get_group_by_name('Employee', 'Human Resources').id or False)

        return tuple(groups)
