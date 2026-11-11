{
    'name': 'Custom Payslip Attachment',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Automatically attach custom payslip PDF on validation',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'report/custom_payslip_template.xml',
        'data/replace_payslip_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
