from rest_framework.response import Response
from .models import Category, MenuItem, Milk, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, MilkSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import MenuItemsPermission, CartItemsPermission, SingleCartItemPermission, OrdersPermission, SingleOrderPermission, SingleOrderItemPermission

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.
class Categories(generics.ListCreateAPIView):   
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [MenuItemsPermission]

class Milks(generics.ListCreateAPIView):   
    queryset = Milk.objects.all()
    serializer_class = MilkSerializer
    permission_classes = [MenuItemsPermission]


class MenuItems(generics.ListCreateAPIView):   
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [MenuItemsPermission]
    
    # pagination_class = CustomPagination
    # ordering_fields=['price']
    # search_fields = ['title']
    # filterset_fields = ['category_id', 'category__slug']




class CartItems(generics.ListCreateAPIView, generics.DestroyAPIView):

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, CartItemsPermission]
    filterset_fields = ['user_id']
    def get_queryset(self):
        queryset=Cart.objects.all()
        current_user = self.request.user
        if not current_user.groups.filter(name='Manager').exists():
            queryset = queryset.filter(user=current_user)
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        print("delete cart")
        queryset = self.get_queryset()

        for item in queryset:
            item.delete()
        return Response({'message': 'User Cart is Empty.'}, 204)

class SingleCartItem(generics.RetrieveUpdateDestroyAPIView):   
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, SingleCartItemPermission]
    queryset = Cart.objects.all()
        
class Orders(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrdersPermission]
    filterset_fields = ['user_id']

    def get_queryset(self):
        queryset = Order.objects.all()
        current_user = self.request.user
        if not current_user.groups.filter(name='Manager').exists():
            queryset = queryset.filter(user=current_user)

        return queryset
    
    def create(self, request, *args, **kwargs):
        
    #     current_user = self.request.user
        user_cart_items = Cart.objects.filter(user=self.request.user)
        #<QuerySet [<Cart: Cart object (14)>, <Cart: Cart object (15)>]>
       
        if len(user_cart_items) == 0:
            return Response({'message': 'Cart is empty.'}, 200)

        orderitems=[]
        for item in list(user_cart_items.values()):
            print(item)
            dict = {
                'menuitem_pk': item['menuitem_id'],
                'quantity': item['quantity'],
                'milk_pk':item['milk_id'],
                'temperature': item['temperature'],
                'sweetness': item['sweetness'],
                'size': item['size'],
                'price': item['price'],
            }
            orderitems.append(dict)

        print(orderitems)
        
        serialized_order = OrderSerializer(
            data = { 'orderitems': orderitems, 'tip': request.data['tip'] },
            context = {'request': request}
        )
        
        if serialized_order.is_valid(raise_exception=True):
            serialized_order.save()
            for user_cart_item in user_cart_items:
                user_cart_item.delete()
            return Response(serialized_order.data, 201)



# class SingleOrder(generics.RetrieveUpdateDestroyAPIView):   
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated, SingleOrderPermission]

class SingleOrderItem(generics.RetrieveUpdateDestroyAPIView):   
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, SingleOrderItemPermission]

    
