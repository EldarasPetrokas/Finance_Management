from django.core.mail import send_mail
from django.db import models
import uuid
from datetime import date
from .utils import generate_pdf
import ssl


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Name', max_length=250)
    address = models.CharField('Address', max_length=100)
    phone_number = models.CharField('Phone Number', max_length=20)
    email = models.EmailField('Email', max_length=100)
    contact_person = models.CharField('Contact Person', max_length=100)
    account_number = models.CharField('Account Number', max_length=25)
    entry_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class Employer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    position = models.CharField('Position', max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.position}"


class InvoiceManager(models.Manager):
    def get_overdue_invoices(self):
        """Retrieve all overdue invoices."""
        return self.filter(
            status='overdue',
            payment_date__lt=date.today()
        )


class Invoice(models.Model):
    INVOICE_STATE = [
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateField('Payment Date', null=True, blank=True)
    sum = models.DecimalField('Sum', max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=INVOICE_STATE, default='issued')
    reminder_sent = models.BooleanField(default=False)
    pdf_file_path = models.CharField(max_length=255, blank=True, null=True)  # To store the path of the generated PDF

    def save(self, *args, **kwargs):
        print(f"Invoice {self.id} save() method called.")  # Debug log
        super().save(*args, **kwargs)  # Save the invoice instance first

        # Generate and save the PDF
        pdf_path = generate_pdf(self)
        print(f"PDF generated at: {pdf_path}")  # Debug log
        self.pdf_file_path = pdf_path
        super().save(*args, **kwargs)  # Save the instance again with the file path

    def __str__(self):
        return f"{self.client.name} - {self.sum}"

    def is_overdue(self):
        """
        Check if the invoice is overdue.
        """
        return self.status == 'overdue' and self.payment_date and self.payment_date < date.today()

    def send_reminder_email(self):
        try:
            if self.status != 'overdue':
                return False
            
            # Create email message
            subject = f"REMINDER: Invoice #{self.id} is overdue"
            message = f"""
            Dear {self.client.name},
            
            This is a reminder that invoice #{self.id} for the amount of €{self.sum} is overdue.
            The payment was expected by {self.payment_date}.
            
            Please make the payment as soon as possible.
            
            Thank you,
            Your Finance Team
            """
            
            recipient = self.client.email
            
            # Create an unverified SSL context to bypass certificate verification
            # Note: This is not recommended for production, but helps for development
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Pass the SSL context to the email function
            send_mail(
                subject,
                message,
                'your-email@example.com',  # Replace with your email
                [recipient],
                fail_silently=False,
                connection=get_connection(
                    use_ssl=True,
                    ssl_context=context
                )
            )
            
            # Record the reminder
            ReminderRecord.objects.create(
                invoice=self,
                recipient=recipient,
                content=message
            )
            
            # Update the reminder_sent flag
            self.reminder_sent = True
            self.save(update_fields=['reminder_sent'])
            
            return True
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send reminder for Invoice {self.id}: {str(e)}")
            raise

    def __str__(self):
        return f"{self.client.name} - {self.sum}"

    # Custom manager
    objects = models.Manager()


class ContactPerson(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=100)
    position = models.CharField('Position', max_length=100)
    phone_number = models.CharField('Phone Number', max_length=20)
    email = models.EmailField('Email', max_length=100)

    def __str__(self):
        return f"{self.name}, {self.position}"


class Reminder(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='reminders')
    recipient = models.EmailField('Recipient Email')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for Invoice {self.invoice.id} sent to {self.recipient} on {self.sent_at}"
