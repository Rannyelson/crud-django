from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index,name='home'),
    path('product/<int:pk>', views.product_detail, name='product_detail'),
    path('create', views.create,name='create'),
    path('update', views.update,name='update'),
    path('update/<int:pk>', views.update_product, name='update_product'),
    path('delete', views.delete,name='delete'),
    path('categories', views.categories, name='categories'),
    path('categories/create', views.category_create, name='category_create'),
    path('categories/<int:pk>/update', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete', views.category_delete, name='category_delete'),
    path('carrinho', views.cart, name='cart'),
    path('carrinho/adicionar/<int:pk>', views.add_to_cart, name='add_to_cart'),
    path('carrinho/remover/<int:pk>', views.remove_from_cart, name='remove_from_cart'),
    path('carrinho/finalizar', views.checkout, name='checkout'),
    path('dashboard', views.dashboard, name='dashboard'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
