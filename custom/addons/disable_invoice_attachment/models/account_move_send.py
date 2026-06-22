import logging
_logger = logging.getLogger(__name__)

def _get_default_pdf_report_id(self, move):
    report = self.env.ref(
        "custom_invoice_report.invoice_template",
        raise_if_not_found=False,
    )
    _logger.warning("REPORT FOUND = %s", report)
    return report
