from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .serializers import *
from storeapp.models import *
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from .filter import *
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings

# Create your views here.
import stripe


stripe.api_key = settings.STRIPE_SECERET_KEY


def initiate_payment(amount, email, order_id):
    try:
        # إنشاء جلسة الدفع في Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    # استبدلها بالعملة المطلوبة
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Supa Electronics Store',
                        'description': 'Best store in town',
                    },
                    # المبلغ الأساسي (عادة بالسنت أو الوحدة الأقل للعملة)
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            metadata={
                'order_id': order_id,
            },
            customer_email=email,
            mode='payment',
            success_url=f'http://127.0.0.1:8000/api/orders/{order_id}/success_payment/',
        )

        # إرجاع رابط جلسة الدفع كاستجابة من Django REST framework
        return Response({'session_url': session.url})

    except Exception as e:
        print(f'Error creating Stripe session: {e}')
        return Response({'error': str(e)}, status=500)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name','description']
    ordering_fields=['old_price']
    pagination_class=PageNumberPagination


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(ModelViewSet):
    # queryset=Review.objects.all()
    serializer_class=ReviewSerializer
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    

class CartsViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset=Cart.objects.all()
    serializer_class=CartSerializer


class CartItemViewSet(ModelViewSet):
    # serializer_class=CartItemSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return Cartitems.objects.filter(cart_id=self.kwargs['cart_pk'])

class OrderViewSet(ModelViewSet):
    queryset=Order.objects.all()
    # serializer_class=OrderSerializers
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def pay(self,request,pk):
        order=self.get_object()
        amount=order.total_price
        email=request.user.email
        order_id=str(order.id)
        return initiate_payment(amount, email, order_id)
    
    @action(detail=True, methods=['get'])
    def success_payment(self,request,pk=None):
        order=self.get_object()
        order.pending_status = Order.PAYMENT_STATUS_COMPLETE
        order.save()
        serializer = OrderSerializers(order)
        data={
            'msg': 'Payment Successful..',
            'data':serializer.data
    
        }
        return Response(data)


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializers
    
    def get_serializers_context(self):
        return{'user_id':self.request.user.id}

    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(owner=user)


class ProfileViewSet(ModelViewSet):
    queryset=Profile.objects.all()
    serializer_class=ProfileSerializer
    parser_classes = (MultiPartParser,FormParser)
    def create(self, request, *args, **kwargs):
        name=request.data['name']
        bio=request.data['bio']
        image=request.data['image']

        Profile.objects.create(name=name,bio=bio,image=image)
        return Response('Profile Created Successfully..',status=HTTP_201_CREATED)       




