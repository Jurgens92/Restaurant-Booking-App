from django.contrib import admin
from .models import Table, Booking, MenuItem

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'capacity', 'location')
    list_filter = ('capacity', 'location')
    search_fields = ('table_number',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'booking_date', 'booking_time', 'party_size', 'status', 'booking_actions')
    list_filter = ('booking_date', 'status', 'table')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'booking_date'
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def booking_actions(self, obj):
        if obj.status == 'PENDING':
            return format_html(
                '<a class="button" href="{}">Confirm</a> &nbsp; '
                '<a class="button" href="{}">Cancel</a>',
                f'/admin/confirm-booking/{obj.id}/',
                f'/admin/cancel-booking/{obj.id}/'
            )
        elif obj.status == 'CONFIRMED':
            return format_html('<a class="button" href="{}">Cancel</a>', f'/admin/cancel-booking/{obj.id}/')
        return "-"
    
    booking_actions.short_description = 'Actions'
    
    def confirm_bookings(self, request, queryset):
        queryset.update(status='CONFIRMED')
        self.message_user(request, f"{queryset.count()} bookings have been confirmed.")
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        queryset.update(status='CANCELLED')
        self.message_user(request, f"{queryset.count()} bookings have been cancelled.")
    cancel_bookings.short_description = "Cancel selected bookings"

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'vegetarian', 'vegan', 'gluten_free')
    list_filter = ('category', 'vegetarian', 'vegan', 'gluten_free')
    search_fields = ('name', 'description')

