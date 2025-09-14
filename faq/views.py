from django.shortcuts import render
from .models import Question


def fyq(request):
    items = Question.objects.filter(is_active=True).order_by('order')
    return render(request, 'faq/fyq.html', { 'items': items })


# Create your views here.
