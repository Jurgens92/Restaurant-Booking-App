from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('book/', views.make_booking, name='make_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('check-availability/', views.check_availability, name='check_availability'),
    
    # Restaurant owner admin views
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-tables/', views.table_management, name='table_management'),
    path('admin-tables/add/', views.edit_table, name='add_table'),
    path('admin-tables/edit/<int:table_id>/', views.edit_table, name='edit_table'),
    path('admin-confirm-booking/<int:booking_id>/', views.admin_confirm_booking, name='admin_confirm_booking'),
    path('admin-cancel-booking/<int:booking_id>/', views.admin_cancel_booking, name='admin_cancel_booking'),
]