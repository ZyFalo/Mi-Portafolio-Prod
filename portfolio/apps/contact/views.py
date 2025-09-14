from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from urllib import request as urlrequest, parse as urlparse
import json
from .forms import ContactForm
from .models import ContactMessage


def _verify_recaptcha(token: str, remote_ip: str | None = None) -> tuple[bool, str]:
    if not getattr(settings, "RECAPTCHA_ENABLED", False):
        return True, ""
    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not secret:
        return False, "missing-secret"
    if not token:
        return False, "missing-input-response"
    data = {
        "secret": secret,
        "response": token,
    }
    if remote_ip:
        data["remoteip"] = remote_ip
    try:
        payload = urlparse.urlencode(data).encode()
        req = urlrequest.Request("https://www.google.com/recaptcha/api/siteverify", data=payload)
        with urlrequest.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("success"):
            return True, ""
        return False, ",".join(result.get("error-codes", []) or [])
    except Exception as e:
        return False, str(e)


def contactame(request):
    success = False
    form = ContactForm(data=request.POST or None)
    captcha_error = ""
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

        # Verify Google reCAPTCHA v2
        captcha_token = request.POST.get('g-recaptcha-response', '')
        captcha_ok, captcha_error = _verify_recaptcha(captcha_token, request.META.get('REMOTE_ADDR'))

        if not is_bot and captcha_ok:
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                consent=form.cleaned_data['consent'],
            )
            success = True
            form = ContactForm()  # reset form
        elif not captcha_ok:
            form.add_error(None, "Por favor completa el reCAPTCHA.")

    return render(request, 'contact/contactame.html', { 'form': form, 'success': success, 'captcha_error': captcha_error })


# Create your views here.
