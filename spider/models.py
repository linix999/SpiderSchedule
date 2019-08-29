from django.db import models

STATUS_CHOICES = (
    (0, '禁用'),
    (1, '启用'),
)
CATAGERY_CHOICES = (
    (0, '普通'),
    (1, '重要'),
)

class Spider(models.Model):
    name=models.CharField(max_length=100,verbose_name='爬虫名称')
    deployProject = models.CharField(max_length=100, verbose_name='爬虫部署项目名称')
    catagery=models.IntegerField(choices=CATAGERY_CHOICES,verbose_name='爬虫分类')
    keywordParameters=models.CharField(max_length=1000,default="",verbose_name='关键词参数')
    dictParameters=models.CharField(max_length=1000,default="",verbose_name='字典参数')
    status=models.IntegerField(choices=STATUS_CHOICES,verbose_name='状态')
    note=models.CharField(max_length=1000,default="",verbose_name='备注')

    class Meta:
        verbose_name='爬虫'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name

class SuffixWords(models.Model):
    """
    由杭州那边维护并传参数过来，这边暂时不需要这个表了
    """
    name=models.CharField(max_length=100,verbose_name='附加词名称')
    catagery = models.IntegerField(default=0,verbose_name='分类')
    status=models.IntegerField(choices=STATUS_CHOICES,verbose_name='状态')

    class Meta:
        app_label="spider"
        verbose_name='附加词'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name