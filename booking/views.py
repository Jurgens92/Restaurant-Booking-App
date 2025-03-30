from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count
from .models import Booking, Table, MenuItem
from .forms import BookingForm
from .forms import RegisterForm
from .forms import TableForm
from datetime import datetime




def home(request):
    # Homepage view
    return render(request, 'booking/home.html')

def menu(request):
    # Display the restaurant menu
    starters = MenuItem.objects.filter(category='STARTER')
    mains = MenuItem.objects.filter(category='MAIN')
    desserts = MenuItem.objects.filter(category='DESSERT')
    drinks = MenuItem.objects.filter(category='DRINK')
    
    context = {
        'starters': starters,
        'mains': mains,
        'desserts': desserts,
        'drinks': drinks
    }
    return render(request, 'booking/menu.html', context)

@login_required
def make_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Create booking but don't save yet
            booking = form.save(commit=False)
            booking.user = request.user
            
            # Get form data for table search
            date = form.cleaned_data['booking_date']
            time = form.cleaned_data['booking_time']
            party_size = form.cleaned_data['party_size']
            
            # Get all tables with enough capacity
            suitable_tables = Table.objects.filter(capacity__gte=party_size)
            
            if not suitable_tables.exists():
                messages.error(request, f'Sorry, we don\'t have any tables that can accommodate {party_size} people.')
                return render(request, 'booking/make_booking.html', {'form': form})
            
            # Remove tables already booked at this time
            booked_tables = Booking.objects.filter(
                booking_date=date,
                booking_time=time,
                status__in=['PENDING', 'CONFIRMED']
            ).values_list('table', flat=True)
            
            available_tables = suitable_tables.exclude(id__in=booked_tables)
            
            if available_tables.exists():
                # Assign the booking to the first available table
                booking.table = available_tables.first()
                # Now save with the table assigned
                booking.save()
                messages.success(request, 'Your booking has been made!')
                return redirect('booking_success')
            else:
                messages.error(request, 'Sorry, no tables available at that time. Please try another time.')
    else:
        form = BookingForm()
    
    return render(request, 'booking/make_booking.html', {'form': form})
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            
            # Find available table with sufficient capacity
            date = form.cleaned_data['booking_date']
            time = form.cleaned_data['booking_time']
            party_size = form.cleaned_data['party_size']
            
            # Get all tables with enough capacity
            suitable_tables = Table.objects.filter(capacity__gte=party_size)
            
            # Remove tables already booked at this time
            booked_tables = Booking.objects.filter(
                booking_date=date,
                booking_time=time,
                status__in=['PENDING', 'CONFIRMED']
            ).values_list('table', flat=True)
            
            available_tables = suitable_tables.exclude(id__in=booked_tables)
            
            if available_tables.exists():
                # Assign the booking to the first available table
                booking.table = available_tables.first()
                booking.save()
                messages.success(request, 'Your booking has been made!')
                return redirect('booking_success')
            else:
                messages.error(request, 'Sorry, no tables available at that time. Please try another time.')
    else:
        form = BookingForm()
    
    return render(request, 'booking/make_booking.html', {'form': form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('booking_date', 'booking_time')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.save()
        messages.success(request, 'Your booking has been cancelled')
        return redirect('my_bookings')
    
    return render(request, 'booking/cancel_booking.html', {'booking': booking})

def booking_success(request):
    return render(request, 'booking/booking_success.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def check_availability(request):
    if request.method == 'GET':
        date = request.GET.get('date')
        party_size = request.GET.get('party_size')
        
        if date and party_size:
            # Convert party_size to integer
            try:
                party_size = int(party_size)
            except ValueError:
                return JsonResponse({'error': 'Invalid party size'}, status=400)
            
            # Get all tables with sufficient capacity
            suitable_tables = Table.objects.filter(capacity__gte=party_size)
            
            # Get all time slots (you could make this dynamic)
            time_slots = ['12:00', '12:30', '13:00', '13:30', '14:00', 
                         '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00']
            
            available_slots = []
            
            for time_slot in time_slots:
                # Convert time_slot string to time object
                from datetime import datetime
                time_obj = datetime.strptime(time_slot, '%H:%M').time()
                
                # Find bookings at this time slot
                booked_tables = Booking.objects.filter(
                    booking_date=date,
                    booking_time=time_obj,
                    status__in=['PENDING', 'CONFIRMED']
                ).values_list('table', flat=True)
                
                # Check if any suitable tables are available
                available_tables = suitable_tables.exclude(id__in=booked_tables)
                
                if available_tables.exists():
                    available_slots.append({
                        'time': time_slot,
                        'available': True,
                        'tables': available_tables.count()
                    })
                else:
                    available_slots.append({
                        'time': time_slot,
                        'available': False,
                        'tables': 0
                    })
            
            return JsonResponse({'available_slots': available_slots})
        
        return JsonResponse({'error': 'Missing date or party size'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


#admin functions

@staff_member_required
def admin_dashboard(request):
    """Dashboard view for restaurant management"""
    # Get today's date
    today = timezone.now().date()
    
    # Get today's bookings
    todays_bookings = Booking.objects.filter(booking_date=today)
    
    # Get upcoming bookings (next 7 days)
    upcoming_bookings = Booking.objects.filter(
        booking_date__gt=today,
        booking_date__lte=today + timezone.timedelta(days=7)
    )
    
    # Get tables usage statistics
    table_usage = Booking.objects.filter(
        status='CONFIRMED'
    ).values('table__table_number').annotate(
        booking_count=Count('id')
    ).order_by('-booking_count')
    
    # Get tables current status
    all_tables = Table.objects.all().order_by('table_number')
    tables_status = []
    
    for table in all_tables:
        current_booking = Booking.objects.filter(
            table=table,
            booking_date=today,
            status='CONFIRMED'
        ).first()
        
        tables_status.append({
            'table': table,
            'current_booking': current_booking,
        })
    
    context = {
        'todays_bookings': todays_bookings,
        'upcoming_bookings': upcoming_bookings,
        'table_usage': table_usage,
        'tables_status': tables_status,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def admin_confirm_booking(request, booking_id):
    """Confirm a booking (admin version)"""
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'CONFIRMED'
    booking.save()
    messages.success(request, f'Booking #{booking_id} has been confirmed.')
    return redirect('admin_dashboard')

@staff_member_required
def admin_cancel_booking(request, booking_id):
    """Cancel a booking (admin version)"""
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'CANCELLED'
    booking.save()
    messages.success(request, f'Booking #{booking_id} has been cancelled.')
    return redirect('admin_dashboard')

@staff_member_required
def table_management(request):
    """Table management view"""
    tables = Table.objects.all().order_by('table_number')
    return render(request, 'admin/table_management.html', {'tables': tables})

@staff_member_required
def edit_table(request, table_id=None):
    """Add or edit a table"""
    if table_id:
        table = get_object_or_404(Table, id=table_id)
    else:
        table = None
    
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, f'Table has been {"updated" if table else "created"}.')
            return redirect('table_management')
    else:
        form = TableForm(instance=table)
    
    return render(request, 'admin/edit_table.html', {'form': form, 'table': table})


