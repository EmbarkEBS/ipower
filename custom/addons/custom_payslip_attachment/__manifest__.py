{
    'name': 'Custom Payslip Attachment',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Use custom payslip report for standard payslip printing',
    'depends': [
        'hr_payroll',
        'your_custom_payslip_module',
    ],
    'data': [
        'data/payslip_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}