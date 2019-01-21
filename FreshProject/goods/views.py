from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from goods.models import GoodsCategory, Goods
from user.models import User


def index(request):
    """
    首页渲染
    :param request:
    :return:
    """
    if request.method == 'GET':
        # 商品的全部种类
        cate = GoodsCategory.objects.all()
        # 全部商品
        goods = Goods.objects.all()
        category_type = GoodsCategory.CATEGORY_TYPE
        # 如果访问页面,返回渲染的首页index.html页面
        # user = User.objects.all()
        return render(request, 'index.html', {'cate': cate, 'goods':goods, 'category_type':category_type})

def detail(request, id):
    """
    单个商品详情
    :param request:
    :param id:
    :return:
    """
    if request.method == 'GET':
        goods = Goods.objects.filter(pk=id).first()
        new = Goods.objects.filter(is_new=1,category_id=goods.category_id)[:2]

        click_list = [goods.id, 1]
        click = request.session.get('click')
        # click :[[goods.id,1],[goods.id,1],[goods.id,1],[goods.id,1]]
        flag = True
        if click:
            for se_click in click:
                if se_click[0] == goods.id:
                    se_click[0] += 1
                    flag = False
            if flag:
                click.append(click_list)
                request.session['click'] = click
        else:
            request.session['click'] = [click_list]
        return render(request, 'detail.html',{'goods':goods,'new':new})


def list(request,id):
    """
    商品
    :param request:
    :param id:
    :return:
    """
    if request.method == 'GET':
        page = int(request.GET.get('page',1))
        if id == 0:
            goods = Goods.objects.all()
            cate=[]
            category_type = GoodsCategory.CATEGORY_TYPE
            new = Goods.objects.filter(is_new=1)[:4]
        else:
            goods = Goods.objects.filter(category_id=id)
            cate = GoodsCategory.objects.filter(pk=id).first()
            category_type = GoodsCategory.CATEGORY_TYPE
            new = Goods.objects.filter(is_new=1,category_id=id)
        pg = Paginator(goods,20)
        goods = pg.page(page)
        return render(request, 'list.html',{'goods':goods, 'cate':cate,'category_type':category_type,'new':new})
