from django.urls import path
from .views import home_view ,suggestion_Get ,Thanks_View,Sug_View,Product_Get,Product_View,update_product,delete_product

urlpatterns = [path('', home_view, name='home'),
               path('suggestion/', suggestion_Get, name='suggestion'),
               path('thanks/', Thanks_View, name='thanks'),
               path('results/', Sug_View, name='results'),
               path('product_input/', Product_Get, name='product_input'),
               path('product_output/', Product_View, name='products_output'),
               path("product_update/<int:id>/", update_product, name='product_update'),
        
               path('product_delete/<int:id>/', delete_product, name='product_delete')
               ]

               
               
               