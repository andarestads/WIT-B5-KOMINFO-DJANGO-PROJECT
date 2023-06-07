from typing import Any
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views import generic
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt



from .forms import CheckoutForm
from .models import ProdukItem, Category, OrderProdukItem, Order, AlamatPengiriman, Payment

import stripe

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")

class HomeListView(generic.ListView):
    template_name = 'home.html'
    queryset = ProdukItem.objects.all()
    paginate_by = 4
    

# def KategoriView(request):
#    title = title
#    produk = ProdukItem.objects.all()
#    categories = Category.objects.all()
    
#    return render(request, 'home.html', {'title': title, 'produk': produk, 'categories': categories })
    
class KontakView(generic.ListView):
    template_name = 'kontak.html'
    queryset = ProdukItem.objects.all()
    paginate_by = 4    

class ProdukSearchView(generic.ListView):
    template_name = 'home.html'
    paginate_by = 4    

    def get_queryset(self):
        query = self.request.GET.get('q')
        return ProdukItem.objects.filter(nama_produk__icontains=query)
    
# def CategoryView(request, cats):
#    category_produk = ProdukItem.objects.filter(kategori=cats)
#    return render(request, 'category.html', {'cats':cats, 'category_produk':category_produk})

#    categories = Category.objects.all()

#    context = {
#        "categories": categories,
#    }

#    return render(request, 'home.html', context)


class ProductDetailView(generic.DetailView):
    template_name = 'product_detail.html'
    queryset = ProdukItem.objects.all()

class CheckoutView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.produk_items.count() == 0:
                messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
                return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            order = {}
            messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
            return redirect('toko:home-produk-list')

        context = {
            'form': form,
            'keranjang': order,
        }
        template_name = 'checkout.html'
        return render(self.request, template_name, context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                alamat_1 = form.cleaned_data.get('alamat_1')
                alamat_2 = form.cleaned_data.get('alamat_2')
                negara = form.cleaned_data.get('negara')
                kode_pos = form.cleaned_data.get('kode_pos')
                opsi_pembayaran = form.cleaned_data.get('opsi_pembayaran')
                alamat_pengiriman = AlamatPengiriman(
                    user=self.request.user,
                    alamat_1=alamat_1,
                    alamat_2=alamat_2,
                    negara=negara,
                    kode_pos=kode_pos,
                )

                alamat_pengiriman.save()
                order.alamat_pengiriman = alamat_pengiriman
                order.save()
                if opsi_pembayaran == 'P':
                    return redirect('toko:payment', payment_method='paypal')
                else:
                    return redirect('toko:payment', payment_method='stripe')

            messages.warning(self.request, 'Gagal checkout')
            return redirect('toko:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('toko:order-summary')
        

class PaymentView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        template_name = 'payment.html'
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            
            paypal_data = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': order.get_total_harga_order,
                'item_name': f'Pembayaran belajanan order: {order.id}',
                'invoice': f'{order.id}-{timezone.now().timestamp()}' ,
                'currency_code': 'USD',
                'notify_url': self.request.build_absolute_uri(reverse('paypal-ipn')),
                'return_url': self.request.build_absolute_uri(reverse('toko:paypal-return')),
                'cancel_return': self.request.build_absolute_uri(reverse('toko:paypal-cancel')),
            }
        
            qPath = self.request.get_full_path()
            isPaypal = 'paypal' in qPath
        
            form = PayPalPaymentsForm(initial=paypal_data)
            context = {
                'paypalform': form,
                'order': order,
                'is_paypal': isPaypal,
            }
            return render(self.request, template_name, context)

        except ObjectDoesNotExist:
            return redirect('toko:checkout')
        
#    def post(self, request, *args, **kwargs):
#        template_name = 'payment.html'
#        order = Order.objects.get(user=self.request.user, ordered=False)

#        checkout_session = stripe.checkout.Session.create(
#            payment_method_types=['card'],
#            line_items = [
#                {
#                    'price_data': {
#                        'currency': 'usd',
#                        'unit_amount': 2000,
#                        'product_data': {
#                            'name': 'Stubborn Attachments',
#                        },
#                    },
#                    'quantity': 1,
#                },
#            ],
#            mode='payment'
#            success_url='toko:stripe-return',
#            cancel_url='toko:stripe-cancel',
#            )
#        return JsonResponse({
#            'id': checkout_session.id
#        })


class OrderSummaryView(LoginRequiredMixin, generic.TemplateView):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'keranjang': order
            }
            template_name = 'order_summary.html'
            return render(self.request, template_name, context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('/')
 

def add_to_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_produk_item, _ = OrderProdukItem.objects.get_or_create(
            produk_item=produk_item,
            user=request.user,
            ordered=False
        )
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                order_produk_item.quantity += 1
                order_produk_item.save()
                pesan = f"ProdukItem sudah diupdate menjadi: { order_produk_item.quantity }"
                messages.info(request, pesan)
                return redirect('toko:produk-detail', slug = slug)
            else:
                order.produk_items.add(order_produk_item)
                messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
                return redirect('toko:produk-detail', slug = slug)
        else:
            tanggal_order = timezone.now()
            order = Order.objects.create(user=request.user, tanggal_order=tanggal_order)
            order.produk_items.add(order_produk_item)
            messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
            return redirect('toko:produk-detail', slug = slug)
    else:
        return redirect('/accounts/login')

def remove_from_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_query = Order.objects.filter(
            user=request.user, ordered=False
        )
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                try: 
                    order_produk_item = OrderProdukItem.objects.filter(
                        produk_item=produk_item,
                        user=request.user,
                        ordered=False
                    )[0]
                    
                    order.produk_items.remove(order_produk_item)
                    order_produk_item.delete()

                    pesan = f"ProdukItem sudah dihapus"
                    messages.info(request, pesan)
                    return redirect('toko:produk-detail',slug = slug)
                except ObjectDoesNotExist:
                    print('Error: order ProdukItem sudah tidak ada')
            else:
                messages.info(request, 'ProdukItem tidak ada')
                return redirect('toko:produk-detail',slug = slug)
        else:
            messages.info(request, 'Tidak ada order yang aktif')
            return redirect('toko:produk-detail',slug = slug)
    else:
        return redirect('/accounts/login')

def update_qty(request, slug):
    if request.user.is_authenticated:
        update_qty = get_object_or_404(update_qty, slug=slug)
        if update_qty == "plus":
            OrderProdukItem.quantity += 1
            order_produk_item.save()
            messages.info(request, "Product quantity was updated.")
        elif update_qty == "minus":
            OrderProdukItem.quantity -= 1
            if OrderProdukItem.quantity < 1:
                order_produk_item.delete()
                messages.info(request, "Product was removed from cart.")
            else:
                order_produk_item.save()
                messages.info(request, "Product quantity was updated.")
    return redirect("order-summary")

# order summary cart
    
# def show_cart(request):
#    produk_item = get_object_or_404(ProdukItem)
#    order_produk_item, _ = OrderProdukItem.objects.get_or_create(
#        produk_item=produk_item,
#        user=request.user,
#        ordered=False
#        )
#    order_query = OrderProdukItem.objects.filter(user=request.user, ordered=False)
#    amount = 0
#    for produk in order_query:
#        value = produk.quantity * produk.produk_item.harga_diskon
#        amount = amount + value
#    totalamount = amount

#    return render(request,'/add-to-cart.html',locals())

@csrf_exempt
def paypal_return(request):
    if request.user.is_authenticated:
        try:
            print('paypal return', request)
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.user=request.user
            payment.amount = order.get_total_harga_order()
            payment.payment_option = 'P' # paypal kalau 'S' stripe
            payment.charge_id = f'{order.id}-{timezone.now()}'
            payment.timestamp = timezone.now()
            payment.save()
            
            order_produk_item = OrderProdukItem.objects.filter(user=request.user,ordered=False)
            order_produk_item.update(ordered=True)
            
            order.payment = payment
            order.ordered = True
            order.save()

            messages.info(request, 'Pembayaran sudah diterima, terima kasih')
            return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            messages.error(request, 'Periksa kembali pesananmu')
            return redirect('toko:order-summary')
    else:
        return redirect('/accounts/login')

@csrf_exempt
def paypal_cancel(request):
    messages.error(request, 'Pembayaran dibatalkan')
    return redirect('toko:order-summary')

@csrf_exempt
def stripe_return(request):
    if request.user.is_authenticated:
        try:
            print('stripe return', request)
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.user=request.user
            payment.amount = order.get_total_harga_order()
            payment.payment_option = 'S'
            payment.charge_id = f'{order.id}-{timezone.now()}'
            payment.timestamp = timezone.now()
            payment.save()
            
            order_produk_item = OrderProdukItem.objects.filter(user=request.user,ordered=False)
            order_produk_item.update(ordered=True)
            
            order.payment = payment
            order.ordered = True
            order.save()

            messages.info(request, 'Pembayaran sudah diterima, terima kasih')
            return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            messages.error(request, 'Periksa kembali pesananmu')
            return redirect('toko:order-summary')
    else:
        return redirect('/accounts/login')

@csrf_exempt
def stripe_cancel(request):
    messages.error(request, 'Pembayaran dibatalkan')
    return redirect('toko:order-summary')

