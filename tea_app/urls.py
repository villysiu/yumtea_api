from django.urls import path 
from . import views 
  
urlpatterns = [ 
  # path('categories', views.Categories),
    path('categories', views.Categories.as_view()),

    path('milks', views.Milks.as_view()),
    # path('milks/<int:pk>', views.SingleMilk.as_view()),

    path('menuitems', views.MenuItems.as_view()),
    # path('menuitems/<int:pk>', views.SingleMenuItem.as_view()),

    path('cart', views.CartItems.as_view()),
    path('cart/<int:pk>', views.SingleCartItem.as_view()),

    path('orders', views.Orders.as_view()), 
    # path('orders/<int:pk>', views.SingleOrder.as_view()),
    # path('orderitems/<int:pk>', views.SingleOrderItem.as_view()),
]