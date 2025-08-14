from django.shortcuts import render, redirect, get_object_or_404
from .models import URL
import qrcode
from io import BytesIO
import base64

def home(request):
    short_url = None
    qr_code_base64 = None

    if request.method == "POST":
        original_url = request.POST.get("original_url")
        custom_code = request.POST.get("custom_code")
        url_obj, created = URL.objects.get_or_create(original_url=original_url)
        if custom_code:
            url_obj.short_code = custom_code
            url_obj.save()
        short_url = request.build_absolute_uri(f"/{url_obj.short_code}")

        # Generate QR code
        img = qrcode.make(short_url)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "index.html", {"short_url": short_url, "qr_code": qr_code_base64})

def redirect_url(request, short_code):
    url_obj = get_object_or_404(URL, short_code=short_code)
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.original_url)
