from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Menu, MenuItem, Order
import razorpay
from django.conf import settings

# Home page
def index(request):
    categories = Menu.objects.all()
    return render(request, "index.html", {"categories": categories})

# Menu page
def menu_view(request):
    categories = Menu.objects.all()
    category_id = request.GET.get('category')  # category from home page

    if category_id:
        all_items = MenuItem.objects.filter(menu_id=category_id).select_related('menu')
        selected_category = get_object_or_404(Menu, id=category_id)
    else:
        all_items = MenuItem.objects.select_related('menu').all()
        selected_category = None

    return render(request, 'menupage.html', {
        'categories': categories,
        'all_items': all_items,
        'selected_category': selected_category
    })

# Menu details
def menu_details(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    return render(request, "menu_details.html", {"item": item})

# Order page
def order_page(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login to place an order.")
        return redirect("login")

    item_id = request.GET.get('item_id')
    if not item_id:
        messages.error(request, "No item selected.")
        return redirect("menu")

    item = get_object_or_404(MenuItem, id=item_id)
    qty = int(request.GET.get('qty', 1))
    if qty < 1: qty = 1

    return render(request, "order_page.html", {
        "item": item,
        "qty": qty,
        "total": item.price * qty
    })

# from django.core.mail import send_mail

def order_confirm(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login to place an order.")
        return redirect("login")

    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("menu")

    item_id = request.POST.get("item_id")
    qty = int(request.POST.get("qty", 1))
    payment_method = request.POST.get("payment_method")

    item = get_object_or_404(MenuItem, id=item_id)
    total = item.price * qty

    order = Order.objects.create(
        user=request.user,
        item=item,
        quantity=qty,
        total_price=total,
        status="pending"
    )

    if payment_method == "cod":
        order.status = "Confirmed"
        order.save()

        # ✅ Send order confirmation email (COD)
        subject = "Your Cafe Order is Confirmed! ✅"
        message = f"""
Hello {request.user.first_name or request.user.username},

Thank you for your order at Cafe! 🍕☕🍔

📌 Order Details:
- Item: {item.name}
- Quantity: {qty}
- Total: ₹{total}

Payment Method: Cash on Delivery

We will prepare your order soon. 🚀

- Cafe Team
"""
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=True)

        return render(request, "order_confirm.html", {"order": order})
    else:
        return redirect("payment_page", order_id=order.id)

# Payment page
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": int(order.total_price * 100),
        "currency": "INR",
        "payment_capture": "1"
    })
    context = {
        "order": order,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": order.total_price,
        "currency": "INR",
    }
    return render(request, "payment.html", context)

# Payment success
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "Paid"
    order.save()
    return render(request, "order_confirm.html", {"order": order})

# About & Contact
def about_view(request):
    return render(request, "about.html")

def contact_view(request):
    return render(request, "contact.html")

# Register
def register_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fullname
        )
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect("login")
    return render(request, "register.html")

# # Login
# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             messages.success(request, "Login successful!")
#             return redirect("index")
#         else:
#             messages.error(request, "Invalid username or password")
#             return redirect("login")
#     return render(request, "login.html")

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("index")
from django.core.mail import send_mail
# from django.conf import settings

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful!")

            # ✅ Send email after login
            subject = "Cafe Login Successful"
            message = f"""
Hello {user.first_name or user.username},

You have successfully logged into your Cafe account.

Happy Ordering! ☕🍰🍔

- Cafe Team
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # sender
                [user.email],  # recipient
                fail_silently=True,
            )

            return redirect("index")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "login.html")
