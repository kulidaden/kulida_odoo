{
    'name': "Hospital",
    'depends': ['base'],
    'version':'1.0',
    'category': 'Uncategorized',
    'application': True,
    'data':[
        'security/ir.model.access.csv',
        'wizard/assign_doctor_wizard.xml',
        'view/hospital_view.xml',
        'view/hospital_menu.xml'

    ],
}