from django.urls import path,include
from .views import *
# from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
# router= DefaultRouter()
router=routers.DefaultRouter()
router.register('products',ProductViewSet)
router.register('categories',CategoryViewSet)
router.register('carts',CartsViewSet)
router.register('profiles',ProfileViewSet)
router.register('orders',OrderViewSet,basename='orders')
router_product=routers.NestedDefaultRouter(router,'products',lookup='product')
router_product.register('reviews',ReviewViewSet,basename='reviews-list')
router_cart=routers.NestedDefaultRouter(router,'carts',lookup='cart')
router_cart.register('items',CartItemViewSet,basename='cart_items')


urlpatterns = router.urls

urlpatterns = [
    path('',include(router.urls)),
    path('', include(router_product.urls)),
    path('', include(router_cart.urls)),
]

# urlpatterns = [
#     path('products/', ApiProducts.as_view()),
#     # path('products/', api_products),
#     path('products/<str:pk>', ApiProduct.as_view()),
#     # path('products/<str:pk>', api_product),
#     path('categories/', ApiCategories.as_view()),
#     # path('categories/', api_categories),
#     path('categories/<str:pk>', ApiCategory.as_view()),
#     # path('categories/<str:pk>', api_category),
# ]
