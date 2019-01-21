from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

from FreshProject.settings import ORDER_NUMBER
from order.models import OrderInfo, OrderGoods
from shopcart.models import ShoppingCart
from user.models import UserAddress
from utils.functions import get_order_sn


def place_order(request):
    if request.method == 'GET':
        # user_id
        user = request.user
        carts = ShoppingCart.objects.filter(user=user, is_select=True)
        total_price = 0
        for cart in carts:
            # 小计金额
            price = cart.goods.shop_price * cart.nums
            cart.goods_price = price
            # 总金额
            total_price += price
        length = len(carts)

        user_address = UserAddress.objects.filter(user=user)

        return render(request, 'place_order.html',
                      {'carts':carts,'total_price':total_price,'length':length,'user_address':user_address})

def order(request):
    if request.method == 'POST':
        # 1.拿到收货地址id
        ad_id = request.POST.get('ad_id')
        user_address = UserAddress.objects.filter(pk=ad_id).first()
        # 2.创建订单详情
        user_id = request.session.get('user_id')
        # 获取订单号
        order_sn = get_order_sn()
        # 计算总价
        carts = ShoppingCart.objects.filter(user_id=user_id, is_select=True)
        order_mount = 0
        for cart in carts:
            # 总金额
            order_mount += cart.goods.shop_price * cart.nums
        order = OrderInfo.objects.create(user_id=user_id,
                                 order_sn=order_sn,
                                 order_mount=order_mount,
                                 address=user_address.address,
                                 signer_name=user_address.signer_name,
                                 signer_mobile=user_address.signer_mobile)
        # 3.创建订单详情
        for cart in carts:
            OrderGoods.objects.create(order=order,
                                      goods=cart.goods,
                                      goods_nums=cart.nums)
        # 4.删除购物车
        session_goods = request.session.get('goods')
        for se_goods in session_goods[:]:
            if se_goods[2]:
                session_goods.remove(se_goods)
        request.session['goods'] = session_goods
        carts.delete()

        return JsonResponse({'code':200,'msg':'请求成功'})


def user_order(request):
    if request.method == "GET":
        page = int(request.GET.get('page',1))
        user_id = request.session.get('user_id')
        orders = OrderInfo.objects.filter(user_id=user_id)
        status = OrderInfo.ORDER_STATUS
        # 分页配置
        pg = Paginator(orders, ORDER_NUMBER)
        orders = pg.page(page)
        activate = 'order'
        return render(request, 'user_center_order.html', {'orders':orders,'status':status,'activate':activate})