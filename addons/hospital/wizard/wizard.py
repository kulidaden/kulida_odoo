from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class AssignDoctorWizard(models.TransientModel):
    _name = 'assign.doctor.wizard'

    patients_ids = fields.Many2many('patient', string='Пацієнти')
    doctor_id = fields.Many2one('docktor', string='Лікар', required=True)

    def reassign_doctor(self):
        for patient in self.patients_ids:
            patient.doctor_id = self.doctor_id


class ChangeDoctorVisit(models.TransientModel):
    _name = 'change.doctor.visit.wizard'

    patient_id = fields.Many2one('patient', string='Пацієнт', required=True)
    doctor_id = fields.Many2one('docktor', string='Лікар', required=True)
    doctor_visit_id=fields.Many2one('docktor.visit',string='Відвідування лікаря')
    appointment_id=fields.Datetime(string='Запис на прийом', required=True)
    change_doctor_id=fields.Many2one('docktor', string='Лікар', required=True)
    change_appointment_id=fields.Datetime(string='Запис на прийом', required=True)

    def transfer_doctor_visit(self):
        existing_visits = self.env['docktor.visit'].search([
            ('docktor_ids', '=', self.doctor_id.id),
            ('patient_ids', '=', self.patient_id.id),
            ('appointment', '=', self.appointment_id),
        ])
        if existing_visits:
            existing_visits.write({
                'docktor_ids': self.change_doctor_id,
                'appointment': self.change_appointment_id,
            })
        else:
            raise ValidationError('Такого запису не існує!')


class DoctorScheduleWizard(models.TransientModel):
    _name = 'doctor.schedule.wizard'
    _description = 'Doctor Schedule Wizard'

    doctor_id=fields.Many2one('docktor', string='Лікар')
    week_type=fields.Selection(string='Тип тижня', selection=[
        ('парний','Парний тиждень'),
        ('непарний', 'Непарний тиждень')
    ])

    date=fields.Date()

    monday_start = fields.Datetime(string='Понеділок початок робочого дня')
    monday_end = fields.Datetime(string='Понеділок кінець робочого дня')
    tuesday_start = fields.Datetime(string='Вівторок початок робочого дня')
    tuesday_end = fields.Datetime(string='Вівторок кінець робочого дня')
    wednesday_start = fields.Datetime(string='Середа початок робочого дня')
    wednesday_end = fields.Datetime(string='Середа кінець робочого дня')
    thursday_start = fields.Datetime(string='Четверг початок робочого дня')
    thursday_end = fields.Datetime(string='Четверг кінець робочого дня')
    friday_start = fields.Datetime(string='П\'ятниця початок робочого дня')
    friday_end = fields.Datetime(string='П\'ятниця кінець робочого дня')
    saturday_start = fields.Datetime(string='Субота початок робочого дня')
    saturday_end = fields.Datetime(string='Субота кінець робочого дня')
    sunday_start = fields.Datetime(string='Неділя початок робочого дня')
    sunday_end = fields.Datetime(string='Неділя кінець робочого дня')

    @api.onchange('date')
    def _onchange_time_fields(self):
        if self.date:
            start_time = fields.Datetime.from_string(self.date)
            days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for i, day in enumerate(days_of_week):
                start_field = f'{day}_start'
                end_field = f'{day}_end'
                start_value = start_time + timedelta(days=i, hours=-3)
                end_value = start_time + timedelta(days=i, hours=-3)
                setattr(self, start_field, start_value)
                setattr(self, end_field, end_value)

    def apply_schedule(self):
        self.env['doctor.schedule'].search([
            ('doctor_id', '=', self.doctor_id.id),
            ('week_type', '=', self.week_type)
        ]).unlink()

        schedule_fields = {
            '0': (self.monday_start, self.monday_end),
            '1': (self.tuesday_start, self.tuesday_end),
            '2': (self.wednesday_start, self.wednesday_end),
            '3': (self.thursday_start, self.thursday_end),
            '4': (self.friday_start, self.friday_end),
            '5': (self.saturday_start, self.saturday_end),
            '6': (self.sunday_start, self.sunday_end),
        }

        for day, (start_time, end_time) in schedule_fields.items():
            if start_time != end_time:
                self.env['doctor.schedule'].create({
                    'doctor_id': self.doctor_id.id,
                    'start_time_invisible': start_time,
                    'end_time_invisible': end_time,
                    'date': start_time.date(),
                    'day_of_week': day,
                    'start_time': (start_time + timedelta(hours=+3)).strftime('%H:%M'),
                    'end_time': (end_time + timedelta(hours=+3)).strftime('%H:%M'),
                    'week_type': self.week_type,

                })
