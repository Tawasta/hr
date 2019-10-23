from odoo import api, models, fields
import datetime


class Employee(models.Model):

    _inherit = 'hr.employee'

    def get_hours_worked(self, today):

        hour_balance_end = datetime.datetime.strftime(today, '%Y-%m-%d')

        timesheet_lines = self.env['account.analytic.line']\
            .search(args=[
                ('employee_id', '=', self.id),
                ('date', '>=', self.hour_balance_start),
                ('date', '<=', hour_balance_end)])

        hours_worked = sum(timesheet_line.unit_amount
                           for timesheet_line
                           in timesheet_lines)

        print("Hours worked: " + str(hours_worked))
        return hours_worked


    def get_hours_needed(self, date_to_check, today):

        def hours_from_attendance(att):
            # Only the hour value matters
            start_time = datetime.datetime(
                year=1990,
                month=3,
                day=28,
                hour=int(att.hour_from))
            # Only the hour value matters
            end_time = datetime.datetime(
                year=1990,
                month=3,
                day=28,
                hour=int(att.hour_to))
            # Convert seconds to hours by division
            return (end_time - start_time).seconds / 60 / 60


        def hours_in_weekday(attendance_ids):
            weekday_hours = [0, 0, 0, 0, 0, 0, 0]
            for att_id in attendance_ids:
                weekday_hours[int(att_id.dayofweek)] += hours_from_attendance(att_id)
            return weekday_hours


        def count_weekdays(start_date, end_date):
            end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()
            weekday_occurences = [0, 0, 0 ,0, 0, 0, 0]
            for n in range(int ((end_date -  start_date).days)):
                wd = (date_to_check + datetime.timedelta(n)).weekday()
                weekday_occurences[wd] += 1
            return weekday_occurences


        def multiply_weekday_hours_by_count(hours, occurences):
            weekday_hours_multiplied = [0, 0, 0, 0, 0, 0, 0]
            for wd in range(0,6):
                weekday_hours_multiplied[wd] = hours[wd] * occurences[wd]
            return weekday_hours_multiplied


        hours_needed = sum(
            multiply_weekday_hours_by_count(
                hours_in_weekday(self.resource_calendar_id.attendance_ids),
                count_weekdays(date_to_check, today)))

        print("Hours needed:" + str(hours_needed))
        return hours_needed


    @api.depends(
        'hour_balance_start',
        'timesheet_lines',
        'timesheet_lines.unit_amount',
        'resource_calendar_id')
    @api.one
    def _get_hour_balance(self):
        if self.resource_calendar_id and self.hour_balance_start:

            today = datetime.datetime.now().date()

            self.hour_balance = \
                self.get_hours_worked(today)\
                -\
                self.get_hours_needed(
                    self.hour_balance_start,
                    today)
        else:
            self.hour_balance = 0

        print("Hour balance: " + str(self.hour_balance))

    @api.one
    def _get_show_balance(self):
        self.show_balance = self.user_id.id == self.env.uid and True or False


    hour_balance_start = fields.Date(
        string='Hour Balance Start Date',
        help='''
            Date from which onwards the hour balance is
            calculated. Set this as the date when the user
            started filling out timesheets.''')

    hour_balance = fields.Float(
        string='Hour Balance',
        compute=_get_hour_balance,
        store=True)

    timesheet_lines = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='employee_id',
        string='Timesheet lines')

    show_balance = fields.Boolean(
        string='Show Hour Balance',
        compute=_get_show_balance)
