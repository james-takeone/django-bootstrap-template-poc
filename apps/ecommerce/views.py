from http import HTTPStatus

import stripe
from django import views
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from apps.ecommerce.forms import ProductForm
from apps.ecommerce.models import Products, Sales


class ProductsView(views.View):

    def get(self, request):
        form = ProductForm()
        return render(request, "", context={
            "form": form
        })

    def post(self, request):
        product = ProductForm(request.POST)
        if not product.is_valid():
            return JsonResponse(data={
                "detail": ""
            }, status=HTTPStatus.BAD_REQUEST)
        product.save()
        return JsonResponse(data={
            "detail": ""
        }, status=HTTPStatus.OK)

    def put(self, request, product_id):
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return JsonResponse(data={
                "message": ""
            }, status=HTTPStatus.NOT_FOUND)
        product_form = ProductForm(request.PUT, instance=product)
        if not product_form.is_valid():
            return JsonResponse(data={
                "detail": ""
            }, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse(data={
            "detail": ""
        }, status=HTTPStatus.OK)

    def delete(self, request, product_id):
        to_delete_product = Products.objects.filter(id=product_id)
        if to_delete_product.count() == 0:
            return JsonResponse(data={
                "detail": ""
            }, status=HTTPStatus.NOT_FOUND)
        to_delete_product.delete()
        return JsonResponse(data={
            "detail": ""
        }, status=HTTPStatus.OK)


def purchase(request):
    return render(request, 'ecommerce/purchase.html')


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        return JsonResponse({'publicKey': settings.STRIPE_PUBLISHABLE_KEY}, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        try:
            product_pk = request.GET.get('product')
            if not product_pk:
                raise Exception("product id not provided.")
            product = Products.objects.get(pk=product_pk)
            quantity = request.GET.get("quantity", 1)
            domain_url = 'http://localhost:8000'
            stripe.api_key = settings.STRIPE_SECRET_KEY
        except Exception as e:
            return JsonResponse({'error': str(e)})

        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + f'{reverse("stripe-success")}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=domain_url + reverse("stripe-cancelled"),
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        "price": product.stripe_price_id,
                        "quantity": quantity
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


def success(request):
    session_id = request.GET.get("session_id")
    session = stripe.checkout.Session.list_line_items(session_id)
    for line_item in session.data:
        product = Products.objects.filter(stripe_product_id=line_item.price.product).first()
        if product is None:
            continue
        sale = Sales.objects.create(
            product=product,
            value=product.price*line_item.quantity,
            fees=product.price,
            quantity=line_item.quantity,
            client=request.user
        )
    return render(request, "ecommerce/success.html")


def cancelled(request):
    return render(request, "ecommerce/cancelled.html")

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)