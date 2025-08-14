from django.shortcuts import render, redirect, get_object_or_404
from .models import URL
import qrcode
from io import BytesIO
import base64

def home(request):
    # Initialize context variables
    context = {
        "short_url": None,
        "qr_code": None,
        "error": None,
    }

    if request.method == "POST":
        original_url = request.POST.get("original_url")
        custom_code = request.POST.get("custom_code", "").strip()

        # --- Custom Code Validation ---
        if custom_code:
            # Check if the custom code already exists
            if URL.objects.filter(short_code=custom_code).exists():
                context["error"] = f"The alias '{custom_code}' is already in use. Please choose another."
                # Fetch all URLs for history display even when there's an error
                context["urls"] = URL.objects.order_by('-created_at')
                return render(request, "index.html", context)
        
        # --- URL Creation ---
        if custom_code:
            # Create a new URL object with the custom code
            url_obj = URL.objects.create(
                original_url=original_url,
                short_code=custom_code
            )
        else:
            # Find an existing URL or create a new one with a generated code
            # This prevents creating multiple short links for the same original URL
            url_obj, created = URL.objects.get_or_create(original_url=original_url)
        
        # Build the full short URL
        short_url = request.build_absolute_uri(f"/{url_obj.short_code}")
        context["short_url"] = short_url

        # --- QR Code Generation ---
        qr_img = qrcode.make(short_url)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        context["qr_code"] = qr_code_base64

    # --- Fetch URL History ---
    # Fetch all URLs to display in the history table, ordered by most recent
    all_urls = URL.objects.order_by('-created_at')
    context["urls"] = all_urls

    return render(request, "index.html", context)

def redirect_url(request, short_code):
    """
    Redirects the short URL to the original URL and increments the click count.
    """
    # Find the URL object by its short code, or return a 404 error if not found
    url_obj = get_object_or_404(URL, short_code=short_code)
    
    # Increment the click counter
    url_obj.clicks += 1
    url_obj.save()
    
    # Redirect to the original URL
    return redirect(url_obj.original_url)

