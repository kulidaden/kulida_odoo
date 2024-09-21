from odoo import fields, models


class Classification(models.Model):
    _name = 'classification'
    _description = 'Classification'

    name = fields.Char(string='Назва класифікації', required=True)


class TypeOfDiagnosis(models.Model):
    _name = 'type.of.diagnosis'
    _description = 'Type of diagnosis'

    name = fields.Char(string='Тип діагнозу', required=True)


class ExampleExploration(models.Model):
    _name = 'example.exploration'
    _description = 'Example exploration'

    name=fields.Char(string='Зразок')


class Specialisation(models.Model):
    _name = "specialisation.ids"
    _description = 'Specialisation'

    name=fields.Char(string='Спеціальнісь')


class MethodDiagnosis(models.Model):
    _name = "method.diagnosis"
    _description = 'Method Diagnosis'

    name=fields.Char(string='Метод діагностики')









