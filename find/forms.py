from django import forms
#from .models import Customers

class FindCustomerForm(forms.Form):
    forename = forms.CharField(max_length=30, label='Forename')
    surname = forms.CharField(max_length=30, label='Surname')
    postcode = forms.CharField(max_length=8, label='Postcode')
    email = forms.EmailField(max_length=254, label='Email')
    phone = forms.CharField(max_length=15, label='Mobile or Landline', required=False)
    plan = forms.CharField(max_length=15, label='Plan Number', required=False)

    def clean(self):
        cleaned_data = super(FindCustomerForm, self).clean()
        forename = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        postcode = cleaned_data.get('postcode')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('Phone')
        plan = cleaned_data.get('plan')
        if not surname and not postcode:
            raise forms.ValidationError('You have to write something!')

#    class Meta:
#        model = Customers
#        managed = False
#        fields = ['forename', 'surname', 'postcode', 'contact_value']


class Register1(forms.Form):
    forename = forms.CharField(max_length=30, label='Forename')
    surname = forms.CharField(max_length=30, label='Surname')
    postcode = forms.CharField(max_length=8, label='Postcode')
    email = forms.EmailField(max_length=254, label='Email')

    def clean(self):
        cleaned_data = super(Register1, self).clean()
        forename = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        postcode = cleaned_data.get('postcode')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('Phone')
        plan = cleaned_data.get('plan')
        if not surname and not postcode:
            raise forms.ValidationError('You have to write something!')

class Register2(forms.Form):
    phone = forms.CharField(max_length=15, label='Mobile or Landline', required=False)
    plan = forms.CharField(max_length=15, label='Plan Number', required=False)

    def clean(self):
        cleaned_data = super(Register2, self).clean()
        forename = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        postcode = cleaned_data.get('postcode')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('Phone')
        plan = cleaned_data.get('plan')
        if not phone and not plan:
            raise forms.ValidationError('You have enter a value for Phone or Plan!')
