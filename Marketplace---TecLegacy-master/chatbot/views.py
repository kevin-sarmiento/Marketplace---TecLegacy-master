from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from products.models import Product, Category
from .models import ChatbotQuery
import json
import re
from django.db import models

@csrf_exempt
def chatbot_query(request):
    """API para procesar consultas del chatbot."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').lower()

            # Guardar la consulta en la base de datos
            chat_query = ChatbotQuery(query=query)

            # Palabras clave para buscar por categoría
            category_keywords = {
                'portatil': 'Portátiles Gaming',
                'laptop': 'Portátiles Gaming',
                'notebook': 'Portátiles Gaming',
                'gaming': None,# Buscar en todas las categorías con "gaming"
                'juego': None,
                'teclado': 'Periféricos',
                'mouse': 'Periféricos',
                'raton': 'Periféricos',
                'auricular': 'Periféricos',
                'cascos': 'Periféricos',
                'tarjeta': 'Componentes',
                'grafica': 'Componentes',
                'procesador': 'Componentes',
                'cpu': 'Componentes',
                'placa': 'Componentes',
                'monitor': 'Monitores',
                'pantalla': 'Monitores',
                'silla': 'Sillas Gaming',
            }

            # Patrones para extraer información de precio
            price_pattern = r'menos de (\d+)|bajo (\d+)|maximo (\d+)|hasta (\d+)'
            price_match = re.search(price_pattern, query)
            max_price = None

            if price_match:
                # Encontrar el primer grupo que no sea None
                for group in price_match.groups():
                    if group is not None:
                        max_price = int(group) * 1000
                        break

            # Iniciar búsqueda de productos
            products_query = Product.objects.filter(is_available=True)

            # Respuestas especiales para saludos o preguntas generales
            greetings = ['hola', 'hey', 'saludos', 'buenos días', 'buenas tardes', 'buenas noches']
            help_keywords = ['ayuda', 'ayudame', 'como funciona', 'que haces']

            if any(greeting in query for greeting in greetings):
                response = "¡Hola! Soy el asistente de TecLegacy. Puedo ayudarte a encontrar productos gaming y tecnología. ¿Qué estás buscando hoy?"
                chat_query.response = response
                chat_query.save()
                return JsonResponse({
                    'success': True,
                    'response': response
                })

            if any(keyword in query for keyword in help_keywords):
                response = "Puedo ayudarte a encontrar productos en nuestra tienda. Prueba preguntándome por productos específicos como 'muéstrame teclados gaming' o 'busco un monitor de 27 pulgadas'. También puedes indicarme un rango de precio como 'monitores por menos de 500'."
                chat_query.response = response
                chat_query.save()
                return JsonResponse({
                    'success': True,
                    'response': response
                })

            # Filtrar por categoría si se detecta una palabra clave
            category_filter_applied = False
            for keyword, category_name in category_keywords.items():
                if keyword in query:
                    if category_name:  # Si hay una categoría específica
                        try:
                            category = Category.objects.get(name=category_name)
                            products_query = products_query.filter(category=category)
                            category_filter_applied = True
                        except Category.DoesNotExist:
                            pass
                    else:  # Para palabras como "gaming" que pueden estar en varias categorías
                        products_query = products_query.filter(name__icontains=keyword)
                        category_filter_applied = True

            # Si no se aplicó filtro por categoría, buscar por nombre
            if not category_filter_applied:
                # Extraer palabras clave potenciales (palabras de 3+ caracteres)
                keywords = [word for word in query.split() if len(word) >= 3]
                for keyword in keywords:
                    products_query = products_query.filter(
                        models.Q(name__icontains=keyword) |
                        models.Q(description__icontains=keyword)
                    )

            # Filtrar por precio máximo si se especificó
            if max_price:
                products_query = products_query.filter(price__lte=max_price)

            # Limitar a 5 productos como máximo
            products = products_query[:5]

            # Crear respuesta basada en los resultados
            if products.exists():
                if max_price:
                    response = f"He encontrado estos productos tacaño, por menos de ${max_price / 1000}k:<br>"
                else:
                    response = "He encontrado estos productos para que compre si o si:<br>"

                for product in products:
                    price_formatted = '{:,.0f}'.format(product.price).replace(',', '.')
                    response += f"- <a href='/products/{product.category.slug}/{product.slug}/'>{product.name}</a> - ${price_formatted}<br>"

                if products.count() == 5:
                    response += "<br>Estos son solo algunos resultados. ¿Quieres más detalles o buscar algo más específico?"
            else:
                response = f"Lo siento, no encontré productos que coincidan con '{query}'. Prueba con otra busqueda o lo veo pues describiendo mejor lo que busca aaa."

                # Sugerir categorías disponibles
                categories = Category.objects.filter(is_active=True)
                if categories.exists():
                    response += "<br><br>Puedes explorar nuestras categorías:<br>"
                    for category in categories:
                        response += f"- <a href='/products/{category.slug}/'>{category.name}</a><br>"

            # Guardar la respuesta y devolver
            chat_query.response = response
            chat_query.save()

            return JsonResponse({
                'success': True,
                'response': response
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })