from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = 'talla'
        verbose_name_plural = 'tallas'
        ordering = ['name']

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'color'
        verbose_name_plural = 'colores'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    GENDER_CHOICES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
        ('N', 'Niño'),
    ]

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # 🆕 Relaciones ManyToMany
    colors = models.ManyToManyField(Color, related_name='products', blank=True)
    sizes = models.ManyToManyField(Size, related_name='products', blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='H')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.category.slug, self.slug])
