from django.http import HttpResponse

from dashboard.models import Inquery


def get_inquery_count(request):
    count = Inquery.objects.count()
    return HttpResponse(f'<span class="badge badge-success">{count}</span>')

def get_login_username(request):
    return HttpResponse(f'<span class="fw-bold">{request.user.username}</span>')