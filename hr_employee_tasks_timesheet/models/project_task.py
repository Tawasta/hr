from datetime import datetime
from datetime import timedelta

from odoo import api
from odoo import fields
from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    employee_resource_hours = fields.Float(
        string="Resource hours",
        compute="_compute_employee_workload",
        store=True,
        help="Employee hours resource for this week",
    )
    employee_workload_percentage = fields.Float(
        string="Weekly workload",
        compute="_compute_employee_workload",
        store=True,
        help="The portion of weekly workload from this task",
    )
    employee_resource_overload = fields.Boolean(
        string="Employee overload",
        help="Employee resource is overloaded for this week",
        compute="_compute_employee_workload",
        store=True,
    )

    @api.onchange("date_deadline", "employee_id", "planned_hours")
    @api.depends("date_deadline", "employee_id", "planned_hours")
    def _compute_employee_workload(self):
        for record in self:
            if not record.date_deadline:
                continue

            deadline = record.date_deadline
            week_start = deadline - timedelta(days=deadline.weekday())
            week_end = week_start + timedelta(days=6)

            time_start = datetime.combine(week_start, datetime.min.time())
            time_end = datetime.combine(week_end, datetime.max.time())

            workload = record.employee_id.get_work_days_data(
                time_start, time_end, True, record.employee_id.resource_calendar_id
            )["hours"]
            workload_percentage = record.planned_hours / workload * 100

            record.employee_resource_hours = workload
            record.employee_workload_percentage = workload_percentage

            if workload_percentage >= 100:
                record.employee_resource_overload = True
