from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Application, Vacancy

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    last_name = forms.CharField(max_length=100, required=True)
    first_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "last_name", "first_name", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]

class ProfileMainForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'last_name', 'first_name', 'middle_name',
            'birth_date', 'birth_place',
            'document_type', 'inn',
            'passport_series', 'passport_number',
            'passport_issue_date', 'passport_division_code',
            'passport_issued_by'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            # Устанавливаем начальные значения из модели User
            self.initial['last_name'] = self.instance.user.last_name
            self.initial['first_name'] = self.instance.user.first_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            # Сохраняем данные в модель User
            instance.user.last_name = self.cleaned_data['last_name']
            instance.user.first_name = self.cleaned_data['first_name']
            instance.user.save()
            instance.save()
        return instance

class ProfileContactForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class ProfileAdditionalForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['education', 'resume']
        widgets = {
            'education': forms.Textarea(attrs={'rows': 3}),
            'resume': forms.Textarea(attrs={'rows': 3}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['document']
        widgets = {
            'document': forms.FileInput(attrs={'accept': '.pdf'})
        }
        labels = {
            'document': 'Документ (в формате PDF)'
        }
        error_messages = {
            'document': {
                'required': 'Необходимо приложить PDF документ',
                'invalid': 'Загрузите корректный PDF файл'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].help_text = 'Загрузите документ в формате PDF (не более 10 МБ)'

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # Проверка размера файла (ограничение 10MB)
            if document.size > 10 * 1024 * 1024:  # 10MB в байтах
                raise forms.ValidationError('Размер файла превышает 10 МБ')
            
            # Проверка расширения файла
            if not document.name.endswith('.pdf'):
                raise forms.ValidationError('Документ должен быть в формате PDF')
            
            # Проверка MIME-типа
            if document.content_type != 'application/pdf':
                raise forms.ValidationError('Файл должен быть в формате PDF')
        return document

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'company', 'description', 'requirements', 'salary', 'location', 'contact_info']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'contact_info': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': 'Название вакансии',
            'company': 'Компания',
            'description': 'Описание',
            'requirements': 'Требования',
            'salary': 'Зарплата',
            'location': 'Местоположение',
            'contact_info': 'Контактная информация',
        }