from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# from django.core.exceptions import ValidationError

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)
    desc = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self)-> str:
        return self.title
    
class Milk(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    # for serializers.StringRelatedField to display string
    def __str__(self)-> str:
        return self.title


    
class MenuItem(models.Model):      
    TEMP_CHOICES = {
        "H":"Hot",
        "I":"Iced",
    }
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    
    temperature = models.CharField(max_length=1, choices=TEMP_CHOICES, blank=True)
    milk = models.ForeignKey(Milk, on_delete=models.PROTECT, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    

    def __str__(self):
        return self.title


class Cart(models.Model):
    #  {menuitem_id:7, quantity:1, temperature:"Iced", size:16, milkId:3, sweet:50, price:7}

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveSmallIntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    milk = models.ForeignKey(Milk, on_delete=models.PROTECT, null=True, blank=True)
    temperature = models.CharField(max_length=1, default='I')
    # sweetness = models.CharField(max_length=3, default='100')
    sweetness = models.IntegerField(null=False, default=0)
    size = models.IntegerField(null=False, default=12)
    

    class Meta: 
        unique_together = ('menuitem', 'user','temperature', 'size', 'sweetness', 'milk')

    
class Order(models.Model):
    # STATUS_CHOICES = {
    #     "R":"Received",
    #     "P":"Processing",
    #     "S": "Served"
    # }
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    # order_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="R")
    
 
    date = models.DateField(db_index=True, null=True, blank=True)
    tip = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    # total = models.DecimalField(decimal_places=2, max_digits=5, default=0)
 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='orderitems', on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    milk = models.ForeignKey(Milk, on_delete=models.PROTECT, null=True, blank=True)
    temperature = models.CharField(max_length=1, default='I')
    size = models.IntegerField(null=False, default=12)
    sweetness = models.IntegerField(null=False, default=0)
    
    quantity = models.PositiveSmallIntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    class Meta:
        unique_together = ('order', 'menuitem', 'milk', 'temperature', 'size', 'sweetness')

