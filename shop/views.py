from django.shortcuts import render
from .models import Product
from django.core.paginator import Paginator
from .forms import ProductFilterForm
from django.shortcuts import render
from .forms import ContactForm
from .forms import ProductForm

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'shop/product_success.html')
    else:
        form = ProductForm()
    return render(request, 'shop/add_product.html', {'form': form})

def product_list(request):
    products = Product.objects.all()

    # Paginare (10 produse pe pagina)
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_list.html', {'page_obj': page_obj})


def product_list(request):
    form = ProductFilterForm(request.GET)
    products = Product.objects.all()

    if form.is_valid():
        name = form.cleaned_data.get('name')
        if name:
            products = products.filter(name__icontains=name)
        price_min = form.cleaned_data.get('price_min')
        if price_min is not None:
            products = products.filter(price__gte=price_min)
        price_max = form.cleaned_data.get('price_max')
        if price_max is not None:
            products = products.filter(price__lte=price_max)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_list.html', {'page_obj': page_obj, 'form': form})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # salveaza in json local
            form.save_message()
            return render(request, 'shop/contact_success.html')
    else:
        form = ContactForm()

    return render(request, 'shop/contact.html', {'form': form})
