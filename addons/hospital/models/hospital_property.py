from odoo import fields, models

class HospitalProperty(models.Model):
    _name = "hospital.property"
    _description = 'Hospital Property'

class DirectoryOfDiseases(models.Model):
    _name = 'directory.of.diseases'
    _description = 'Directory of diseases'

    name = fields.Char(string='Назва хвороби', required=True)
    type_of_diseases = fields.Char(string='Тип хвороби', required=True)
    description = fields.Text(string='Опис хвороби', required=True)
    classification = fields.Char(string='Класифікація', required=True)
    method_diagnosis = fields.Char(string='Метод діагностики', required=True)
    treatment = fields.Text(string='Лікування')
