from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from django.utils.timezone import make_aware
from datetime import datetime
from xhtml2pdf import pisa
import qrcode
import io
import base64

from .models import InventoryItem, RequestItem, Notification, CustomUser
from .forms import (
    InventoryItemForm,
    RequestItemForm,
    CustomUserCreationForm,
    CustomUserChangeForm,
    InventoryReportSearchForm,
    EditUserForm
)
from inventory.utils import send_real_time_notification

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard_redirect')  # Updated name here
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def dashboard_redirect(request):
    role = getattr(request.user, 'role', '').lower()
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'staff':
        return redirect('user_dashboard')
    return redirect('login')

@login_required
def admin_dashboard(request):
    context = {
        'total_items': InventoryItem.objects.count(),
        'total_requests': RequestItem.objects.count(),
        'pending_requests': RequestItem.objects.filter(status='pending').count(),
        'total_users': User.objects.count(),
        'notifications': Notification.objects.filter(user=request.user, is_read=False),
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def user_dashboard(request):
    context = {
        'requests': RequestItem.objects.filter(requester=request.user).order_by('-created_at'),
        'notifications': Notification.objects.filter(user=request.user, is_read=False),
    }
    return render(request, 'user_dashboard.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def manage_inventory(request):
    items = InventoryItem.objects.all().order_by('-created_at')
    return render(request, 'manage_inventory.html', {'items': items})

@login_required
def manage_requests(request):
    return render(request, 'manage_requests.html', {'requests': RequestItem.objects.all()})

@login_required
def manage_users(request):
    return render(request, 'manage_users.html', {'users': User.objects.all()})

@login_required
def add_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item added successfully!")
            return redirect('manage_inventory')
    else:
        form = InventoryItemForm()
    return render(request, 'add_item.html', {'form': form})

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully.')
            return redirect('manage_inventory')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'edit_item.html', {'form': form, 'item': item})

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'Item "{item_name}" deleted successfully.')
        return redirect('manage_inventory')


@login_required
def request_item(request):
    if request.method == 'POST':
        form = RequestItemForm(request.POST)
        if form.is_valid():
            inventory_request = form.save(commit=False)
            inventory_request.requester = request.user
            inventory_request.save()
            for admin in User.objects.filter(is_staff=True):
                Notification.objects.create(user=admin, message=f"{request.user.username} requested {inventory_request.item.name}")
            return redirect('user_dashboard')
    else:
        form = RequestItemForm()
    return render(request, 'request_item.html', {'form': form})

@login_required
def approve_request(request, request_id):
    req = get_object_or_404(RequestItem, pk=request_id)

    if req.status != 'approved':
        item = req.item
        if item.quantity >= req.quantity:
            item.quantity -= req.quantity
            item.save()
            req.status = 'approved'
            req.save()
            messages.success(request, f"{req.quantity} unit(s) of {item.name} deducted.")
        else:
            messages.error(request, f"Not enough stock for {item.name}.")
    else:
        messages.warning(request, "This request is already approved.")

    return redirect('manage_requests')  # or your preferred redirect


@login_required
def reject_request(request, request_id):
    inventory_request = get_object_or_404(RequestItem, id=request_id)
    inventory_request.status = 'rejected'
    inventory_request.save()
    return redirect('manage_requests')

@login_required
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('manage_users')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'add_user.html', {'form': form})

@login_required
def edit_user(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user_obj)
        password_form = PasswordChangeForm(user_obj, request.POST)

        if 'new_password1' in request.POST:  # Password form submitted
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user_obj)
                messages.success(request, f'Password for {user_obj.username} updated successfully.')
                return redirect('edit_user', user_id=user_id)
        else:  # Regular form submitted
            if form.is_valid():
                form.save()
                messages.success(request, 'User updated successfully.')
                return redirect('edit_user', user_id=user_id)
    else:
        form = CustomUserCreationForm(instance=user_obj)
        password_form = PasswordChangeForm(user_obj)

    return render(request, 'edit_user.html', {
        'form': form,
        'user_obj': user_obj,
        'password_form': password_form
    })

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user != request.user:  # Prevent self-deletion if needed
        user.delete()
        messages.success(request, f'User "{user.username}" was deleted successfully.')
    else:
        messages.warning(request, "You cannot delete your own account.")
    return redirect('manage_users')

@login_required
def change_user_password(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
            return redirect('edit_user', user_id=user.id)
    else:
        form = PasswordChangeForm(user)
    return render(request, 'change_user_password.html', {'form': form, 'user_obj': user})

@login_required
def notifications(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notes})

@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')

@login_required
def acknowledge_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('notifications')

@login_required
def generate_reports(request):
    form = InventoryReportSearchForm(request.GET or None)
    items = InventoryItem.objects.all()
    if form.is_valid():
        search = form.cleaned_data.get('search')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if search:
            items = items.filter(name__icontains=search)
        if start_date:
            items = items.filter(created_at__date__gte=start_date)
        if end_date:
            items = items.filter(created_at__date__lte=end_date)
    return render(request, 'generate_report.html', {'form': form, 'items': items})

def generate_qr_code(data):
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

@login_required
def print_request_report(request, request_id):
    request_obj = get_object_or_404(RequestItem, id=request_id)
    item = request_obj.item
    qr_data = f"Item: {item.name}, Location: {item.location}, Status: {request_obj.status}"
    qr_code_url = generate_qr_code(qr_data)
    return render(request, 'print_item_report.html', {'item': item, 'request_obj': request_obj, 'qr_code_url': qr_code_url})

@login_required
def export_item_report_pdf(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    item_request = RequestItem.objects.filter(item=item).first()
    context = {'item': item, 'request_obj': item_request}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="item_report.pdf"'
    html = get_template('print_item_report.html').render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response
