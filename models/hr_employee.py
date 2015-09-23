# -*- coding: utf-8 -*-
from openerp import models, api, fields
from openerp import tools
from openerp import exceptions
from openerp import _

import re
import logging
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    ''' SALES '''
    show_group_sales = fields.Boolean(
        compute='compute_show_group_sales',
    )
    group_sales = fields.Selection(
        selection='get_group_sales',
        inverse='set_group_sales',
        string='Sales role',
        default='salesperson',
    )

    ''' PROJECT '''
    show_group_project = fields.Boolean(
        compute='compute_show_group_project',
    )
    group_project = fields.Selection(
        selection='get_group_project',
        inverse='set_group_project',
        string='Projects role',
        default='user',
    )

    ''' ACCOUNT '''
    show_group_account = fields.Boolean(
        compute='compute_show_group_account',
    )
    group_account = fields.Selection(
        selection='get_group_account',
        inverse='set_group_account',
        string='Finance role',
        default='invoicing',
    )

    ''' HR '''
    show_group_hr = fields.Boolean(
        compute='compute_show_group_hr',
    )
    group_hr = fields.Selection(
        selection='get_group_hr',
        inverse='set_group_hr',
        string='Human relations role',
        default='employee',
        required=True,
    )

    ''' USER RELATION '''
    user_state = fields.Char(
        compute='get_user_state',
        readonly=True
    )

    ''' Onchanges '''
    @api.onchange('name')
    def onchange_name(self):
        groups = []

        groups.append(
            self.get_group_by_name('See all Leads', 'Sales').id or False)
        groups.append(
            self.get_group_by_name('Employee', 'Human Resources').id or False)

    @api.onchange('work_email')
    def onchange_work_email(self):
        if self.work_email:
            valid_email = re.match(tools.single_email_re, self.work_email)

            if not valid_email:
                raise exceptions.Warning("Invalid email!")

    ''' Main function overrides '''
    @api.model
    def create(self, vals):
        ''' Creates an user and sets default permission rights '''

        if not self.user_id:
            vals = self.create_user(vals)

        return super(HrEmployee, self).create(vals)

    @api.one
    def write(self, vals):
        if self.user_id and 'work_email' in vals:
            self.sudo().user_id.login = vals['work_email']

        return super(HrEmployee, self).write(vals)

    @api.one
    def unlink(self):
        self.sudo().user_id.active = False

        super(HrEmployee, self).unlink()

    ''' User creation '''
    def create_user(self, vals):
        users_object = self.env['res.users']

        user_vals = {
            'login': vals['work_email'],
            'name': vals['name'],
            # 'groups_id': {(6, False, self.get_default_groups())}
        }

        user_id = users_object.sudo().create(user_vals)

        vals['user_id'] = user_id.id
        vals['address_home_id'] = user_id.partner_id.id

        user_id.partner_id.email = vals['work_email']
        user_id.partner_id.phone = vals['mobile_phone']

        return vals

    def get_user_state(self):
        self.user_state = ('active' if self.user_id.login_date else 'new')

    ''' SALES '''
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
            self.sudo().user_id.groups_id = [(3, sales_group.id)]

        ''' Set the new sale group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' PROJECT '''
    def get_group_project(self):
        group = [
            ('user', 'User'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_project(self):
        if not self.group_project:
            group = False

        elif self.group_project == 'user':
            group = self.get_group_by_name("User", "Project")

        elif self.group_project == 'manager':
            group = self.get_group_by_name("Manager", "Project")

        project_groups = self.get_groups_by_category_name("Project")

        ''' Unset current project groups '''
        for project_group in project_groups:
            self.sudo().user_id.groups_id = [(3, project_group.id)]

        ''' Set the new project group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' ACCOUNT '''
    def get_group_account(self):
        group = [
            ('view', 'View'),
            ('invoicing', 'Invoicing'),
            ('accountant', 'Accountant'),
            ('manager', 'Manager'),
        ]

        return group

    def set_group_account(self):
        if not self.group_account:
            group = False

        elif self.group_account == 'view':
            group = self.get_group_by_name("Can view", "Accounting")

        elif self.group_account == 'invoicing':
            group = self.get_group_by_name("Invoicing", "Accounting")

        elif self.group_account == 'accountant':
            group = self.get_group_by_name("Accountant", "Accounting")

        elif self.group_account == 'manager':
            group = self.get_group_by_name("Financial Manager", "Accounting")

        account_groups = self.get_groups_by_category_name("Accounting")

        ''' Unset current account groups '''
        for group_account in account_groups:
            self.sudo().user_id.groups_id = [(3, group_account.id)]

        ''' Set the new account group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]

    ''' HUMAN RESOURCES '''
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
            self.sudo().user_id.groups_id = [(3, hr_group.id)]

        ''' Set the new sale group '''
        if group:
            self.sudo().user_id.groups_id = [(4, group.id)]