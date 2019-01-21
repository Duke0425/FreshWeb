
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from goods.models import Goods
from user.forms import RegisterForm, LoginForm, AddressForm
from user.models import User, UserAddress


def register(request):
    """
    注册用户
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 账号不存在于数据库，密码和确认密码一致，邮箱格式正确
            username = form.cleaned_data['user_name']
            password = make_password(form.cleaned_data['pwd'])
            email = form.cleaned_data['email']
            User.objects.create(username=username,
                                password=password,
                                email=email)
            return HttpResponseRedirect(reverse('user:login'))
        else:
            # 获取表单验证不通过的错误信息
            errors = form.errors
            return render(request, 'register.html', {'errors': errors})
        pass

def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # 用户名存在，密码相同
            username = form.cleaned_data['username']
            user = User.objects.filter(username=username).first()
            request.session['user_id'] = user.id
            return HttpResponseRedirect(reverse('goods:index'))
        else:
            errors = form.errors
            return render(request, 'login.html', {'errors': errors})

def logout(request):
    """
    用户退出
    :param request:
    :return:
    """
    if request.method == 'GET':
        del request.session['user_id']
        if request.session.get('click'):
            click = request.session['click']
            for se_click in click:
                goods = Goods.objects.filter(pk=se_click[0]).first()
                goods.click_nums += se_click[1]
                goods.save()
            del request.session['click']
        if request.session.get('goods'):
            del request.session['goods']
        return HttpResponseRedirect(reverse('goods:index'))

def user_site(request):
    """
    用户地址
    :param request:
    :return:
    """
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        user_address = UserAddress.objects.filter(user_id=user_id)
        activate = 'site'
        return render(request, 'user_center_site.html',{'user_address':user_address, 'activate':activate})

    if request.method == 'POST':
        form = AddressForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            address = form.cleaned_data.get('address')
            mobile = form.cleaned_data.get('mobile')
            postcode = form.cleaned_data.get('postcode')
            user_id = request.session.get('user_id')
            UserAddress.objects.create(user_id=user_id,
                                       address=address,
                                       signer_name=username,
                                       signer_mobile=mobile,
                                       signer_postcode=postcode)
            return HttpResponseRedirect(reverse('user:user_site'))
        else:
            errors = form.errors
            return render(request, 'user_center_site.html', {'errors': errors})

def user_info(request):
    """
    用户基本信息
    :param request:
    :return:
    """
    if request.method == 'GET':
        activate = 'info'
        user_id = request.session.get('user_id')
        user_address = UserAddress.objects.filter(user_id=user_id).first()
        click = request.session.get('click')
        click_goods = []
        if click:
            for se_click in click:
                goods = Goods.objects.filter(pk=se_click[0]).first()
                click_goods.append(goods)
            click_goods = click_goods[-5:]
        return render(request, 'user_center_info.html', {'activate':activate,'user_address':user_address,'click':click_goods})