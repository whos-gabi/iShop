# shop/forms.py

import re
import json
import time
from datetime import date
from django import forms
from django.conf import settings
from .models import Product

############################
# ContactForm
############################

def validate_text_field(value, required=True):
    if required and not value:
        raise forms.ValidationError("Acest câmp este obligatoriu.")

    if value:
        if not value[0].isupper():
            raise forms.ValidationError("Textul trebuie să înceapă cu literă mare.")
        # Verificăm doar litere și spații
        if not all(ch.isalpha() or ch.isspace() for ch in value):
            raise forms.ValidationError("Textul trebuie să conțină doar litere și spații.")
    return value

class ContactForm(forms.Form):
    TIP_MESAJ_CHOICES = [
        ('reclamatie', 'Reclamație'),
        ('intrebare', 'Întrebare'),
        ('review', 'Review'),
        ('cerere', 'Cerere'),
        ('programare', 'Programare'),
    ]

    nume = forms.CharField(
        max_length=10,
        required=True,
        label='Nume'
    )
    prenume = forms.CharField(
        max_length=50,
        required=False,
        label='Prenume'
    )
    data_nasterii = forms.DateField(
        required=False,
        label='Data nașterii',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    email = forms.EmailField(
        required=True,
        label='E-mail'
    )
    confirm_email = forms.EmailField(
        required=True,
        label='Confirmare E-mail'
    )
    tip_mesaj = forms.ChoiceField(
        choices=TIP_MESAJ_CHOICES,
        required=True,
        label='Tip mesaj'
    )
    subiect = forms.CharField(
        required=True,
        label='Subiect'
    )
    minim_zile_asteptare = forms.IntegerField(
        required=True,
        label='Minim zile așteptare',
        min_value=1
    )
    mesaj = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label='Mesaj (Semnați-vă la final cu numele)'
    )

    def clean_nume(self):
        nume = self.cleaned_data['nume']
        return validate_text_field(nume, required=True)

    def clean_prenume(self):
        prenume = self.cleaned_data['prenume']
        if prenume:
            return validate_text_field(prenume, required=False)
        return prenume

    def clean_subiect(self):
        subiect = self.cleaned_data['subiect']
        return validate_text_field(subiect, required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        data_nasterii = cleaned_data.get('data_nasterii')
        mesaj = cleaned_data.get('mesaj')
        nume = cleaned_data.get('nume')

        # Validare emailuri
        if email and confirm_email and email != confirm_email:
            self.add_error('confirm_email', 'Adresele de email nu coincid.')

        # Expeditor major
        if data_nasterii:
            today = date.today()
            age_years = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
            if age_years < 18:
                self.add_error('data_nasterii', 'Trebuie să fiți major pentru a trimite un mesaj.')

        # Mesaj 5-100 cuvinte
        if mesaj:
            # înlocuim linii noi cu spații și comasăm spațiile multiple
            msg_processed = re.sub(r'\s+', ' ', mesaj.strip())
            words = re.findall(r'\w+', msg_processed)
            if len(words) < 5 or len(words) > 100:
                self.add_error('mesaj', 'Mesajul trebuie să conțină între 5 și 100 de cuvinte.')

            # Nu poate conține linkuri
            for w in words:
                if w.startswith("http://") or w.startswith("https://"):
                    self.add_error('mesaj', 'Mesajul nu poate conține linkuri.')
                    break

            # Ultimul cuvânt trebuie să fie numele utilizatorului
            if words and words[-1].lower() != nume.lower():
                self.add_error('mesaj', 'Ultimul cuvânt din mesaj trebuie să fie numele dvs. (semnătura).')

        return cleaned_data

    def save_message(self):
        data = self.cleaned_data
        data_nasterii = data.get('data_nasterii')
        # Calc varsta în ani și luni
        if data_nasterii:
            today = date.today()
            age_years = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
            age_months = (today.month - data_nasterii.month) % 12
            age_str = f"{age_years} ani și {age_months} luni"
        else:
            age_str = "N/A"

        mesaj = data['mesaj']
        # curățare mesaj
        mesaj_processed = re.sub(r'\s+', ' ', mesaj.strip())

        final_data = {
            'nume': data['nume'],
            'prenume': data['prenume'],
            'varsta': age_str,
            'email': data['email'],
            'tip_mesaj': data['tip_mesaj'],
            'subiect': data['subiect'],
            'minim_zile_asteptare': data['minim_zile_asteptare'],
            'mesaj': mesaj_processed
        }

        timestamp = int(time.time())
        import os
        messages_dir = os.path.join(os.path.dirname(__file__), 'mesaje')
        if not os.path.exists(messages_dir):
            os.makedirs(messages_dir)
        filename = f"mesaj_{timestamp}.json"
        filepath = os.path.join(messages_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)


############################
# ProductFilterForm
############################

class ProductFilterForm(forms.Form):
    name = forms.CharField(max_length=100, required=False, label='Nume produs')
    price_min = forms.DecimalField(required=False, label='Preț minim', min_value=0)
    price_max = forms.DecimalField(required=False, label='Preț maxim', min_value=0)


############################
# ProductForm (ModelForm)
############################

class ProductForm(forms.ModelForm):
    # Câmpuri adiționale
    discount_percentage = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=100,
        label='Discount (%)'
    )
    extra_stock = forms.IntegerField(
        required=False,
        min_value=0,
        label='Stoc suplimentar',
        help_text='Introduceți stocul suplimentar față de cel implicit.'
    )

    class Meta:
        model = Product
        fields = ['name', 'price']  # Doar două coloane din model
        labels = {
            'name': 'Nume produs',
            'price': 'Preț',
        }
        help_texts = {
            'price': 'Introduceți prețul în USD',
        }
        error_messages = {
            'name': {
                'required': "Numele produsului este obligatoriu.",
            },
            'price': {
                'invalid': "Prețul trebuie să fie un număr valid.",
            }
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError("Numele trebuie să aibă cel puțin 3 caractere.")
        if not name[0].isupper():
            raise forms.ValidationError("Numele trebuie să înceapă cu majusculă.")
        if ' ' not in name:
            raise forms.ValidationError("Numele trebuie să conțină cel puțin un spațiu (ex: 'Mac Book').")
        return name

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 10:
            raise forms.ValidationError("Prețul trebuie să fie minim 10.")
        return price

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        data_nasterii = cleaned_data.get('data_nasterii')
        mesaj = cleaned_data.get('mesaj')
        nume = cleaned_data.get('nume')
    
        # Validare emailuri
        if email and confirm_email and email != confirm_email:
            self.add_error('confirm_email', 'Adresele de email nu coincid.')
    
        # Expeditor major
        if data_nasterii:
            today = date.today()
            age_years = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
            if age_years < 18:
                self.add_error('data_nasterii', 'Trebuie să fiți major pentru a trimite un mesaj.')
    
        if mesaj:
            msg_processed = re.sub(r'\s+', ' ', mesaj.strip())
            words = re.findall(r'\w+', msg_processed)
            if len(words) < 5 or len(words) > 100:
                self.add_error('mesaj', 'Mesajul trebuie să conțină între 5 și 100 de cuvinte.')
    
            for w in words:
                if w.startswith("http://") or w.startswith("https://"):
                    self.add_error('mesaj', 'Mesajul nu poate conține linkuri.')
                    break
                
            # Verificăm semnătura doar dacă nume există (a trecut validările)
            if nume and words and words[-1].lower() != nume.lower():
                self.add_error('mesaj', 'Ultimul cuvânt din mesaj trebuie să fie numele dvs. (semnătura).')
    
        return cleaned_data


    def save(self, commit=True):
        instance = super().save(commit=False)
        discount = self.cleaned_data.get('discount_percentage', 0)
        extra_stock = self.cleaned_data.get('extra_stock', 0)

        from .models import Category
        category, _ = Category.objects.get_or_create(name='Apple')
        instance.category = category

        # Ajustăm prețul cu discount
        if discount:
            instance.price = instance.price * (100 - discount) / 100

        # Adăugăm stoc suplimentar
        instance.stock = 10 + (extra_stock or 0)

        if commit:
            instance.save()
        return instance
