# -*- coding: utf-8 -*-
# @Time    : 6/20/19 11:15 PM
# @Author  : linix

import json
import datetime
from celery.task import task,periodic_task
from celery.schedules import crontab
from scrapyd_api import ScrapydAPI
from .models import Spider,SuffixWords
from hangzhou.models import MovieCrawlState
from django.conf import settings


@task()
def add(x,y):
    return x+y

def setDeParams(dictPara):
    params=dictPara.get('dictParameters',{})
    spiderName=dictPara.get('spider_name',"")
    searchWord = params.get('searchWord','')
    searchTaskId = str(params.get('searchTaskId', '-1'))
    results=SuffixWords.objects.filter(status__exact=0)
    suffixWords=""
    for x in results:
        suffixWords=suffixWords+x.name+","
    return searchWord.strip(),searchTaskId,suffixWords.rstrip(','),spiderName

def commonSchedule(catagery,isChangeScheduleStatus):
    scrapyd = ScrapydAPI(settings.SCRAPYD_URL,timeout=8)
    if catagery==1:
        results = MovieCrawlState.objects.filter(task__exact=catagery)
    else:
        results=MovieCrawlState.objects.filter(manage__exact=0).filter(task__exact=catagery)
    for item in results:
        dictParam=json.loads(item.json) if item.json else {}
        searchWord, searchTaskId,suffixWords,spiderName=setDeParams(dictParam)
        if len(searchWord):
            if spiderName:
                spiderList=Spider.objects.filter(name__exact=spiderName).filter(status__exact=0)
            else:
                spiderList=Spider.objects.filter(status__exact=0)
            for spider in spiderList:
                project=spider.deployProject
                scrapyd.schedule(project=project,spider=spider.name,keyword=searchWord,searchTaskId=searchTaskId,suffixWords=suffixWords)
            if isChangeScheduleStatus:
                item.manage=1
            item.startNum=len(spiderList)
            item.save()

@periodic_task(run_every=3)
def sheduleCustomerTask(**kwargs):
    commonSchedule(0,isChangeScheduleStatus=True)
    return True

@periodic_task(run_every=crontab(minute=0,hour=18))
def sheduleUserTask(**kwargs):
    commonSchedule(1, isChangeScheduleStatus=False)
    return True