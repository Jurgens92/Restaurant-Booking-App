from django.contrib import admin
from .models import Table, Booking, MenuItem

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'capacity', 'location')
    list_filter = ('capacity', 'location')
    search_fields = ('table_number',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'booking_date', 'booking_time', 'party_size', 'status')
    list_filter = ('booking_date', 'status', 'table')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'booking_date'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'vegetarian', 'vegan', 'gluten_free')
    list_filter = ('category', 'vegetarian', 'vegan', 'gluten_free')
    search_fields = ('name', 'description')