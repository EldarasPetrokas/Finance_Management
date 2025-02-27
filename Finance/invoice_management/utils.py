from django.template.loader import render_to_string
from xhtml2pdf import pisa
import os
from django.conf import settings


def generate_pdf(invoice):
    try:
        # Use absolute path for the invoices folder
        client_name = invoice.client.name.replace(' ', '_')
        invoices_folder = os.path.join(settings.BASE_DIR, 'invoices')
        folder_path = os.path.join(invoices_folder, client_name)
        os.makedirs(folder_path, exist_ok=True)

        pdf_file_path = os.path.join(folder_path, f"invoice_{invoice.id}.pdf")
        print(f"Absolute PDF file path: {pdf_file_path}")

        # Render and generate the PDF
        template_path = 'invoice_pdf_template.html'
        context = {'invoice': invoice}
        html = render_to_string(template_path, context)

        with open(pdf_file_path, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(html, dest=pdf_file)
            if pisa_status.err:
                print("Failed to generate PDF")
                return None

        return pdf_file_path
    except Exception as e:
        print(f"Error in generate_pdf: {e}")
        return None
