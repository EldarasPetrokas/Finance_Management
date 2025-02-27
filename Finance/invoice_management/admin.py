from django.contrib import admin
from .models import Client, Employer, Invoice, ContactPerson


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'email', 'account_number')


class EmployerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'position')


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'entry_date', 'payment_date', 'sum', 'status')
    exclude = ('pdf_file_path',)


class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'name', 'position', 'phone_number', 'email')


admin.site.register(Client, ClientAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(ContactPerson, ContactPersonAdmin)

