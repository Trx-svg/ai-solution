from django.urls import path

from . import views
from .utils import get_inquery_count, get_login_username

urlpatterns = [
    path("", views.main_page, name="index"),
    path("login/", views.login_view, name="login"),
    path("password-change/", views.dashboard_password_change, name="password_change"),
    path('logout/', views.logout_view, name='logout'),
    path('management/event/', views.dashboard_events, name='dashboard-events'),
    path('management/event-form', views.event_form, name='admin_event_form'),
    path('management/event/delete/<int:event_id>', views.delete_event, name='delete_event'),
    path('management/gallery/', views.dashboard_gallery, name='dashboard-gallery'),
    path('management/gallery-form', views.gallery_form, name='admin_gallery_form'),
    path('management/gallery/delete/<int:gallery_id>', views.delete_gallery, name='delete_gallery'),
    path('management/blog/', views.dashboard_blog, name='dashboard-blog'),
    path('management/blog/form/', views.blog_form, name='admin_blog_form'),
    path('management/blog/delete/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('management/service/', views.dashboard_service, name='dashboard-service'),
    path('management/service-form/', views.service_form, name='admin_service_form'),
    path('management/service/delete/<int:service_id>', views.delete_service, name='delete_service'),
    path('message/inquery/', views.inquery, name='inquery'),
    path('site/logo/', views.dashboard_logo, name='logo'),
    path('site/logo-form/', views.site_logo_form, name='admin_site_logo_form'),
    path('site/logo/delete/<int:logo_id>', views.delete_site_logo, name='delete_site_logo'),
    path('site/timezone-settings/', views.timezone_settings, name='timezone-settings'),
    path('setting/account/', views.account_view, name='account'),
    path('setting/admin-user-form/', views.admin_user_form, name='admin_user_form'),
    path('setting/create-admin-user/', views.create_admin_user, name='create_admin_user'),
    path('setting/delete-admin-user/<int:user_id>/', views.delete_admin_user, name='delete_admin_user'),
    path('get-inquery-count/', get_inquery_count, name='get_inquery_count'),
    path('get-username/', get_login_username, name='get_login_username')
]