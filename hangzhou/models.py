from django.db import models

# Create your models here.
class MovieCrawlState(models.Model):
    id=models.IntegerField(primary_key=True)
    keyword = models.CharField(max_length=50)
    status = models.IntegerField()
    json = models.CharField(max_length=2000, blank=True, null=True)
    task = models.IntegerField()
    manage = models.IntegerField()
    startNum = models.IntegerField()
    finishNum = models.IntegerField()
    createtime = models.DateTimeField(db_column='createTime', blank=True, null=True)

    class Meta:
        managed = True
        app_label="hangzhou"
        db_table = 'movie_crawl_state'