from django.contrib.admin import AdminSite
from django.contrib import admin
from.models import *
from django.contrib.auth.models import User, Group


class MyAdminSite(AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        # Lấy danh sách sản phẩm cần bổ sung
        products = Product.objects.all()
        low_stock_products = [item.name for item in products if item.remaining_quantity <= 3]
        # Thêm low_stock_products vào context
        context['low_stock_products'] = low_stock_products
        return context

# Khởi tạo AdminSite tùy chỉnh
admin_site = MyAdminSite(name='myadmin')

class ProductAdmin(admin.ModelAdmin):
    # Các trường hiển thị trong danh sách
    list_display = ('id', 'name', 'price', 'inventory_quantity', 'purchased_quantity', 'remaining_quantity')

    # Các trường chỉ đọc trong form chỉnh sửa
    readonly_fields = ('remaining_quantity', 'purchased_quantity')

    # Dùng phương thức để hiển thị remaining_quantity
    def remaining_quantity(self, obj):
        return obj.remaining_quantity
    remaining_quantity.short_description = 'Remaining Quantity'

# Đăng ký model OrderItem với list_display
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity','total', 'date_added')
    def total(self, obj):
        return obj.get_total
    total.short_description = 'total'
    
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name' , 'detail')

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at', 'admin_response')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    fields = ('product', 'user', 'rating', 'comment', 'admin_response', 'created_at')
    readonly_fields = ('created_at',)


# Register your models here.
admin_site.register(Product, ProductAdmin)
admin_site.register(Categorie)
admin_site.register(Order)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(Banner,BannerAdmin)
admin_site.register(ProductReview, ProductReviewAdmin)
# Đăng ký User và Group vào admin tùy chỉnh
admin_site.register(User)
admin_site.register(Group)