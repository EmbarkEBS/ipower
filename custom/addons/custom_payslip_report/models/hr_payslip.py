from odoo import models

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_print_custom_payslip(self):
        return self.env.ref(
            "custom_payslip_report.action_custom_payslip_report"
        ).report_action(self)

    def action_preview_custom_payslip(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_url",
            "url": "/report/html/custom_payslip_report.custom_payslip_template/%s" % self.id,
            "target": "new",
        }