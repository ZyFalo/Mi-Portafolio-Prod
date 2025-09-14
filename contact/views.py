from django.shortcuts import render
from django.utils import timezone
from .forms import ContactForm
from .models import ContactMessage


def contactame(request):
    success = False
    form = ContactForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        website = form.cleaned_data.get('website') or ''
        ts = form.cleaned_data.get('ts') or ''
        is_bot = False
        # Honeypot: should be empty
        if website.strip():
            is_bot = True
        # Timestamp: should be at least ~2s old
        try:
            client_ms = int(ts)
            now_ms = int(timezone.now().timestamp() * 1000)
            if now_ms - client_ms < 1500:
                is_bot = True
        except Exception:
            # If missing/invalid, treat as bot-like but still allow submission
            pass

        if not is_bot:
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                consent=form.cleaned_data['consent'],
            )
            success = True
            form = ContactForm()  # reset form

    return render(request, 'contact/contactame.html', { 'form': form, 'success': success })


# Create your views here.
