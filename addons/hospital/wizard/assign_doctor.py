from odoo import models, fields


class AssignDoctorWizard(models.TransientModel):
    _name = 'assign.doctor.wizard'

    patients_ids = fields.Many2many('patient', string='Пацієнти')
    doctor_id = fields.Many2one('docktor', string='Лікар', required=True)

    def reassign_doctor(self, additional_arg=None):
        for patient in self.patients_ids:
            patient.doctor_id = self.doctor_id


class ChangeDoctorVisit(models.TransientModel):
    _name = 'change.doctor.visit'

