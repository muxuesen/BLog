from django import template
from app01.models import Category,Tag,Article,UserInfo
from django.db.models import Count

register = template.Library()


@register.inclusion_tag("left_region.html")
def get_query_data(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    category_list = Category.objects.values("pk").filter(blog=blog).annotate(c=Count("article__title")).values("c",
                                                                                                               "title")
    # 查询当前站点每一个标签的名称以及对应的文章数
    tag_list = Tag.objects.values("pk").filter(blog=blog).annotate(c=Count("article__title")).values("c", "title")

    # 日期归档
    date_List = Article.objects.filter(user=user).extra(
        select={"y_m-date": "DATE_FORMAT(create_time,'%%Y/%%m')"}).values("y_m-date").annotate(
        c=Count("id")).values_list("y_m-date", "c")
    return {"blog":blog,"username":username,"category_list":category_list,"tag_list":tag_list,"date_List":date_List}
