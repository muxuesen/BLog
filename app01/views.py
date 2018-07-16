from django.shortcuts import render,redirect,HttpResponse
from django.contrib import auth
from app01.models import Article,UserInfo,Tag,Category,Comment,ArticleUpDown,Article2Tag
from django.db.models import Count
# Create your views here.
def login(request):
    if request.method=="POST":
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        user = auth.authenticate(username=user,password=pwd)
        if user:
            auth.login(request,user)
            return redirect("/index/")
    return render(request,"login.html")

def index(request):
    article_list = Article.objects.all()

    return render(request,"index.html",{"article_list":article_list})

def logout(request):
    auth.logout(request)
    return redirect("/index/")

def homesite(request,username,**kwargs):
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request,"not_found.html")

    blog = user .blog

    if not kwargs:
        article_list = Article.objects.filter(user__username=username)
    else:
        condition = kwargs.get("condition")
        params = kwargs.get("params")

        if condition == "category":
            article_list = Article.objects.filter(user__username=username).filter(category__title=params)
        elif condition == "tag":
            article_list = Article.objects.filter(user__username=username).filter(tags__title=params)
        else:
            year, month = params.split("/")

            article_list = Article.objects.filter(user__username=username).filter(create_time__year=year)
                                                                                  # create_time__month=month)


    # 查询当前站点每一个分类的名称以及对应的文章数
    category_list = Category.objects.values("pk").filter(blog=blog).annotate(c=Count("article__title")).values("c","title")

    # 查询当前站点每一个标签的名称以及对应的文章数
    tag_list = Tag.objects.values("pk").filter(blog=blog).annotate(c=Count("article__title")).values("c","title")

    #日期归档
    date_List = Article.objects.filter(user=user).extra(select={"y_m-date":"DATE_FORMAT(create_time,'%%Y/%%m')"}).\
                                                values("y_m-date").annotate(c=Count("id")).values_list("y_m-date","c")

    return render(request,"homesite.html",{"blog":blog,"article_list":article_list,
                                           "category_list":category_list,
                                           "tag_list":tag_list,"date_List":date_List,
                                           "username":username})

def article_detail(request,username,article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # # 查询当前站点每一个分类的名称以及对应的文章数
    # category_list = Category.objects.values("pk").filter(blog=blog).annotate(c=Count("article__title")).values("c",
    #                                                                                                            "title")
    # # 查询当前站点每一个标签的名称以及对应的文章数
    # tag_list = Tag.objects.values("pk").filter(blog=blog).annotate(c=Count("article__title")).values("c", "title")
    #
    # # 日期归档
    # date_List = Article.objects.filter(user=user).extra(
    #     select={"y_m-date": "DATE_FORMAT(create_time,'%%Y/%%m')"}).values("y_m-date").annotate(
    #     c=Count("id")).values_list("y_m-date", "c")
    article_obj = Article.objects.filter(pk=article_id).first()

    comment_list = Comment.objects.filter(articles_id=article_id)

    return render(request,"article_detail.html",locals())


# from app01.models import ArticleUpDown,Comment
import json
from django.http import JsonResponse

from django.db.models import F
from django.db import transaction

def digg(request):
    print(request.POST)
    is_up=json.loads(request.POST.get("is_up"))
    article_id=request.POST.get("article_id")
    user_id=request.user.pk
    response={"state":True,"msg":None}

    obj=ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
    if obj:
        response["state"]=False
        response["handled"]=obj.is_up
    else:
        with transaction.atomic():
            new_obj=ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)


    return JsonResponse(response)


def comment(request):

    # 获取数据
    user_id=request.user.pk
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    pid=request.POST.get("pid")
    # 生成评论对象
    with transaction.atomic():
        comment=Comment.objects.create(userinfo_id=user_id,articles_id=article_id,content=content,parent_comment_id_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response={"state":True}
    response["timer"]=comment.create_time.strftime("%Y-%m-%d %X")
    response["content"]=comment.content
    response["user"]=request.user.username

    return JsonResponse(response)


def backend(request):
    user=request.user
    article_list=Article.objects.filter(user=user)
    return render(request, "../static/../templates/backend/backend.html", locals())


def add_article(request):
    if request.method=="POST":

        title=request.POST.get("title")
        content=request.POST.get("content")
        user=request.user
        cate_pk=request.POST.get("cate")
        tags_pk_list=request.POST.getlist("tags")

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        # 文章过滤：
        for tag in soup.find_all():
            # print(tag.name)
            if tag.name in ["script",]:
                tag.decompose()

        # 切片文章文本
        desc=soup.text[0:150]
        print(desc)
        article_obj=Article.objects.create(title=title,count=str(soup),user=user,category_id=cate_pk,deac=desc)

        for tag_pk in tags_pk_list:
            Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag_pk)

        return redirect("/backend/")


    else:

        blog=request.user.blog
        cate_list=Category.objects.filter(blog=blog)
        tags=Tag.objects.filter(blog=blog)
        return render(request, "../static/../templates/backend/add_article.html", locals())

from Blog import settings
import os
def upload(request):
    print(request.FILES)
    obj=request.FILES.get("upload_img")
    name=obj.name

    path=os.path.join(settings.BASE_DIR,"static","upload",name)
    with open(path,"wb") as f:
        for line in obj:
            f.write(line)

    import json

    res={
        "error":0,
        "url":"/static/upload/"+name
    }

    return HttpResponse(json.dumps(res))