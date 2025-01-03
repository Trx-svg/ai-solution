from django import forms
from tinymce.widgets import TinyMCE

from .models import Service, Gallery, SiteLogo, Blog, TimeZone, EventHandler


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['icon', 'name', 'description']
        widgets = {
            'icon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['gallery_image', 'image_name', 'image_description']
        widgets = {
            'gallery_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image_name': forms.TextInput(attrs={'class': 'form-control'}),
            'image_description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SiteLogoForm(forms.ModelForm):
    class Meta:
        model = SiteLogo
        fields = ['site_logo', 'active']
        widgets = {
            'site_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['image', 'name', 'description', 'blog_content']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'blog_content': TinyMCE(attrs={'cols': 50, 'rows': 20}),
        }

class TimeZoneForm(forms.ModelForm):
    class Meta:
        model = TimeZone
        fields = ['timezone']
        widgets = {
            'timezone': forms.Select(attrs={'class': 'form-control'})
        }

class EventHandlerForm(forms.ModelForm):
    class Meta:
        model = EventHandler
        fields = ['name', 'description', 'date_time', 'timezone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
        }