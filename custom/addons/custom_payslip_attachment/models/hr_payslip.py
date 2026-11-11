from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        result = super().action_payslip_done()

        report = self.env.ref(
            'custom_payslip_attachment.action_custom_payslip',
            raise_if_not_found=False
        )

        if not report:
            return result

        for slip in self.filtered(lambda s: s.state == 'done'):

            # Remove previously generated custom PDF
            self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'hr.payslip'),
                ('res_id', '=', slip.id),
                ('name', '=', 'Custom-Payslip-%s.pdf' % slip.id),
            ]).unlink()

            # Generate custom PDF
            pdf_content, output_type = report.sudo()._render_qweb_pdf(
                report,
                res_ids=[slip.id],
            )

            if output_type != 'pdf':
                continue

            # Attach generated PDF to payslip
            self.env['ir.attachment'].sudo().create({
                'name': 'Custom-Payslip-%s.pdf' % slip.id,
                'type': 'binary',
                'datas': __import__('base64').b64encode(pdf_content),
                'res_model': 'hr.payslip',
                'res_id': slip.id,
                'mimetype': 'application/pdf',
            })

        return result
