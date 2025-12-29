# Django imports
from django import forms

# Local imports
from .models import Order, OrderItem, Product


# Constants
PAYMENT_METHOD_CHOICES = [
    ('COD', 'Cash on Delivery'),
    ('RAZORPAY', 'Online Payment')
]


# Forms
class OrderItemForm(forms.Form):
    """Form for order items."""
    
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1, initial=1)


class OrderForm(forms.ModelForm):
    """Form for order creation."""
    # Split customer_name into first_name and last_name for frontend
    first_name = forms.CharField(
        max_length=60,
        required=True,
        label='Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'form-input',
            'required': True
        })
    )
    last_name = forms.CharField(
        max_length=60,
        required=True,
        label='Surname',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'form-input',
            'required': True
        })
    )
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code',
            'latitude', 'longitude', 'notes'
        ]
        # Exclude customer_name from direct rendering, we'll handle it via first_name/last_name
        widgets = {
            'customer_name': forms.HiddenInput(),  # Hidden, will be set from first_name + last_name
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Enter your email', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your phone number', 'required': True}),
            'address_line1': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your address', 'required': True}),
            'address_line2': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apartment, suite, etc. (optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your city', 'required': True}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your state', 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your pincode', 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Any special instructions (optional)', 'rows': 3}),
        }

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        initial='RAZORPAY',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_reference = forms.CharField(required=False, max_length=120, widget=forms.TextInput(attrs={'class': 'form-input'}))

    def clean(self):
        cleaned = super().clean()
        
        # Combine first_name and last_name into customer_name
        first_name = cleaned.get('first_name', '').strip()
        last_name = cleaned.get('last_name', '').strip()
        
        # Combine names (both are required fields, so they should always be present)
        if first_name and last_name:
            cleaned['customer_name'] = f"{first_name} {last_name}".strip()
        elif first_name:
            cleaned['customer_name'] = first_name
        elif last_name:
            cleaned['customer_name'] = last_name
        else:
            # This shouldn't happen since fields are required, but set empty string as fallback
            cleaned['customer_name'] = ''
        
        # Payment reference is optional for COD orders
        return cleaned
    
    def save(self, commit=True):
        # Ensure customer_name is set before saving
        instance = super().save(commit=False)
        if not instance.customer_name:
            first_name = self.cleaned_data.get('first_name', '').strip()
            last_name = self.cleaned_data.get('last_name', '').strip()
            if first_name and last_name:
                instance.customer_name = f"{first_name} {last_name}".strip()
            elif first_name:
                instance.customer_name = first_name
            elif last_name:
                instance.customer_name = last_name
        
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields - all mandatory except address_line2 and notes
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['address_line1'].required = True
        self.fields['address_line2'].required = False  # Optional
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['postal_code'].required = True
        self.fields['notes'].required = False  # Optional
        
        # Hide lat/lng from UI
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['latitude'].widget = forms.HiddenInput()
        self.fields['longitude'].widget = forms.HiddenInput()
        
        # Hide customer_name from UI (we use first_name/last_name instead)
        self.fields['customer_name'].required = False
        self.fields['customer_name'].widget = forms.HiddenInput()
        
        # If editing existing order, split customer_name into first_name and last_name
        if self.instance and self.instance.pk and self.instance.customer_name:
            name_parts = self.instance.customer_name.split(' ', 1)
            if len(name_parts) >= 2:
                self.fields['first_name'].initial = name_parts[0]
                self.fields['last_name'].initial = name_parts[1]
            else:
                self.fields['first_name'].initial = self.instance.customer_name


