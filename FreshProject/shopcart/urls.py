from django.urls import path, include, re_path

from shopcart import views

urlpatterns = [
    # 加入购物车
    path('add_cart/', views.add_cart, name='add_cart'),
    # 购物车
    path('cart/', views.cart, name='cart'),
    # 购物车数量的刷新
    path('cart_num/', views.cart_num, name='cart_num'),
    # 购物车计算价格
    path('cart_price/', views.cart_price, name='cart_price'),
    # 改变购物车商品数量
    path('change_cart/', views.change_cart, name='change_cart'),
    # 删除购物车商品
    path('del_cart/', views.del_cart, name='del_cart'),


]