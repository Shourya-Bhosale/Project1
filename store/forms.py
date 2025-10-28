from django import forms
from .models import Order, OrderItem, Product


class OrderItemForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1, initial=1)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_name', 'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code',
            'latitude', 'longitude', 'notes'
        ]

    payment_method = forms.ChoiceField(choices=[('COD','Cash on Delivery'),('RAZORPAY','Online Payment')], initial='COD')
    payment_reference = forms.CharField(required=False, max_length=120)

    def clean(self):
        cleaned = super().clean()
        # Payment reference is optional for COD orders
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make address fields required
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['postal_code'].required = True
        # Hide lat/lng from UI
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['latitude'].widget = forms.HiddenInput()
        self.fields['longitude'].widget = forms.HiddenInput()


