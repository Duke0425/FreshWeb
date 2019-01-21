import re

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from shopcart.models import ShoppingCart
from user.models import User


class AuthMiddleware(MiddlewareMixin):

    # 拦截请求之前的函数
    # 给request.user属性赋值,赋值为当前登录系统的用户
    def process_request(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            user = User.objects.filter(pk=user_id).first()
            request.user = user
        # 登录校验
        # 如果请求的path为去结算的路由:/order/place_order/
        path = request.path
        if path == '/':
            return None
        not_need_check = ['/user/register/','/user/login/','/user/logout/','/goods/index/', '/goods/detail/.*/','/shopcart/.*/','/goods/list/.*']
        for check_path in not_need_check:
            if re.match(check_path, path):
                # 当前path路径不需要做登录校验的路由
                return None
        # 如果没有user,需要做的登录校验的路由时,跳转到登录
        if not user_id:
            return HttpResponseRedirect(reverse('user:login'))

class SessionToDBMiddleware(MiddlewareMixin):

    def process_response(self, request,response):
        # 同步session中的商品信息和数据库中的购物车信息
        # 1. 判断用户是否登录,登录才做数据同步请求
        user_id = request.session.get('user_id')
        if user_id:
            # 2.同步
            # 2.1 判断session中的商品是否存在于数据库中,则更新
            # 2.2 如果不存在,则创建
            # 2.3 同步数据库的数据到session中
            session_goods = request.session.get('goods')
            if session_goods:
                for se_goods in session_goods:
                    # se_goods结构为[goods_id, num,is_select]
                    cart = ShoppingCart.objects.filter(user_id=user_id,goods_id=se_goods[0]).first()
                    if cart:
                        # 更新商品信息
                        if cart.nums != se_goods[1] or cart.is_select != se_goods[2]:
                            cart.nums = se_goods[1]
                            cart.is_select = se_goods[2]
                            cart.save()
                        # 创建商品信息
                    else:
                        # 组装多个商品的结果[[goods_id, num,is_select],[goods_id, num,is_select],[goods_id, num,is_select]]
                        ShoppingCart.objects.create(user_id=user_id,goods_id=se_goods[0],
                                            nums = se_goods[1],is_select=se_goods[2])

            # 同步数据库中到session中
            db_carts = ShoppingCart.objects.filter(user_id=user_id)
            if db_carts:
                new_session_goods = []
                is_select = 0
                for cart in db_carts:
                    if cart.is_select:
                        is_select = 1
                    data = [cart.goods_id, cart.nums, is_select]
                    new_session_goods.append(data)
                    is_select = 0
                request.session['goods'] = new_session_goods

        return response