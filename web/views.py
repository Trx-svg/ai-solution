from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import F

from dashboard.models import Inquery, Service, Gallery, Blog, EventHandler, SiteLogo
from web.utilis import chatbot, load_qa_data


def index_page(request):
    services = Service.objects.all()
    context = {
        'services': services
    }
    return render(request, 'pages/home.html', context)

def service_page(request):
    services = Service.objects.all()
    context = {
        'services': services
    }
    return  render(request, 'pages/service.html', context)

def gallery_page(request):
    gallery_images = Gallery.objects.all()
    context = {
        'gallery_images': gallery_images
    }
    return render(request, 'pages/gallery.html', context)

def about_page(request):
    return render(request, 'pages/about.html')

def contact_page(request):
    return render(request, 'pages/contact.html')

def blog_list(request):
    blog_lists = Blog.objects.all().order_by('-created_date')
    paginator = Paginator(blog_lists, 6)
    page = request.GET.get('page', 1)
    blogs = paginator.get_page(page)
    recent_blogs = Blog.objects.order_by('-created_date')[:3]
    return render(request, 'pages/blog.html', {'blogs': blogs, 'recent_blogs': recent_blogs})


def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    viewed_blogs = request.session.get('viewed_blogs', [])
    if blog_id not in viewed_blogs:
        Blog.objects.filter(id=blog_id).update(blog_view_count=F('blog_view_count') + 1)
        blog.refresh_from_db()
        viewed_blogs.append(blog_id)
        request.session['viewed_blogs'] = viewed_blogs
    recent_blogs = Blog.objects.exclude(id=blog_id).order_by('-created_date')[:3]

    return render(request, 'pages/blog_detail.html', {
        'blog': blog,
        'recent_blogs': recent_blogs
    })

def event_page(request):
    events = EventHandler.objects.all()
    return render(request, 'pages/event.html', {'events': events})

@require_http_methods(["POST"])
def create_appointment(request):
    try:
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'address': request.POST.get('address'),
            'phone_number': request.POST.get('phone_number'),
            'company_name': request.POST.get('company_name'),
            'country': request.POST.get('country'),
            'job_title': request.POST.get('job_title'),
            'job_description': request.POST.get('job_description')
        }
        appointment = Inquery(
            name=data['name'],
            email=data['email'],
            address=data['address'],
            phone_number=data['phone_number'],
            company_name=data['company_name'],
            country=data['country'],
            job_title=data['job_title'],
            job_description=data['job_description']
        )
        appointment.save()

        return HttpResponse(
            '<div class="alert alert-success">Appointment successfully created!</div>',
            status=200
        )
    except ValidationError:
        return HttpResponse(
            '<div class="alert alert-danger">Invalid data provided. Please check your inputs.</div>',
            status=400
        )


def get_logo_view(request):
    active_logo = SiteLogo.get_active_logo()

    if active_logo and active_logo.site_logo:
        html = f'''
            <div class="brand-container">
                <div class="nav-logo"><img src="{active_logo.site_logo.url}" class="navbar-image"></div>
                <div class="brand-name">AI-Solution</div>
            </div>
        '''
    else:
        html = '''
            <div class="brand-container">
                <div class="brand-name">AI-Solution</div>
            </div>
        '''

    return HttpResponse(html)


def process_message(request):
    if request.method == "POST":
        message = request.POST.get('message', '')
        try:
            response = chatbot.get_response(message)

            # Escape HTML special characters to prevent XSS
            message = message.replace('<', '&lt;').replace('>', '&gt;')
            response = response.replace('<', '&lt;').replace('>', '&gt;')
            return HttpResponse(f"""
                <div class="message user-message">
                    <div class="message-content">{message}</div>
                </div>
                <div class="message bot-message">
                    <div class="message-content">{response}</div>
                </div>
            """)
        except Exception as e:
            return HttpResponse(f"""
                <div class="message error-message">
                    <div class="message-content">Error processing message: {str(e)}</div>
                </div>
            """)


def initialize_chatbot(request):
    try:
        qa_data = load_qa_data('chat_data.txt')
        chatbot.load_knowledge(qa_data)
        return HttpResponse("Chatbot initialized successfully")
    except Exception as e:
        return HttpResponse(f"Error initializing chatbot: {str(e)}", status=500)