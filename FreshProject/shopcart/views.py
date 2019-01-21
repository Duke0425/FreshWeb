from django.http import JsonResponse
from django.shortcuts import render

from goods.models import Goods
from shopcart.models import ShoppingCart


def add_cart(request):
    if request.method == 'POST':
        # 接收商品id值和商品数量num
        # 组装存储的商品格式:[goods_id,num,is_select]
        # 组装多个商品格式:[[goods_id,num,is_select],[goods_id,num,is_select],[goods_id,num,is_select]]
        goods_id = int(request.POST.get('goods_id'))
        goods_num = int(request.POST.get('goods_num'))
        goods_list = [goods_id,goods_num,1]

        session_goods = request.session.get('goods')
        if session_goods:

            #   1. 添加重复的商品,则修改
            flag = True
            for se_goods in session_goods:
                if se_goods[0] == goods_id:
                    se_goods[1] += goods_num
                    flag = False
            if flag:
                # 2.添加的商品不存在购物车中
                session_goods.append(goods_list)
            request.session['goods'] = session_goods
            count = len(session_goods)
            return JsonResponse({'code':200, 'msg':'请求成功','count':count})
        else:
            # 第一次添加购物车, 需组装购物车中的商品格式为[[goods_id,num,is_select]]
            request.session['goods'] = [goods_list]
            count = 1
            return JsonResponse({'code': 200, 'msg': '请求成功', 'count': count})


def cart(request):
    """
    购物车页面

    :param request:
    :return:
    """
    if request.method == 'GET':

        session_goods = request.session.get('goods')
        # objects = [goods , num , is_delete, total_price]
        result = []
        if session_goods:
            for s_goods in session_goods:
                goods = Goods.objects.filter(pk=s_goods[0]).first()
                total_price = goods.shop_price * s_goods[1]
                data = [goods,s_goods[1],s_goods[2],total_price]
                result.append(data)
        return render(request, 'cart.html',{'result': result})


def cart_num(request):
    if request.method == 'GET':
        session_goods = request.session.get('goods')
        count = len(session_goods) if session_goods else 0
        return JsonResponse({'code':200, 'msg':'请求成功','count':count})


def cart_price(request):
    """
    计算购物车价格

    :param request:
    :return:
    """
    if request.method == 'GET':
        session_goods = request.session.get('goods')
        all_total = len(session_goods)
        all_price = 0
        is_select_num = 0
        for sgoods in session_goods:
            # se_goods为[goods_id, num, is_select]
            if sgoods[2]:
                goods = Goods.objects.filter(pk=sgoods[0]).first()
                total_price = goods.shop_price * sgoods[1]
                all_price += total_price
                is_select_num += 1


        return JsonResponse({'code': 200, 'msg': '请求成功',
                             'all_total':all_total,
                             'all_price':all_price,
                             'is_select_num':is_select_num})

def change_cart(request):
    if request.method == 'POST':
        # 修改商品的数量和选择状态
        # 修改se_goods为[goods_id, num, is_select]
        # 1.获取商品id值和(数量或选择状态)

        goods_id = int(request.POST.get('goods_id'))
        goods_num = request.POST.get('goods_num')
        goods_select = request.POST.get('goods_select')

        # 修改
        session_goods = request.session.get('goods')
        for sgoods in session_goods:
            if goods_id == sgoods[0]:
                    sgoods[1] = int(goods_num)if goods_num else sgoods[1]
                    if goods_select:
                        if goods_select == '1':
                            sgoods[2] = 0
                        else:
                            sgoods[2] = 1


        request.session['goods'] = session_goods

        return JsonResponse({'code':200,'msg':'请求成功'})


def del_cart(request):
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        all_goods = request.session.get('goods')

        for s_goods in all_goods:
            if int(goods_id) == s_goods[0]:
                all_goods.remove(s_goods)
                break
        request.session['goods'] = all_goods
        # 删除数据库
        user_id = request.session.get('user_id')
        if user_id:
            ShoppingCart.objects.filter(user_id=user_id,goods_id=goods_id).delete()
        return JsonResponse({'code':200,'msg':'请求成功'})

