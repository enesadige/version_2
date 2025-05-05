from .models import Category

def categories_processor(request):
    """Her şablonda kategorileri erişilebilir yapar"""
    categories = Category.objects.all()
    return {'categories': categories} 