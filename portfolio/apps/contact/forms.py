from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label="Nombre", max_length=120, min_length=3)
    email = forms.EmailField(label="Email", max_length=200)
    subject = forms.CharField(label="Asunto", max_length=150, min_length=5)
    message = forms.CharField(label="Mensaje", widget=forms.Textarea, min_length=20)
    consent = forms.BooleanField(label="Acepto ser contactado", required=True)

    # Anti-bot
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
    ts = forms.CharField(required=False, widget=forms.HiddenInput)  # timestamp (ms)

