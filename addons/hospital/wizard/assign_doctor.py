from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from datetime import timedelta


_logger = logging.getLogger(__name__)


class AssignDoctorWizard(models.TransientModel):
    _name = 'assign.doctor.wizard'

    patients_ids = fields.Many2many('patient', string='Пацієнти')
    doctor_id = fields.Many2one('docktor', string='Лікар', required=True)

    def reassign_doctor(self, additional_arg=None):
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
            ('patient_ids', 'in', self.patient_id.ids),
            ('appointment', '=', self.appointment_id),
        ])
        if existing_visits:
            existing_visits.write({
                'docktor_ids': self.change_doctor_id,
                'appointment': self.change_appointment_id,
            })
        else:
            raise ValidationError('Такого запису не існує!')
