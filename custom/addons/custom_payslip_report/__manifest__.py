
{
    'name': 'Custom Payslip Report',
    'version': '19.0.1.0',
    'category': 'Payroll',
    'depends': ['hr_payroll'],
    'data': [
        'report/payslip_report.xml',
        'report/payslip_template.xml',
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
}
