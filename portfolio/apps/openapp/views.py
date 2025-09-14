from django.shortcuts import render, get_object_or_404
from .models import OpenEntity, Tag


def open_list(request):
    items = OpenEntity.objects.filter(is_published=True).select_related().prefetch_related('keywords')
    tags = Tag.objects.all()
    return render(request, 'openapp/open_list.html', { 'items': items, 'tags': tags })


def open_detail(request, slug: str):
    item = get_object_or_404(OpenEntity.objects.select_related().prefetch_related('keywords'), slug=slug, is_published=True)
    return render(request, 'openapp/open_detail.html', { 'item': item })


# Create your views here.
