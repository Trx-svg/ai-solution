import os
from time import sleep
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.utils.timezone import localtime

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from dashboard.form import ServiceForm, GalleryForm, SiteLogoForm, BlogForm, TimeZoneForm, EventHandlerForm
from dashboard.models import AdminUser, Service, Gallery, SiteLogo, Inquery, Blog, TimeZone, EventHandler
from django.contrib import messages
import logging

@login_required
def main_page(request):
    # Event
    total_events = EventHandler.objects.count()
    completed_events = EventHandler.objects.filter(held_status=True).count()
    completion_percentage = (completed_events / total_events * 100) if total_events > 0 else 0
    # Admin User
    total_users = AdminUser.objects.count()
    week_ago = timezone.now() - timedelta(days=7)
    new_weekly_users = AdminUser.objects.filter(created_at__gte=week_ago).count()
    weekly_percentage = (new_weekly_users / total_users * 100) if total_users > 0 else 0
    # Inquiries
    total_inquiries = Inquery.objects.count()
    last_days = timezone.now() - timedelta(days=2)
    previous_days = last_days - timedelta(days=2)
    current_inquiries = Inquery.objects.filter(created_date__gte=last_days).count()
    previous_inquiries = Inquery.objects.filter(
        created_date__gte=previous_days,
        created_date__lt=last_days
    ).count()
    print(previous_inquiries)
    increase_rate = (
        ((current_inquiries - previous_inquiries) / previous_inquiries * 100)
        if previous_inquiries > 0
        else 0
    )
    # Blogs
    total_blogs = Blog.objects.count()
    total_views = Blog.objects.aggregate(total_views=Sum('blog_view_count'))['total_views'] or 0
    avg_views_per_blog = (total_views / total_blogs) if total_blogs > 0 else 0
    blogs_above_average = Blog.objects.filter(
        blog_view_count__gt=avg_views_per_blog
    ).count()
    view_rate = (blogs_above_average / total_blogs * 100) if total_blogs > 0 else 0
    # Get the 6 most recent inquiries
    recent_inquiries = Inquery.objects.all()[:6]
    inquiries_data = [{
        'name': inquiry.name,
        'date': localtime(inquiry.created_date),
        'color_class': f'feed-item-{color}'
    } for inquiry, color in zip(
        recent_inquiries,
        ['secondary', 'success', 'info', 'warning', 'danger', '']
    )]
    context = {
        'total_events': total_events,
        'completed_events': completed_events,
        'completion_percentage': round(completion_percentage, 1),
        'total_users': total_users,
        'new_weekly_users': new_weekly_users,
        'weekly_percentage': round(weekly_percentage, 1),
        'total_inquiries': total_inquiries,
        'current_month_inquiries': current_inquiries,
        'increase_rate': round(increase_rate, 1),
        'total_blogs': total_blogs,
        'total_views': total_views,
        'view_rate': round(view_rate, 1),
        'recent_inquiries': inquiries_data
    }

    return render(request, 'pages/main.html', context)


@login_required
def dashboard_password_change(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user

        if not user.check_password(current_password):
            return HttpResponse("""
                <div class="error">Current password is incorrect</div>
            """.strip(), headers={'HX-Trigger': 'passwordError'})

        if new_password != confirm_password:
            return HttpResponse("""
                <div class="error">New passwords don't match</div>
            """.strip(), headers={'HX-Trigger': 'passwordError'})

        if len(new_password) < 3:
            return HttpResponse("""
                <div class="error">Password must be at least 3 characters</div>
            """.strip(), headers={'HX-Trigger': 'passwordError'})

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)

        return HttpResponse("""
            <div class="success">Password updated successfully</div>
        """.strip(), headers={'HX-Trigger': 'passwordSuccess'})


    return render(request, 'pages/password_change.html')

@login_required
def account_view(request):
    users = AdminUser.objects.all().order_by('-created_at')
    return render(request, 'pages/account.html', {'users': users})

@login_required
@require_http_methods(["GET"])
def admin_user_form(request):
    return render(request, 'components/user_form_modal.html')

@login_required
@require_http_methods(["POST"])
def create_admin_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    password_confirmation = request.POST.get('password_confirmation')

    if password != password_confirmation:
        return HttpResponse("""
            <div class="alert alert-danger">
                Passwords do not match!
            </div>
        """)

    try:
        # Create your user here using your AdminUser model
        AdminUser.objects.create_user(username=username, password=password)
        return HttpResponse("""
            <div class="alert alert-success">
                User created successfully!
                <script>
                    setTimeout(function() {
                        document.querySelector('#userModal').modal('hide');
                        location.reload();
                    }, 1500);
                </script>
            </div>
        """)
    except Exception as e:
        return HttpResponse(f"""
            <div class="alert alert-danger">
                Error creating user: {str(e)}
            </div>
        """)

@login_required
@require_http_methods(["DELETE"])
def delete_admin_user(request, user_id):
    try:
        user = AdminUser.objects.get(id=user_id)
        user.delete()
        users = AdminUser.objects.all().order_by('-created_at')
        return render(request, 'components/users_table.html', {'users': users})
    except AdminUser.DoesNotExist:
        return HttpResponse("User not found", status=404)


logger = logging.getLogger(__name__)


@csrf_protect
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Add slight delay to prevent brute force attempts
        sleep(0.5)

        if not (username and password):
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'pages/login.html')
        print(username, password)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Safely handle the redirect
                next_url = request.GET.get('next', '')
                if not next_url or not url_has_allowed_host_and_scheme(
                        url=next_url,
                        allowed_hosts={request.get_host()},
                        require_https=request.is_secure()
                ):
                    next_url = reverse('index')

                logger.info(f"Successful login for user: {username}")
                return redirect(next_url)
            else:
                logger.warning(f"Login attempt for inactive user: {username}")
                messages.error(request, 'This account is inactive.')
        else:
            # Use consistent error message to prevent username enumeration
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, 'Invalid login credentials. Please try again.')

    return render(request, 'pages/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def dashboard_service(request):
    services = Service.objects.all().order_by('-created_date')
    return render(request, 'pages/dashboard_service.html', {'services': services})

@login_required
def service_form(request):
    service_id = request.GET.get('id') or request.POST.get('service_id')
    service = None
    if service_id:
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            pass

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)

        if form.is_valid():
            service_instance = form.save(commit=False)
            if not service_instance.id:
                service_instance.created_by = request.user

            if request.POST.get('delete_icon') and service_instance.icon:
                service_instance.icon.delete()
                service_instance.icon = None

            if not request.FILES.get('icon') and service and service.icon:
                service_instance.icon = service.icon

            service_instance.save()
            services = Service.objects.all().order_by('-created_date')
            return render(request, 'components/service_table.html', {'services': services})
    else:
        if service:
            form = ServiceForm(instance=service)
        else:
            form = ServiceForm()

    return render(request, 'components/service_form.html', {'form': form})

@login_required
@require_http_methods(["DELETE"])
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    try:
        service.delete()
        messages.success(request, f"Service '{service.name}' was successfully deleted.")
        services = Service.objects.all()
        return render(request, 'components/service_table.html', {'services': services})
    except Exception as e:
        messages.error(request, f"Error deleting service: {str(e)}")
        return HttpResponse(status=400)

@login_required
def dashboard_gallery(request):
    galleries = Gallery.objects.all().order_by('-created_date')
    return render(request, 'pages/dashboard_gallery.html', {'galleries': galleries})

@login_required
def gallery_form(request):
    gallery_id = request.GET.get('id') or request.POST.get('gallery_id')
    gallery = None
    if gallery_id:
        try:
            gallery = Gallery.objects.get(id=gallery_id)
        except Gallery.DoesNotExist:
            pass

    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=gallery)

        if form.is_valid():
            gallery_instance = form.save(commit=False)
            if not gallery_instance.id:
                gallery_instance.created_by = request.user

            if request.POST.get('delete_image') and gallery_instance.gallery_image:
                gallery_instance.gallery_image.delete()
                gallery_instance.gallery_image = None

            if not request.FILES.get('gallery_image') and gallery and gallery.gallery_image:
                gallery_instance.gallery_image = gallery.gallery_image

            gallery_instance.save()
            galleries = Gallery.objects.all().order_by('-created_date')
            return render(request, 'components/gallery_table.html', {'galleries': galleries})
    else:
        if gallery:
            form = GalleryForm(instance=gallery)
        else:
            form = GalleryForm()

    return render(request, 'components/gallery_form.html', {'form': form})

@login_required
@require_http_methods(["DELETE"])
def delete_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    try:
        gallery.delete()
        messages.success(request, f"Gallery image '{gallery.image_name}' was successfully deleted.")
        galleries = Gallery.objects.all()
        return render(request, 'components/gallery_table.html', {'galleries': galleries})
    except Exception as e:
        messages.error(request, f"Error deleting gallery image: {str(e)}")
        return HttpResponse(status=400)

@login_required
def dashboard_logo(request):
    logos = SiteLogo.objects.all().order_by('-created_date')
    return render(request, 'pages/logo.html', {'logos': logos})


@login_required
def site_logo_form(request):
    logo_id = request.GET.get('id') or request.POST.get('logo_id')
    logo = None
    if logo_id:
        try:
            logo = SiteLogo.objects.get(id=logo_id)
        except SiteLogo.DoesNotExist:
            pass

    if request.method == 'POST':
        form = SiteLogoForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            logo_instance = form.save(commit=False)
            if not logo_instance.id:
                logo_instance.created_by = request.user

            if logo_instance.active:
                SiteLogo.objects.exclude(id=logo_instance.id).update(active=False)

            if not request.FILES.get('site_logo') and logo and logo.site_logo:
                logo_instance.site_logo = logo.site_logo

            logo_instance.save()
            logos = SiteLogo.objects.all().order_by('-created_date')
            return render(request, 'components/logo_table.html', {'logos': logos})
    else:
        if logo:
            form = SiteLogoForm(instance=logo)
        else:
            form = SiteLogoForm()

    return render(request, 'components/logo_form.html', {'form': form})

@login_required
@require_http_methods(["DELETE"])
def delete_site_logo(request, logo_id):
    logo = get_object_or_404(SiteLogo, id=logo_id)
    try:
        logo.delete()
        messages.success(request, "Site logo was successfully deleted.")
        logos = SiteLogo.objects.all()
        return render(request, 'components/logo_table.html', {'logos': logos})
    except Exception as e:
        messages.error(request, f"Error deleting site logo: {str(e)}")
        return HttpResponse(status=400)

def inquery(request):
    web_messages = Inquery.objects.all().order_by('-created_date')
    return render(request, "pages/inquery.html", {"web_messages": web_messages})

def dashboard_blog(request):
    blogs = Blog.objects.all().order_by('-created_date')
    return render(request, "pages/dashboard_blog.html", {"blogs": blogs})


@login_required
def blog_form(request):
    blog_id = request.GET.get('id') or request.POST.get('blog_id')
    blog = None
    if blog_id:
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)

        if form.is_valid():
            blog_instance = form.save(commit=False)
            if not blog_instance.id:
                blog_instance.created_by = request.user

            if request.POST.get('delete_image') and blog_instance.image:
                blog_instance.image.delete()
                blog_instance.image = None

            if not request.FILES.get('image') and blog and blog.image:
                blog_instance.image = blog.image

            blog_instance.save()
            blogs = Blog.objects.all().order_by('-created_date')
            return render(request, 'components/blog_table.html', {'blogs': blogs})
    else:
        if blog:
            form = BlogForm(instance=blog)
        else:
            form = BlogForm()

    return render(request, 'components/blog_form.html', {'form': form})

@login_required
@require_http_methods(["DELETE"])
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    try:
        blog.delete()
        messages.success(request, f"Blog '{blog.name}' was successfully deleted.")
        blogs = Blog.objects.all()
        return render(request, 'components/blog_table.html', {'blogs': blogs})
    except Exception as e:
        messages.error(request, f"Error deleting blog: {str(e)}")
        return HttpResponse(status=400)


@login_required
def timezone_settings(request):
    timezone_instance = TimeZone.objects.first()

    if request.method == 'POST':
        form = TimeZoneForm(request.POST, instance=timezone_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Timezone updated successfully")
            return redirect('timezone-settings')
    else:
        form = TimeZoneForm(instance=timezone_instance)

    return render(request, 'pages/timezone_settings.html', {'form': form})

@login_required
def dashboard_events(request):
    events = EventHandler.objects.all().order_by('-created_date')
    return render(request, 'pages/dashboard_event.html', {'events': events})

@login_required
def event_form(request):
    event_id = request.GET.get('id') or request.POST.get('event_id')
    event = None
    if event_id:
        event = get_object_or_404(EventHandler, id=event_id)

    if request.method == 'POST':
        form = EventHandlerForm(request.POST, instance=event)
        if form.is_valid():
            event_instance = form.save(commit=False)
            if not event_instance.id:
                event_instance.created_by = request.user
            event_instance.save()
            events = EventHandler.objects.all().order_by('-created_date')
            return render(request, 'components/event_table.html', {'events': events})
    else:
        form = EventHandlerForm(instance=event)

    return render(request, 'components/event_form.html', {'form': form})

@login_required
@require_http_methods(["DELETE"])
def delete_event(request, event_id):
    event = get_object_or_404(EventHandler, id=event_id)
    try:
        event.delete()
        messages.success(request, f"Event '{event.name}' was successfully deleted.")
        events = EventHandler.objects.all()
        return render(request, 'components/event_table.html', {'events': events})
    except Exception as e:
        messages.error(request, f"Error deleting event: {str(e)}")
        return HttpResponse(status=400)