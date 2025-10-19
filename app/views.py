import os
import json
import logging
import threading
import requests
import google.generativeai as genai
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import (
  Sum, F, CharField, Func, ExpressionWrapper, FloatField,
  Value, Avg, DateField, Window
)
from django.db.models.functions import (
  TruncDate, TruncWeek, TruncMonth, TruncYear,
  ExtractWeek, ExtractYear, Concat, DenseRank
)
from datetime import datetime, timedelta
from .models import Product
from .utils import send_email
from .recommend import *
from apscheduler.schedulers.background import BackgroundScheduler

# Cấu hình logging để debug dễ hơn
logging.basicConfig(level=logging.INFO)

# Lấy API Key từ biến môi trường
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
  logging.error("API Key của Gemini chưa được thiết lập!")
  raise ValueError("API Key của Gemini chưa được thiết lập!")

genai.configure(api_key=GEMINI_API_KEY)

# Cấu hình mô hình Gemini
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

# Khởi tạo model Gemini
model = genai.GenerativeModel(
  model_name="gemini-2.5-flash",
  generation_config=generation_config,
)

# Hàm xử lý yêu cầu chatbot
def chatbot_response(request):
  try:
    # Kiểm tra phương thức request
    if request.method != "POST":
      return JsonResponse({"error": "Invalid request method"}, status=405)

    # Lấy danh sách sản phẩm từ database
    list_product = []
    products = Product.objects.all()

    for product in products:
      list_product.append({
        "name": product.name,
        "category": [category.name for category in product.category.all()] if product.category.exists() else [],
        "price": product.price,
        "detail": product.detail
      })

    list_product_json = json.dumps(list_product)

    # Lấy tin nhắn từ người dùng
    message_input = request.POST.get("message", "").strip()

    if not message_input:
      return JsonResponse({"error": "Tin nhắn không được để trống."}, status=400)

    # Thêm vào prompt chính
    message_input += " tại cửa hàng của bạn."

    message_assistant = f"""Bạn là một trợ lý ảo bán hàng.
    Danh sách sản phẩm trong cửa hàng: {list_product_json}.
    - Không gợi ý sản phẩm nằm ngoài danh sách.
    - Chỉ tư vấn sản phẩm có trong danh sách trên.
    - Đơn vị tiền tệ là USD.
    - Gợi ý sản phẩm gần giống nhất khi khách hàng hỏi sai tên.
    - Xưng em thay vì chúng tôi
    - Trả lời tin nhắn dạng html.
    """

    # Bắt đầu một phiên chat với Gemini
    chat_session = model.start_chat(history=[])

    # Gửi tin nhắn đến Gemini
    response = chat_session.send_message(message_assistant)
    response = chat_session.send_message(message_input)

    # Kiểm tra phản hồi từ Gemini
    chatbot_reply = response.text.strip() if response.text else "Xin lỗi, tôi không hiểu câu hỏi của bạn."

    return JsonResponse({"reply": chatbot_reply})

  except requests.exceptions.RequestException as e:
    logging.error(f"Lỗi kết nối API: {e}")
    return JsonResponse({"reply": "Lỗi khi kết nối đến Gemini API.", "error": str(e)}, status=500)
  except Exception as e:
    logging.error(f"Lỗi không mong muốn: {e}")
    return JsonResponse({"reply": "Đã xảy ra lỗi không mong muốn.", "error": str(e)}, status=500)

def rate_product(request, product_id):
  if request.method == 'POST':
    # Lấy thông tin từ form
    rating = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '')

    # Tìm sản phẩm
    product = get_object_or_404(Product, id=product_id)

    # Kiểm tra xem người dùng đã đánh giá sản phẩm này chưa
    review, created = ProductReview.objects.get_or_create(
      product=product,
      user=request.user,
      defaults={'rating': rating, 'comment': comment}
    )
    if not created:
      # Cập nhật đánh giá nếu đã tồn tại
      review.rating = rating
      review.comment = comment
      review.save()
      messages.success(request, "Đánh giá của bạn đã được cập nhật.")
    else:
      # Thêm thông báo nếu đây là đánh giá mới
      pass

    # Chuyển hướng trở lại trang chi tiết sản phẩm
    return redirect(f'/detail_page/?id={product_id}')
  
  # Nếu không phải phương thức POST, chuyển hướng về trang chi tiết
  return redirect(f'/detail_page/?id={product_id}')

def detail_page(request):
  quantity = 0
  id = request.GET.get('id', '')
  product = Product.objects.get(id=id)

  # Lấy sản phẩm tương tự
  products = Product.objects.filter(category__in=product.category.all()).exclude(id=product.id).distinct()[:5]

  # Lấy loại sản phẩm
  product_category = product.category.all()
  categories = Categorie.objects.filter(is_sub=False)

  # Lấy thông tin giỏ hàng
  if request.user.is_authenticated:
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
  else:
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = order['get_cart_items']

  for i in items:
    if i.product.id == product.id:
      quantity = i.quantity

  # Lấy danh sách đánh giá sản phẩm
  ratings = ProductReview.objects.filter(product=product)

  # Tính trung bình đánh giá
  average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

  context = {
    'products': products,
    'product': product,
    'quantity': quantity,
    'order': order,
    'cartItems': cartItems,
    'categories': categories,
    'product_category': product_category,
    'ratings': ratings,
    'average_rating': average_rating,
  }

  return render(request, 'app/detail.html', context)

def category(request):
  categories = Categorie.objects.filter(is_sub = False)
  active_category = request.GET.get('category','')
  product_type = Categorie.objects.filter(slug = active_category)[0]
  if active_category:
    products = Product.objects.filter(category__slug = active_category)
  if request.user.is_authenticated:
    customer = request.user
    order, created = Order.objects.get_or_create(customer = customer,complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
  else:
    items = []
    order = {'get_cart_total':0,'get_cart_items':0}
    cartItems = order['get_cart_items']
  context ={'categories':categories,'active_category':active_category,'products':products,'cartItems':cartItems,'product_type':product_type}
  return render(request,'app/category.html',context)

def search(request):
    searched = ""
    keys = Product.objects.none()
    group_price = 0  # Default value

    if request.method == "POST":
        searched = request.POST.get("searched", "")
        filter_price = request.POST.get("filter_price", "default")

        # Filter products based on the statistic type
        if filter_price == "less_50":
            group_price = 50
            keys = Product.objects.filter(name__icontains=searched, price__lt=50)
        elif filter_price == "less_100":
            group_price = 100
            keys = Product.objects.filter(name__icontains=searched, price__lt=100)
        elif filter_price == "less_150":
            group_price = 150
            keys = Product.objects.filter(name__icontains=searched, price__lt=150)
        elif filter_price == "less_200":
            group_price = 200
            keys = Product.objects.filter(name__icontains=searched, price__lt=200)
        else:
            keys = Product.objects.filter(name__icontains=searched)

    # Handle cart data
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    # Fetch all products and categories
    products = Product.objects.all()
    categories = Categorie.objects.filter(is_sub=False)

    context = {
        'searched': searched,
        'keys': keys,
        'products': products,
        'cartItems': cartItems,
        'categories': categories,
        'group_price': group_price,
    }

    return render(request, 'app/search.html', context)

def register(request):
  form = CreateUserForm()
  if request.method == "POST":
    form = CreateUserForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('login')
  context = {'form': form}
  return render(request,'app/register.html',context)

def loginPage(request):
  if request.user.is_authenticated:
    return redirect('home')
  if request.method == "POST":
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request,username=username,password=password)
    if user is not None:
      login(request,user) 
      return redirect('home')
    else: messages.info(request,'User or password not correct')
  context = {}
  return render(request,'app/login.html',context)

def logoutPage(request):
  logout(request)
  return redirect('login')

def combineFeatures(row):
  return str(row['price']) + " " + str(row['detail'])

def home(request):
  # Kiểm tra người dùng đã đăng nhập
  if request.user.is_authenticated:
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cartItems = order.get_cart_items
     # Lấy điểm gợi ý cho user hiện tại
    productScores = CollaborativeFiltering(userId=request.user.id)

    # Tạo danh sách ID sản phẩm theo thứ tự điểm gợi ý
    productIds = list(productScores.index)

    # Lấy tất cả sản phẩm và sắp xếp theo danh sách ID
    allProducts = Product.objects.filter(id__in=productIds)
    products = sorted(allProducts, key=lambda p: productIds.index(p.id))
  else:
    cartItems = 0
    products = Product.objects.all()
  products_recommend = Product.objects.all()
  # Lấy dữ liệu cho banner, sản phẩm, và danh mục
  banners = Banner.objects.all()[:3]
  categories = Categorie.objects.filter(is_sub=False)
  recommend_record = RecommendId.objects.first()
  if not recommend_record:
    recommend_record = RecommendId.objects.create(productIdRecommend=1)

  productId = recommend_record.productIdRecommend

  # Sử dụng ContentBasedFiltering để gợi ý sản phẩm
  cb_filter = ContentBasedFiltering(products_recommend)
  recommended_products = cb_filter.get_recommendations(productId, num_recommendations=5)

  # Render trang với context
  context = {
    'products': products,
    'cartItems': cartItems,
    'categories': categories,
    'banners': banners,
    'recommended_products': recommended_products,
  }
  return render(request, 'app/home.html', context)

def cart(request):
  if request.user.is_authenticated:
    customer = request.user
    order, created = Order.objects.get_or_create(customer = customer,complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
  else:
    items = []
    order = {'get_cart_total':0,'get_cart_items':0}
    cartItems = order['get_cart_items']
  categories = Categorie.objects.filter(is_sub = False)
  context= {'items':items,'order':order,'cartItems':cartItems,'categories': categories}
  return render(request,'app/cart.html', context)

def checkout(request):
  if request.user.is_authenticated:
    customer = request.user
    order, created = Order.objects.get_or_create(customer = customer,complete=False)
    items = order.orderitem_set.all()
    id_item = [item.product.id for item in items]
    cartItems = order.get_cart_items
  else:
    items = []
    order = {'get_cart_total':0,'get_cart_items':0}
    cartItems = order['get_cart_items']
  categories = Categorie.objects.filter(is_sub = False)
  context= {'items':items,'order':order,'cartItems':cartItems,'categories': categories}
  # thanhtoan
  if request.method == "POST":
    name = request.POST.get("name", "").strip()
    address = request.POST.get("address", "").strip()
    try:
        mobile = int(request.POST.get("mobile", "").strip())
    except ValueError:
        context['error'] = "Số điện thoại không hợp lệ. Vui lòng nhập một số hợp lệ."
        return render(request, 'app/checkout.html', context)
    identify = request.POST.get("identify", "").strip()

    # Kiểm tra nếu bất kỳ trường nào bị bỏ trống
    if not name or not address or not mobile or not identify:
      context['error'] = "Vui lòng điền đầy đủ thông tin trước khi thanh toán!"
      return render(request, 'app/checkout.html', context)
    if mobile<0 or mobile>=1000000000000:
      context['error'] = "Sai số điện thoại"
      return render(request, 'app/checkout.html', context)
    # Thực hiện lưu vào cơ sở dữ liệu hoặc xử lý thêm
    # ...
    order.name = name
    order.address = address
    order.numberphone = mobile
    order.transaction_id = identify
    order.complete =True
    threading.Thread(target=send_email, args=(customer.email, id_item)).start()
    order.save()
    response =  '''<script type="text/javascript">alert("Thông tin thanh toán đã được xử lý thành công!");window.location.href = '/checkout/';</script>'''
    return HttpResponse(response)
  return render(request,'app/checkout.html', context)

def updateItem(request):
  data = json.loads(request.body)
  productId = data['productId']
  action = data['action']
  customer = request.user
  product = Product.objects.get(id=productId)
  Recommend = RecommendId.objects.first()
  # Cập nhật purchased_quantity trước khi kiểm tra
  product.purchased_quantity = sum(item.quantity for item in OrderItem.objects.filter(product=product))
  product.save()

  # Lấy hoặc tạo đơn hàng
  order, created = Order.objects.get_or_create(customer=customer, complete=False)
  orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

  if action =='watch':
    Recommend.productIdRecommend = productId
    Recommend.save()
  if action == 'add':
    Recommend.productIdRecommend = productId
    Recommend.save()
    if product.remaining_quantity > 0:
      orderItem.quantity += 1
      product.purchased_quantity += 1
      product.save()
    else:
      return JsonResponse({'error': 'Hết hàng rồi'}, status=400)
  elif action == 'remove':
    orderItem.quantity -= 1
    product.purchased_quantity -= 1
    product.save()
  orderItem.save()
  if orderItem.quantity <= 0:
    orderItem.delete()
  return JsonResponse({'message': 'Cập nhật thành công'}, safe=False)

def contact(request):
  categories = Categorie.objects.filter(is_sub = False)
  context= {'categories': categories}
  return render(request, 'app/contact.html',context)

def introduce(request):
  categories = Categorie.objects.filter(is_sub = False)
  context= {'categories': categories}
  return render(request, 'app/introduce.html',context)
# Chỉ cho phép nhân viên hoặc admin truy cập
def manage(request):
  return render(request, 'admin/base_site.html')

# format date
class DateFormat(Func):
  function = 'DATE_FORMAT'
  template = "%(function)s(%(expressions)s, '%(format)s')"
  output_field = CharField()

  def __init__(self, expression, format, **extra):
    super().__init__(expression, format=format, **extra)

def statistic(request):
  #----------------------------------------statistic sales------------------------------------------
  
  # Default to showing last 30 days of data
  end_date = datetime.now().date()
  start_date = end_date - timedelta(days=30)
  
  # Default to daily statistics
  group_by = 'day'

  if request.method == "POST":
    # Get date range from form
    start_date_str = request.POST.get('date-start')
    end_date_str = request.POST.get('date-end')
    group_by = request.POST.get('statistic-type', 'day')

    # Convert string dates to datetime objects
    if start_date_str:
      start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    if end_date_str:
      end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

  # Perform statistics based on grouping
  if group_by == 'day':
    statistics = (
      OrderItem.objects
      .filter(date_added__range=[start_date, end_date])
      .annotate(date=TruncDate('date_added', output_field=DateField()))
      .annotate(date_str=DateFormat('date_added', '%%d/%%m'))
      .values('date_str')
      .annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
      )
      .order_by('date')
    )
  elif group_by == 'week':
    # Group by week
    statistics = (
      OrderItem.objects
      .filter(date_added__range=[start_date, end_date])
      .annotate(
        week=ExtractWeek('date_added'),  # Lấy số tuần
        year=ExtractYear('date_added')  # Lấy năm
      )
      .annotate(
        week_str=Concat(
          Value('Tuần '), F('week'), Value(' - Năm '), F('year'),
          output_field=CharField()
        )
      )
      .values('week_str')  # Nhóm theo chuỗi định dạng tuần
      .annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
      )
      .order_by('year', 'week')  # Sắp xếp theo năm và tuần
    )
  elif group_by == 'month':
    # Group by month
    statistics = (
      OrderItem.objects
      .filter(date_added__range=[start_date, end_date])
      .annotate(month=TruncMonth('date_added', output_field=DateField()))
      .annotate(month_str=DateFormat('date_added', '%%m/%%Y'))
      .values('month_str')
      .annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
      )
      .order_by('month')
    )
  else:  # year
    # Group by year
    statistics = (
      OrderItem.objects
      .filter(date_added__range=[start_date, end_date])
      .annotate(year=TruncYear('date_added', output_field=DateField()))
      .annotate(year_str=DateFormat('date_added', '%%Y'))
      .values('year_str')
      .annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('product__price'))
      )
      .order_by('year')
    )

  #--------------------------------------statistic bestselling--------------------------------------
  
  # Tổng số lượng sản phẩm đã bán
  orders = Order.objects.filter(complete=True)
  orderItems = OrderItem.objects.filter(order__in=orders)
  sum_quantity = orderItems.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
  # Lọc danh sách sản phẩm bán chạy với số lượng >= 5
  bestSellings = (
    orderItems
    .values('product__name')  # Nhóm theo tên sản phẩm
    .annotate(
        total_quantity=Sum('quantity'),  # Tổng số lượng bán
    )
    .filter(total_quantity__gte=5)  # Chỉ lấy sản phẩm có số lượng >= 5
    .annotate(
        percent_quantity=ExpressionWrapper(
            F('total_quantity') * 100 / Value(sum_quantity),
            output_field=FloatField()
        ) if sum_quantity > 0 else Value(0)  # Tính tỷ lệ phần trăm
    )
    .order_by('-total_quantity')  # Sắp xếp giảm dần theo số lượng
  )
  
  context = {
    'bestSellings': list(bestSellings),
    'statistics': list(statistics),
    'start_date': start_date,
    'end_date': end_date,
    'group_by': group_by
  }
  return render(request, 'app/statistic.html', context)
