from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db.models import Avg
from cloudinary.models import CloudinaryField

# Create your models here.

class Categorie(models.Model):
  sub_category = models.ForeignKey('self',on_delete = models.CASCADE,related_name = 'sub_categories',null=True,blank=True)
  is_sub = models.BooleanField(default=False,null=True,blank=True)
  name = models.CharField(max_length=200,null=True)
  slug = models.SlugField(max_length=200,unique=True)
  def __str__(self):
    return self.name
  
class CreateUserForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['username','email','first_name','last_name','password1','password2']
  
class Product(models.Model):
    category = models.ManyToManyField('Categorie', related_name='product')
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(default=0)
    price_origin = models.FloatField(default=0)
    detail = models.CharField(max_length=1000, null=True)
    image = CloudinaryField('image', blank=True, null=True)
    inventory_quantity = models.IntegerField(default=0, null=True, blank=True)
    purchased_quantity = models.IntegerField(default=0)

    @property
    def remaining_quantity(self):
        return (self.inventory_quantity or 0) - (self.purchased_quantity or 0)

    def __str__(self):
        return self.name or "Unnamed Product"

    @property
    def ImageURL(self):
        """
        Trả về URL của ảnh, tự động fallback về ảnh mặc định nếu chưa có ảnh.
        Dùng được cho Cloudinary và local.
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return 'https://res.cloudinary.com/demo/image/upload/v1690000000/default_product.png'  

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(ratings.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0.0
  
class Order(models.Model):
  customer = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
  date_order = models.DateField(auto_now_add=True)
  complete = models.BooleanField(default=False,null=True,blank=False)
  name = models.CharField(max_length=200,null=True)
  address = models.CharField(max_length=200,null=True)
  numberphone = models.CharField(max_length=12,null=True)
  transaction_id = models.CharField(max_length=200,null=True)
  
  def __str__(self):
    return str(self.id)
  @property
  def get_cart_total(self):
    orderitems = self.orderitem_set.all()
    total = sum([item.get_total for item in orderitems])
    return total
  @property
  def get_cart_items(self):
    orderitems = self.orderitem_set.all()
    total = sum([item.quantity for item in orderitems])
    return total
  
class OrderItem(models.Model):
  product = models.ForeignKey(Product,on_delete=models.CASCADE,blank=True,null=True)
  order = models.ForeignKey(Order,on_delete=models.CASCADE,blank=True,null=True)
  quantity = models.IntegerField(default = 0,null=True,blank=True)
  date_added = models.DateField(auto_now_add=True)
  @property
  def get_total(self):
    total = self.quantity*self.product.price
    return total
   
@receiver(post_delete, sender=OrderItem)
def update_purchased_quantity_on_orderitem_delete(sender, instance, **kwargs):
    if instance.product:
      product = instance.product
      product.purchased_quantity = sum(item.quantity for item in OrderItem.objects.filter(product=product))
      product.save()
@receiver(post_save, sender=OrderItem)
def update_purchased_quantity_on_orderitem_save(sender, instance, **kwargs):
  if instance.product:
    product = instance.product
    product.purchased_quantity = sum(item.quantity for item in OrderItem.objects.filter(product=product))
    product.save()
    
       
class Banner(models.Model):
  image = models.ImageField(null=True,blank=True)
  name = models.CharField(max_length=50,null=True,blank=True)
  detail = models.CharField(max_length=50,null=True,blank=True)
  @property
  def ImageURL(self):
    try:
      url = self.image.url
    except:
      url = ''
    return url

class RecommendId(models.Model):
  productIdRecommend = models.IntegerField()
  
class ProductReview(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  rating = models.PositiveIntegerField(default=1)  # Giá trị từ 1-5 sao
  comment = models.TextField(blank=True, null=True)
  admin_response = models.TextField(blank=True, null=True)  # Phản hồi từ Admin
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.user.username} - {self.product.name}: {self.rating} Stars"

