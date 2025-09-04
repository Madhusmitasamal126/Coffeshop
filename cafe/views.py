from django.shortcuts import render, get_object_or_404, redirect
from .models import Menu, MenuItem, Order
import razorpay
from django.conf import settings

def index(request):
    categories = Menu.objects.all()
    return render(request, "index.html", {"categories": categories})


def menu_view(request):
    category_id = request.GET.get("category")
    highlighted_item_id = request.GET.get("highlighted")

    if category_id:
        categories = Menu.objects.filter(id=category_id).prefetch_related('items')
    else:
        categories = Menu.objects.prefetch_related('items').all()

    return render(request, "menupage.html", {
        "categories": categories,
        "highlighted_item_id": highlighted_item_id
    })


def order_page(request):
    item_id = request.GET.get('item_id')
    if not item_id:
        return render(request, 'order_page.html', {"error": "No item selected."})

    try:
        item = MenuItem.objects.get(id=item_id)
    except MenuItem.DoesNotExist:
        return render(request, 'order_page.html', {"error": "Item not found."})

    try:
        qty = int(request.GET.get('qty', 1))
        if qty < 1:
            qty = 1
    except ValueError:
        qty = 1

    return render(request, 'order_page.html', {
        'item': item,
        'qty': qty,
        'total': item.price * qty
    })


def order_confirm(request):
    if request.method != "POST":
        return render(request, 'order_page.html', {"error": "Invalid request."})

    item_id = request.POST.get('item_id')
    qty = int(request.POST.get('qty', 1))
    payment_method = request.POST.get('payment_method')

    item = get_object_or_404(MenuItem, id=item_id)
    total = item.price * qty

    # Save order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        item=item,
        quantity=qty,
        total_price=total,
        status="pending"
    )
    if payment_method == "cod":
    # Cash on delivery → confirm immediately
      order.status = "Confirmed"
      order.save()
      return render(request, "order_confirmed.html", {"order": order})  # <-- no "template/" prefix

    else:
        # Online payment → go to Razorpay
        return redirect("payment_page", order_id=order.id)


def about_view(request):
    return render(request, "about.html")


def contact_view(request):
    return render(request, "contact.html")


def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    razorpay_order = client.order.create({
        "amount": int(order.total_price * 100),  # in paisa
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


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "Paid"
    order.save()
    return render(request, "order_confirmed.html", {"order": order})
