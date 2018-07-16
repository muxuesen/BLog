from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.
class UserInfo(AbstractUser):#用户
    tel=models.CharField(max_length=11,null=True,unique=True)
    avatar = models.FileField(upload_to='avatars/', default="avatars/default.png")
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True,null=True)
    #用户与个人主页一对一
    blog = models.OneToOneField(to="Blog",on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.username

class Article(models.Model):#文章
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    count = models.TextField()
    title = models.CharField(max_length=32, verbose_name="文章标题")
    deac = models.CharField(max_length=255, verbose_name="文章描述")

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    # 用户（一）文章（多）
    user = models.ForeignKey(to="UserInfo",
                             to_field="id",
                             on_delete=models.CASCADE,
                             verbose_name="作者")
    # 文章（多）分类（一）
    category = models.ForeignKey(to="Category",
                                 null=True,
                                 on_delete=models.CASCADE)
    # 文章（多）标签（多）
    tags = models.ManyToManyField(to="Tag",
                                  through='Article2Tag',)
    def __str__(self):
        return self.title

class Article2Tag(models.Model):
    article = models.ForeignKey(verbose_name="文章",to="Article",on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name="标签",to="Tag",on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]

    def __str__(self):
        v = self.article.title + "---" + self.tag.title
        return v

class Category(models.Model):#分类
    title = models.CharField(verbose_name="分类名称",max_length=32)
    #分类（一）博客（多）
    blog = models.ForeignKey(to="Blog",
                             verbose_name="所属博客",
                             on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Tag(models.Model):#标签
    title = models.CharField(verbose_name="标签名称",max_length=32)
    blog = models.ForeignKey(to="Blog",
                             verbose_name="所属博客",
                             on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class ArticleUpDown(models.Model):#赞灭
    user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey("Article", null=True, on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)



class Comment(models.Model):#评论
    content = models.CharField(max_length=1024,verbose_name="评论内容")
    create_time =models.DateTimeField(verbose_name="评论时间",auto_now_add=True)
    #用户（一）评论（多）
    userinfo = models.ForeignKey(to="UserInfo",
                                 verbose_name="评论者",
                                 on_delete=models.CASCADE)
    #文章（一）评论（多）
    articles = models.ForeignKey(to="Article",
                                 verbose_name="评论文章",
                                 on_delete=models.CASCADE)
    parent_comment_id = models.ForeignKey(to="Comment",null="True",on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class Blog(models.Model):#个人主页
    title = models.CharField(max_length=64,verbose_name='个人博客标题')
    site_name = models.CharField(verbose_name="站点名称",max_length=64)
    theme = models.CharField(verbose_name="博客主题",max_length=32)
    def __str__(self):
        return self.title