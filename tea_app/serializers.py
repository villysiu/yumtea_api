from rest_framework import serializers 
from .models import Category, MenuItem, Milk, Cart, OrderItem, Order
from datetime import date
from django.db.models import Sum, ExpressionWrapper,F, DecimalField
from decimal import *
from django.db import IntegrityError

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"
        # fields = ['pk','title', 'slug', 'desc', 'image_path']

class MilkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milk
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    
    milk_pk = serializers.PrimaryKeyRelatedField(
        source='Milk',
        queryset=Milk.objects.all(), 
        write_only=True,
    )
    category_pk = serializers.PrimaryKeyRelatedField(
        source='Category',
        queryset=Category.objects.all(), 
        write_only=True,
    )
    # sweetness = serializers.CharField()
    temperature = serializers.CharField(source='get_temperature_display')

    class Meta:
        model = MenuItem
        fields = ['pk', 'title', 'price', 'description', 'image_path','temperature',
                  'milk_id', 'milk_pk', 
                  'category_id', 'category_pk']
    
   
    # POST
    # def create(self, validated_data):
    #     print("in serializer")
    #     print(validated_data)
    #     # milk_obj = validated_data.pop('Milk')
    #     category_obj = validated_data.pop('Category')
    #     menuitem_obj = MenuItem.objects.create( category=category_obj, **validated_data)
    #     return menuitem_obj
    
    # #PATCH/ PUT
    # def update(self, instance, validated_data):
    #     print(validated_data)
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.price = validated_data.get('price', instance.price)
    #     instance.description = validated_data.get('description', instance.description)
    #     # instance.inventory = validated_data.get('inventory', instance.inventory)
    #     # instance.milk = validated_data.get('Milk', instance.milk)
    #     instance.category = validated_data.get('Category', instance.category)
    #     instance.temperature = validated_data.get('temperature', instance.temperature)
    #     # instance.sweetness = validated_data.get('sweetness', instance.sweetness)
    #     instance.save()
    #     return instance

class CartSerializer(serializers.ModelSerializer):

    menuitem_pk = serializers.PrimaryKeyRelatedField(
        source='MenuItem',
        queryset=MenuItem.objects.all(), 
        write_only=True,
    )
    milk_pk = serializers.PrimaryKeyRelatedField(
        source='Milk',
        queryset=Milk.objects.all(), 
        write_only=True,
    )
    temperature = serializers.CharField()
    
    size = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=5, decimal_places=2)
    quantity = serializers.IntegerField(min_value=0, max_value=6)
    sweetness = serializers.IntegerField(min_value=0, max_value=100)
    

    class Meta:
        model = Cart
        # fields = "__all__"
        fields = ['pk','user_id', 
                  'menuitem_pk', 'menuitem_id', 
                  'milk_pk', 'milk_id',
                  'quantity', 'temperature', 'price', 'size', 'sweetness'
                  ]

    def create(self, validated_data): 
        # Should always return a user since only authenticated user can access ( isAuthenticated)
        print(validated_data)
        user = self.context['request'].user
        menuitem = validated_data.pop('MenuItem')
        milk = validated_data.pop('Milk')
        temperature = validated_data.pop('temperature')
        sweetness = validated_data.pop('sweetness')
        size = validated_data.pop('size')
        quantity = validated_data.pop('quantity')
        price = validated_data.pop('price')

        cartitem_obj, created = Cart.objects.get_or_create(
            menuitem=menuitem, user=user, milk=milk, temperature=temperature, 
            sweetness=sweetness, size=size, quantity=quantity, price=price
        
        )
        
        cartitem_obj.save()
        return cartitem_obj
        
    def update(self, instance, validated_data):
        print(validated_data)
        user = self.context['request'].user
        menuitem = instance.menuitem
        
        try:
            instance.quantity = validated_data.get('quantity', instance.quantity)  
            instance.milk = validated_data.get('Milk', instance.milk)
            instance.temperature = validated_data.get('temperature', instance.temperature)
            instance.sweetness = validated_data.get('sweetness', instance.sweetness)
            instance.size = validated_data.get('size', instance.size)
            instance.save()
            return instance

        except IntegrityError as e:
            print("Item with same spec existed")
            milk = validated_data.get('Milk', instance.milk)
            temperature = validated_data.get('temperature', instance.temperature)
            sweetness = validated_data.get('sweetness', instance.sweetness)
            size = validated_data.get('size', instance.size)
            dup_cartitem =Cart.objects.get(menuitem=menuitem, user=user, milk=milk, temperature=temperature, sweetness=sweetness, size=size)
            
            dup_cartitem.quantity += instance.quantity
            dup_cartitem.save()
            instance.delete()
            
            return dup_cartitem
        

class OrderItemSerializer(serializers.ModelSerializer):   
   
    # menuitem = serializers.PrimaryKeyRelatedField(read_only=True)
    menuitem_pk = serializers.PrimaryKeyRelatedField(
        source='MenuItem',
        queryset=MenuItem.objects.all(), 
        write_only=True,
    )
    # milk = serializers.PrimaryKeyRelatedField(read_only=True)
    milk_pk = serializers.PrimaryKeyRelatedField(
        source='Milk',
        queryset=Milk.objects.all(), 
        write_only=True,
    )

    temperature = serializers.CharField()
    sweetness = serializers.IntegerField(min_value=0, max_value=100)
    size = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=5, decimal_places=2)
    quantity = serializers.IntegerField(min_value=0, max_value=6)
    
    


    class Meta:
        model = OrderItem
        fields = [ 
            'pk', 'menuitem_id', 'menuitem_pk',
            'milk_id', 'milk_pk', 
            'quantity', 'price', 'temperature', 'sweetness', 'size'
            
            ]
    

    
    def update(self, instance, validated_data):
        menuitem = instance.menuitem
        if menuitem.inventory + instance.quantity < validated_data['quantity']:
            raise serializers.ValidationError("oh no There is {} in stock".format(menuitem.inventory))
        
        menuitem.inventory = menuitem.inventory+instance.quantity-validated_data['quantity']
        menuitem.save()

        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
       
        return instance



class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    orderitems = OrderItemSerializer(many=True)
    tip = serializers.DecimalField(max_digits=5, decimal_places=2)
    

    class Meta:
        model = Order
        fields = ['pk', 'user', 'date', 'tip', 'orderitems']



    def create(self, validated_data):
        print('in order serualizer')
        user = self.context['request'].user

        print(validated_data)
    #    {'tip': Decimal('0.75'), 'orderitems': [OrderedDict([('MenuItem', <MenuItem: Jasmine Milk Tea>), ('quantity', 1), ('Milk', <Milk: Whole Milk>)])]}
        orderitems = validated_data.pop('orderitems')
        # print(orderitems)
        # [OrderedDict([('MenuItem', <MenuItem: Boba Black Milk Tea>), ('quantity', 3), ('Milk', <Milk: Soy Milk>)])]
        

        order_obj = Order.objects.create(user=user, date=date.today(), tip=validated_data['tip'])
    
    
        for orderitem in orderitems:
            menuitem = orderitem.pop('MenuItem')
            milk = orderitem.pop('Milk')

            OrderItem.objects.create(order=order_obj, menuitem=menuitem, milk=milk, **orderitem )
            
        order_obj.save()
        return order_obj



    # def update(self, instance, validated_data):
    #     print(validated_data)
    #     instance.order_status = validated_data.get('order_status', instance.order_status)
    #     instance.save()
    #     return instance