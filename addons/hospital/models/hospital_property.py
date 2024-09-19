from odoo import fields, models, api
from datetime import datetime


class HospitalProperty(models.Model):
    _name = "hospital.property"
    _description = 'Hospital Property'


class Person(models.Model):
    _name = 'person'
    _description = 'Person'

    name = fields.Char(string='ПІБ', default='', required=True)
    mobile_phone=fields.Char(string='Номер телефону')
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
    id_card=fields.Char(string='Номер id картки')
    id_code=fields.Char(string='Ідентифікаційний код')
    issuing_body=fields.Char(string='Орган що видав')
    numb_pass=fields.Char(string='Номер паспорта')
    record_numb=fields.Char(string='Запис №')

    diagnosis_ids = fields.One2many('diagnosis', 'patient_ids')
    diagnosis_name = fields.Char(related='diagnosis_ids.diseases_name.name', string='Діагноз', store=True)
    diagnosis_doctor_name=fields.Char(related='diagnosis_ids.doctor_ids.name', string='Лікар', store=True)
    injure_name_id = fields.Char(related='diagnosis_ids.injury_name', string='Травма', store=True)
    intern_name_id = fields.Char(related='diagnosis_ids.intern_ids.name', store=True)
    comment_of_docktor_id = fields.Text(related='diagnosis_ids.comment_of_docktor', string='Коментар лікаря')

    contact_pers_id = fields.Many2one('contact.person', string='Контакстна особа')
    contact_name = fields.Char(related='contact_pers_id.name', string='ПІБ контактної особи', store=True)
    contact_mobile_phone = fields.Char(related='contact_pers_id.mobile_phone', string='Телефон контактної особи', store=True)
    contact_email = fields.Char(related='contact_pers_id.email', string='Електронна пошта контактної особи', store=True)
    contact_relationship = fields.Selection(related='contact_pers_id.relationship', string='Стосунки з пацієнтом',store=True)

    doctor_id = fields.Many2one('docktor', string='Персональний лікар')
    doctor_name = fields.Char(related='doctor_id.name', string='ПІБ лікаря', store=True)
    doctor_specialisation = fields.Selection(related='doctor_id.specialisation', string='Спеціальність лікаря', store=True)
    intern = fields.Boolean(string='Інтерн')

    intern_id = fields.Many2one('intern', string='Інтерн')
    intern_name = fields.Char(related='intern_id.name', string='ПІБ інтерна', store=True)

    exploration_ids=fields.One2many('exploration','patient_ids')

    @api.model
    def create(self, vals):

        patient = super(Patient, self).create(vals)

        if patient.doctor_id:
            self.env['docktor.history'].create({
                'patient_ids': patient.id,
                'docktor_ids': patient.doctor_id.id,
                'meeting': datetime.now(),
            })

        return patient

    @api.model
    def write(self, vals):
        new_doctor_id = vals.get('doctor_id')
        if new_doctor_id:
            for patient in self:
                existing_record = self.env['docktor.history'].search([
                    ('patient_ids', '=', patient.id),
                    ('docktor_ids', '=', new_doctor_id)
                ])

                if not existing_record:
                    self.env['docktor.history'].create({
                        'docktor_ids': new_doctor_id,
                        'patient_ids': patient.id,
                        'meeting': datetime.now(),
                    })

        return super(Patient, self).write(vals)

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


class DocktorHistory(models.Model):
    _name = 'docktor.history'
    _description = 'Docktor\'s history'

    docktor_ids=fields.Many2one('docktor', string='Лікар')
    patient_ids=fields.Many2one('patient',string='Пацієнт')
    meeting=fields.Date(string='Дата призначення')
    status_color = fields.Selection([
        ('green', 'Активний пацієнт'),
        ('red', 'Неактивний пацієнт')
    ], string="Статус", compute='_compute_status_color')

    @api.depends('docktor_ids', 'patient_ids.doctor_id')
    def _compute_status_color(self):
        for record in self:
            if record.patient_ids.doctor_id == record.docktor_ids:
                record.status_color = 'green'
            else:
                record.status_color = 'red'


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
    intern = fields.Boolean(string='Інтерн')
    intern_id = fields.Many2one('intern', string='Інтерн')
    intern_name = fields.Char(related='intern_id.name', string='ПІБ інтерна', store=True)
    intern_number = fields.Char(related='intern_id.mobile_phone', string='Номер телефону')
    patient = fields.Many2one('Patient', string='Пацієнт')
    docktor_history_ids=fields.One2many('docktor.history','docktor_ids',string=' ')


class Intern(models.Model):
    _inherit = 'person'
    _name = 'intern'
    _description = 'Intern'


class Diagnosis(models.Model):
    _name = 'diagnosis'
    _description = 'Diagnosis'

    doctor_ids = fields.Many2one('docktor', string='Лікар')
    intern_ids = fields.Many2one('intern',string='Інтерн')
    patient_ids = fields.Many2one('patient', string='Пацієнт', required=True)
    diseases_name = fields.Many2one('directory.of.diseases', string='Назва хвороби')
    name=fields.Char(related='diseases_name.name')
    intern = fields.Boolean(string='Інтерн')
    injury_name = fields.Char(string='Назва травми')
    appointment_of_treatment = fields.Text(string='Призначення лікування', required=True)
    comment_of_docktor=fields.Text(string='Коментар лікаря')
    data_of_diseases = fields.Date(string='Дата встановлення діагнозу')

    doctor_name = fields.Char(related='doctor_ids.name', string='ПІБ лікаря', store=True)
    doctor_specialisation = fields.Selection(related='doctor_ids.specialisation', string='Спеціальність лікаря', store=True)

    intern_name = fields.Char(related='intern_ids.name', string='ПІБ інтерна', store=True)


class DiseaseType(models.Model):
    _name = 'disease.type'
    _description = 'Disease Type'

    name = fields.Char(string='Тип хвороби', required=True)
    parent_id = fields.Many2one('disease.type', string='Батьківський тип')
    child_ids = fields.One2many('disease.type', 'parent_id', string='Підтипи')
    complete_name = fields.Char(compute='_compute_complete_name', string='Повна назва', store=True)

    @api.depends('name', 'parent_id')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = f"{record.parent_id.complete_name} / {record.name}"
            else:
                record.complete_name = record.name


class DirectoryOfDiseases(models.Model):
    _name = 'directory.of.diseases'
    _description = 'Directory of diseases'

    name = fields.Char(string='Назва хвороби', required=True)
    type_of_diseases = fields.Many2one('disease.type', string='Тип хвороби', required=True)
    complete_disease_type = fields.Char(related='type_of_diseases.complete_name', string='Повний тип хвороби',store=True)
    description = fields.Text(string='Опис хвороби', required=True)
    classification_name = fields.Many2one('classification', string='Класифікація', required=True)
    method_diagnosis_name = fields.Char(string='Метод діагностики', required=True)
    treatment = fields.Text(string='Лікування')


class DocktorVisit(models.Model):
    _name = 'docktor.visit'
    _description = "Docktor's visit"

    patient_ids = fields.Many2one('patient', string='Пацієнт')
    docktor_ids = fields.Many2one('docktor', string='Лікар')
    exploration_ids = fields.One2many('exploration', 'doctor_ids', string='Дослідження')
    diagnosis_ids = fields.Char(related='patient_ids.diagnosis_name', string='Діагноз')
    name = fields.Char(related='docktor_ids.name')
    time = fields.Datetime(string='Дата/Час')
    recommendation = fields.Text(string='Рекомендації')


class Exploration(models.Model):
    _name = 'exploration'
    _description = 'Exploration'
    _sql_constraints = [
        ('unique_number_exploration', 'unique(number_exploration)', 'The number must be unique!')
    ]

    name = fields.Char(string='Дослідження')
    number_exploration = fields.Char(string='Номер дослідження')
    patient_ids = fields.Many2one('patient', string='Пацієнт', required=True)
    doctor_ids = fields.Many2one('docktor.visit', string='Відвідування лікаря')
    patient_age = fields.Integer(related='patient_ids.age', string='Вік пацієнта')
    diagnosis_name = fields.Char(related='patient_ids.diagnosis_ids.diseases_name.name', string='Діагноз')
    doctor_name = fields.Char(related='patient_ids.doctor_name', string='Лікар')
    doctor_specialisation = fields.Selection(related='patient_ids.doctor_specialisation', string='Спеціальність лікаря')
    type_exploration = fields.Many2one('type.exploration', string='Тип дослідження')
    complete_exploration_type = fields.Char(related='type_exploration.complete_name', string='Повний тип дослідження', store=True)
    example = fields.Many2one('example.exploration', string='Зразок', store=True)
    conclusion = fields.Text(string='Висновок')

    @api.model
    def create(self, vals):
        exploration_record = super(Exploration, self).create(vals)

        # Знаходимо лікаря за doctor_name
        if exploration_record.patient_ids:
            doctor_name = exploration_record.patient_ids.doctor_name
            doctor_visit = self.env['docktor.visit'].search([
                ('docktor_ids.name', '=', doctor_name),
                ('patient_ids', '=', exploration_record.patient_ids.id)
            ], limit=1)
            if doctor_visit:
                doctor_visit.exploration_ids = [(4, exploration_record.id)]

        return exploration_record


class TypeExploration(models.Model):
    _name = 'type.exploration'
    _description = 'Type exploration'

    name=fields.Char(string='Тип дослідження', required=True)
    parent_id = fields.Many2one('type.exploration', string='Основний тип')
    child_ids = fields.One2many('type.exploration', 'parent_id', string='Підтипи')
    complete_name = fields.Char(compute='_compute_complete_name', string='Повна назва', store=True)

    @api.depends('name', 'parent_id')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = f"{record.parent_id.complete_name} / {record.name}"
            else:
                record.complete_name = record.name







