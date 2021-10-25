from invoice_generator.invoice_generator import InvoiceGenerator
from invoice_generator import models

from app import settings


async def generate_pdf_invoice(invoice, issuer, customer, invoice_name=None):
    issuer = models.Issuer(**issuer.dict())
    invoice_data = invoice.dict()
    invoice_data.pop('issuer')
    invoice_data.pop('customer')
    invoice_data = models.Invoice(**invoice_data,
                                  issuer=issuer,
                                  customer=customer)
    generator = InvoiceGenerator(invoice_data,
                                 invoice_name=invoice_name,
                                 output_directory=settings.LATEX_TEMP_DIR)
    generator.run()
    invoice.filename = generator.invoice_name
    await invoice.save()
