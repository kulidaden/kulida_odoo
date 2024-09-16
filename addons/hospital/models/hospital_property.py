from odoo import fields, models, api
from datetime import datetime


class HospitalProperty(models.Model):
    _name = "hospital.property"
    _description = 'Hospital Property'


class Person(models.Model):
    _name = 'person'
    _description = 'Person'

    name = fields.Char(string='ПІБ', default=' ', required=True)
    mobile_phone=fields.Integer(string='Номер телефону')
    email=fields.Char(string='Емайл')
    photo=fields.Binary(string='Фото')
    sex=fields.Selection(string='Стать', selection=[
        ('чоловіча','Чоловіча'),
        ('жіноча','Жіноча')
    ])


class Patient(models.Model):
    _inherit = 'person'
    _name = 'patient'
    _description = 'Patient'

    birthday = fields.Date(string='Дата народження')
    age = fields.Integer(string='Вік', compute='_compute_age', store=True)
    choose_id_pass=fields.Selection(string='Паспортні дані', selection=[
        ('id карта', 'ID карта'),
        ('паспорт', 'Паспорт')
    ])
    id_card=fields.Integer(string='Номер id картки')
    id_code=fields.Integer(string='Ідентифікаційний код')
    issuing_body=fields.Integer(string='Орган що видав')
    numb_pass=fields.Integer(string='Номер паспорта')
    record_numb=fields.Integer(string='Запис №')
    contact_pers_id=fields.Many2one('contact.person', string='Контакстна особа')
    personal_docktor=fields.Many2one('docktor', string='Персональний лікар')
    diagnosis_ids = fields.One2many('diagnosis', 'patient_ids', string='Діагнози')

    contact_name = fields.Char(related='contact_pers_id.name', string='ПІБ', store=True)
    contact_mobile_phone = fields.Integer(related='contact_pers_id.mobile_phone', string='Телефон контактної особи', store=True)
    contact_email = fields.Char(related='contact_pers_id.email', string='Електронна пошта контактної особи', store=True)
    contact_relationship = fields.Selection(related='contact_pers_id.relationship', string='Стосунки з пацієнтом',
                                       store=True)
    doctor_id = fields.Many2one('docktor', string='Лікар')
    doctor_name = fields.Char(related='doctor_id.name', string='ПІБ лікаря', store=True)
    doctor_specialisation = fields.Selection(related='doctor_id.specialisation', string='Спеціальність лікаря', store=True)
    doctor_type = fields.Selection(related='doctor_id.doctor_type', string='Тип лікаря', store=True)

    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                today = datetime.today()
                birthday = fields.Date.from_string(record.birthday)
                age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
                record.age = age
            else:
                record.age = 0


class ContactPerson(models.Model):
    _inherit = 'person'
    _name = 'contact.person'
    _description = 'Contact Person'

    relationship = fields.Selection([
        ('parent', 'Батько/Мати'),
        ('spouse', 'Чоловік/Дружина'),
        ('child', 'Дитина'),
        ('friend', 'Друг'),
        ('other', 'Інший')
    ], string='Відношення до пацієнта', required=True)
    patient_ids = fields.One2many('patient', 'contact_pers_id', string='Пацієнти')

class Docktor(models.Model):
    _inherit = 'person'
    _name = 'docktor'
    _description = 'Docktor'

    specialisation=fields.Selection(string='Спеціальність', selection=[
        ('травматолог', 'Травматолог'),
        ('стоматолог', 'Стоматолог'),
        ('кардіолог', 'Кардіолог'),
        ('невролог', 'Невролог'),
        ('ендокринолог', 'Ендокринолог'),
        ('гінеколог', 'Гінеколог'),
        ('уролог', 'Уролог'),
        ('дерматолог', 'Дерматолог'),
        ('онколог', 'Онколог'),
        ('пульмонолог', 'Пульмонолог'),
        ('офтальмолог', 'Офтальмолог'),
        ('оториноларинголог', 'Оториноларинголог'),
        ('ревматолог', 'Ревматолог'),
        ('алерголог', 'Алерголог'),
        ('інфекціоніст', 'Інфекціоніст'),
        ('анестезіолог', 'Анестезіолог'),
        ('хірург', 'Хірург'),
        ('проктолог', 'Проктолог'),
        ('педіатр', 'Педіатр'),
        ('гепатолог', 'Гепатолог'),
        ('гастроентеролог', 'Гастроентеролог'),
        ('неонатолог', 'Неонатолог'),
        ('геронтолог', 'Геронтолог'),
        ('нефролог', 'Нефролог'),
        ('мамолог', 'Мамолог'),
        ('флеболог', 'Флеболог'),
        ('фізіотерапевт', 'Фізіотерапевт'),
        ('сексопатолог', 'Сексопатолог'),
        ('психіатр', 'Психіатр'),
        ('психотерапевт', 'Психотерапевт'),
        ('дитячий хірург', 'Дитячий хірург'),
        ('нейрохірург', 'Нейрохірург'),
        ('імунолог', 'Імунолог'),
        ('логопед', 'Логопед'),
        ('ангіолог', 'Ангіолог'),
        ('епідеміолог', 'Епідеміолог'),
        ('фізіолог', 'Фізіолог'),
        ('судинний хірург', 'Судинний хірург'),
        ('стоматолог-ортодонт', 'Стоматолог-ортодонт'),
        ('стоматолог-хірург', 'Стоматолог-хірург'),
        ('паразитолог', 'Паразитолог'),
        ('санолог', 'Санолог'),
        ('віролог', 'Віролог'),
        ('гематолог', 'Гематолог'),
        ('токсиколог', 'Токсиколог'),
        ('педіатр-неонатолог', 'Педіатр-неонатолог'),
        ('патологоанатом', 'Патологоанатом'),
        ('пластичний хірург', 'Пластичний хірург'),
        ('ортопед', 'Ортопед'),
        ('військовий хірург', 'Військовий хірург'),
        ('стоматолог-ортопед', 'Стоматолог-ортопед'),
        ('акушер', 'Акушер'),
        ('вертебролог', 'Вертебролог'),
        ('фізіатр', 'Фізіатр'),
        ('косметолог', 'Косметолог'),
        ('сомнолог', 'Сомнолог'),
        ('дієтолог', 'Дієтолог'),
        ('педіатр-ендокринолог', 'Педіатр-ендокринолог'),
        ('педіатр-кардіолог', 'Педіатр-кардіолог'),
        ('клінічний фармаколог', 'Клінічний фармаколог'),
        ('андролог', 'Андролог'),
        ('лікар-лаборант', 'Лікар-лаборант'),
        ('лікар-лаборант-бактеріолог', 'Лікар-лаборант-бактеріолог'),
        ('лікар-лаборант-цитолог', 'Лікар-лаборант-цитолог')

    ])
    doctor_type=fields.Selection(string='Тип лікаря',selection=[
        ('лікар-ментор', 'Лікар-ментор'),
        ('інтерн', 'Інтерн')
    ])


class Diagnosis(models.Model):
    _name = 'diagnosis'
    _description = 'Diagnosis'

    doctor_ids = fields.Many2one('docktor', string='Лікар')
    patient_ids = fields.Many2one('patient', string='Пацієнт')
    diseases_name = fields.Many2one('directory.of.diseases', string='Назва хвороби' )
    injury_name = fields.Char(string='Назва травми')
    appointment_of_treatment = fields.Text(string='Призначення лікування')
    data_of_diseases = fields.Date(string='Дата встановлення діагнозу')
    @api.onchange('diseases')
    def _choose_diseases(self):
        if self.diseases:
            self.diseases_name=" "
        else:
            self.diseases_name=False

    @api.onchange('injury')
    def _choose_injury(self):
        if self.injury:
            self.injury_name=" "
        else:
            self.injury_name=False



class DirectoryOfDiseases(models.Model):
    _name = 'directory.of.diseases'
    _description = 'Directory of diseases'

    name = fields.Char(string='Назва хвороби', required=True)
    type_of_diseases = fields.Char(string='Тип хвороби', required=True)
    description = fields.Text(string='Опис хвороби', required=True)
    classification_name = fields.Many2one('classification',string='Класифікація', required=True)
    method_diagnosis_name = fields.Many2one('type.of.diagnosis',string='Метод діагностики', required=True)
    treatment = fields.Text(string='Лікування')

