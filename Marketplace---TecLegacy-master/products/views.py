from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Category, Product
from django.db import models

def index(request):
    """Vista de la página principal con productos destacados."""
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'products/index.html', context)


def product_list(request, category_slug=None):
    """Lista de productos, puede filtrarse por categoría."""
    category = None
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # Paginación: 12 productos por página
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'category': category,
        'categories': categories,
        'products': products_page,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, category_slug, product_slug):
    """Detalle de un producto específico."""
    product = get_object_or_404(
        Product,
        slug=product_slug,
        category__slug=category_slug,
        is_available=True
    )

    # Productos relacionados: misma categoría, excepto el actual
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def search_products(request):
    """Búsqueda de productos."""
    query = request.GET.get('q', '')
    products = []

    if query:
        # Buscar por nombre, descripción o categoría
        products = Product.objects.filter(
            is_available=True
        ).filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(category__name__icontains=query)
        ).distinct()

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/search_results.html', context)