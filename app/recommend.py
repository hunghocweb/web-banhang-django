from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from .models import *

class ContentBasedFiltering:
  def __init__(self, product_queryset):
    self.products = product_queryset
    self.df_product = pd.DataFrame(list(self.products.values()))
    self.df_product['ImageURL'] = [product.ImageURL() for product in self.products]
    self.df_product['combineFeatures'] = self.df_product.apply(self.combine_features, axis=1)

  def combine_features(self, row):
    return str(row['detail'])

  def get_recommendations(self, product_id, num_recommendations=5):
    tf = TfidfVectorizer()
    tf_matrix = tf.fit_transform(self.df_product['combineFeatures'])
    similar = cosine_similarity(tf_matrix)
    similar_products = list(enumerate(similar[product_id - 1]))
    sorted_similar_products = sorted(similar_products, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i in range(1, min(num_recommendations + 1, len(sorted_similar_products))):
      product_dict = {
        'id': int(self.df_product.iloc[sorted_similar_products[i][0]]['id']),
        'name': str(self.df_product.iloc[sorted_similar_products[i][0]]['name']),
        'ImageURL': str(self.df_product.iloc[sorted_similar_products[i][0]]['ImageURL']),
        'price': float(self.df_product.iloc[sorted_similar_products[i][0]]['price']),
      }
      recommendations.append(product_dict)

    return recommendations

def CollaborativeFiltering(userId):
  """
  Tính điểm gợi ý cho tất cả sản phẩm dựa trên Collaborative Filtering.
  userId: ID của người dùng hiện tại.
  """
  allProducts = Product.objects.values_list('id', flat=True)
  # Lấy tất cả đánh giá
  reviews = ProductReview.objects.all().values('user_id', 'product_id', 'rating')
  reviewDataFrame = pd.DataFrame(reviews)
  
  # Tạo ma trận người dùng - sản phẩm
  userProductMatrix = reviewDataFrame.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)

  # Tính ma trận tương đồng người dùng
  userSimilarity = cosine_similarity(userProductMatrix)
  similarityDataFrame = pd.DataFrame(userSimilarity, index=userProductMatrix.index, columns=userProductMatrix.index)
  if userId not in similarityDataFrame.index:
    # Trường hợp hiếm khi user vừa đăng ký nhưng chưa rating
    return pd.Series(0.0, index=allProducts)
  # Lấy người dùng tương tự
  similarUsers = similarityDataFrame[userId].sort_values(ascending=False).drop(userId)

  # Tích lũy điểm gợi ý cho từng sản phẩm
  productScores = pd.Series(0, index=userProductMatrix.columns)
  for similarUserId, similarityScore in similarUsers.items():
    productScores += similarityScore * userProductMatrix.loc[similarUserId]

  # Loại bỏ sản phẩm mà user đã đánh giá
  userRatedProducts = userProductMatrix.loc[userId]
  productScores[userRatedProducts > 0] = 0

  # Đảm bảo tất cả sản phẩm đều có mặt trong danh sách (với điểm mặc định là 0 nếu không có điểm gợi ý)
  productScores = productScores.reindex(allProducts, fill_value=0)

  return productScores.sort_values(ascending=False)


