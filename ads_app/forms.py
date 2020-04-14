from django import forms  
from ads_app.models import Comment, Category, Advert
from django.forms.widgets import ClearableFileInput
from django.contrib.auth.models import User

class MyClearableFileInput(ClearableFileInput):
    initial_text = 'Текущяя'
    input_text = 'Изменить'
    clear_checkbox_label = 'Удалить'

class CommentForm(forms.ModelForm):

    author = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'required': True,
                'type': 'text',
                'class':'input-comment',
                'placeholder': 'Введите ваше имя'
            }
        )
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'required': True,
                'type': 'text',
                'class': 'textarea-comment',
                'placeholder': 'Введите ваш комментарий'
            }
        )
    )
    class Meta:
        model = Comment
        fields = ('author', 'content')

class AdvertForm(forms.ModelForm):

    title = forms.CharField(
        label='Название объявления',
        required=True,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Введите название объявления'
            }
        )
    )
    content = forms.CharField(
        label='Содержание объявления',
        required=True,
        widget=forms.Textarea(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Введите содержание объявления'
            }
        )
    )
    tags = forms.CharField(
        label='Теги',
        required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Введите теги через пробел'
            }
        )
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label='Категория',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    photo = forms.ImageField(
        label= 'Фото',
        required=False,
        widget= MyClearableFileInput(
            attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.gif'
            }
        )
    )
    class Meta:
        model = Advert
        fields = ('title', 'content', 'tags', 'category', 'photo')
