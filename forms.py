from django.forms import ModelForm
from .models import Offer, Rank
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div
from crispy_forms.bootstrap import FormActions, InlineField, PrependedText
from registration.forms import RegistrationFormUniqueEmail


class OfferForm(ModelForm):
    target_date = forms.DateTimeField(initial=timezone.now, label='Data', input_formats=['%d/%m/%Y %H:%M:%S',
                                                                                         '%d/%m/%Y %H:%M',])

    class Meta:
        model = Offer
        exclude = ['chosen_worker', 'author']
        labels = {
            'place': 'Adres',
            'phone_number': 'Numer telefonu',
            'full_cleaning': 'Pełne mycie',
            'car_cleaning': 'Mycie samochodu',
            'window_cleaning': 'Mycie okien',
            'living_room': 'Salon',
            'kitchen': 'Kuchnia',
            'bedroom': 'Sypialnia',
            'bathroom': 'Łazienka',
            'price': 'Cena'
        }

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
        Field('place'),
        Field('target_date'),
        Field('phone_number', placeholder='+999999999'),
        PrependedText('email', '@'),
        Div(
            InlineField('full_cleaning'),
            InlineField('car_cleaning'),
            InlineField('window_cleaning'),
            css_class='form-inline'
        ),
        Div(
            InlineField('living_room'),
            InlineField('kitchen'),
            InlineField('bedroom'),
            InlineField('bathroom'),
            css_class='form-inline'
        ),
        PrependedText('price', '$'),
        FormActions(
            Submit('save', 'Zapisz', css_class='btn-primary')
            )
        )


class RankForm(ModelForm):
    class Meta:
        model = Rank
        exclude = ['user']


class FilterForm(forms.Form):
    full_cleaning = forms.BooleanField(required=False, label='Pełne mycie')
    car_cleaning = forms.BooleanField(required=False, label='Mycie samochodu')
    window_cleaning = forms.BooleanField(required=False, label='Mycie okien')
    living_room = forms.BooleanField(required=False, label='Salon')
    kitchen = forms.BooleanField(required=False, label='Kuchnia')
    bedroom = forms.BooleanField(required=False, label='Sypialnia')
    bathroom = forms.BooleanField(required=False, label='Łazienka')
    price__gte = forms.FloatField(required=False, widget=forms.TextInput(attrs={'placeholder': 'cena od'}))
    price__lte = forms.FloatField(required=False, widget=forms.TextInput(attrs={'placeholder': 'cena do'}))

    helper = FormHelper()
    helper.form_method = 'GET'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-xs-1'
    helper.field_class = 'col-xs-2'
    helper.form_show_labels = False
    helper.layout = Layout(
        Div(
            InlineField('full_cleaning'),
            InlineField('car_cleaning'),
            InlineField('window_cleaning'),
            css_class='form-inline', css_id='chbox'
        ),
        Div(
            InlineField('living_room'),
            InlineField('kitchen'),
            InlineField('bedroom'),
            InlineField('bathroom'),
            css_class='form-inline', css_id='chbox'
        ),
        Field('price__gte'),
        Field('price__lte'),
        FormActions(
            Submit('submit', 'Submit', css_class='btn-primary')
        )
    )


class CustomRegistration(RegistrationFormUniqueEmail):
    password1 = forms.CharField(label='Hasło', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Potwierdź Hasło', widget=forms.PasswordInput, help_text='Wprowadź ponownie', required=True)
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nazwa użytkownika'
        }
        help_texts = {
            'username': 'Maksymalnie 150 znaków, tylko cyfry, litery i @/./+/-/_'
        }

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.field_class = 'col-lg-2'
    helper.label_class = 'col-lg-1'
    helper.add_input(Submit('register', 'Rejestracja'))
