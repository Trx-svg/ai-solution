from django.urls import path
from . import views
from .views import initialize_chatbot

urlpatterns = [
    path("", views.index_page, name="home"),
    path("service", views.service_page, name="service"),
    path("gallery", views.gallery_page, name="gallery"),
    path("about", views.about_page, name="about"),
    path('blog/', views.blog_list, name='blog'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path("events/", views.event_page, name='event'),
    path("contact", views.contact_page, name="contact"),
    path('create-appointment/', views.create_appointment, name='create_appointment'),
    path("get-logo", views.get_logo_view, name='get-logo'),
    path('process-message/', views.process_message, name='process_message'),
    path('initialize-chatbot/', initialize_chatbot, name='initialize_chatbot'),
]