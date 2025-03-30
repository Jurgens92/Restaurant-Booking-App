from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'party_size', 'notes']
        widgets = {
            'booking_date': DateInput(),
            'booking_time': TimeInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        from datetime import datetime
        self.fields['booking_date'].widget.attrs['min'] = datetime.now().date()
        
    def clean_booking_date(self):
        date = self.cleaned_data.get('booking_date')
        from datetime import datetime
        today = datetime.now().date()
        if date < today:
            raise forms.ValidationError("You cannot book a date in the past")
        return date

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']