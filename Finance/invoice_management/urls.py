from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<uuid:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/mark_as_paid/', views.mark_as_paid, name='mark_as_paid'),
    path('send_reminder/<uuid:invoice_id>/', views.send_reminder, name='send_reminder'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('clients/', views.client_list, name='client_list'),
    path('add_client/', views.add_client, name='add_client'),
    path('add_invoice/', views.add_invoice, name='add_invoice'),
    path('clients/<int:client_id>/add_contact_person/', views.add_contact_person, name='add_contact_person'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    path('download_invoice/<uuid:invoice_id>/', views.download_invoice, name='download_invoice'),
]
