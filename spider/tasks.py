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

maxScheduleTasks=500
@task()
def add(x,y):
    return x+y

def getRunServer(deployProject='searchSpiders'):
    """
    :return: 返回pending和running状态任务数最少的机器,暂时按每个任务进行一次安排。如果超过最大任务数就不添加任务
    """
    servers=settings.SCRAPYD_URLS
    minTaskServer=None
    minTasks=-1
    for server in servers:
        try:
            scrapyd = ScrapydAPI(server, timeout=8)
            jobs=scrapyd.list_jobs(project=deployProject)
            taskNums=len(jobs.get('pending',[]))+len(jobs.get('running',[]))
        except BaseException as e:
            print("this server is not deployed, %s" %server)
            continue
        print("server: %s Running tasks is %s" %(server,taskNums))
        if taskNums<maxScheduleTasks and (taskNums<minTasks or minTasks<0) :
            minTaskServer=server
            minTasks=taskNums
    return minTaskServer

def setDeParams(dictPara):
    params=dictPara.get('dictParameters',{})
    spiderName=dictPara.get('spider_name',"")
    searchWord = params.get('searchWord','')
    searchTaskId = str(params.get('searchTaskId', '-1'))
    proxyType=params.get("proxyType","0")
    limit=params.get("limit", "-1")
    filterWords=params.get("filterWords", "")
    necessaryWords=params.get("mustWord", "")
    extraParams={
        'proxytype':proxyType,
        'limit':limit,
        'filterWords':filterWords,
        'necessaryWords':necessaryWords
    }
    suffixWords = params.get('attachWord','')
    if spiderName:
        spiderNameList = spiderName.split(',')
        spiderList=[]
        for spiderName in spiderNameList:
            spiderObjs=Spider.objects.filter(name__exact=spiderName).filter(status__exact=0)
            if spiderObjs:
                spiderList.append(spiderObjs[0])
    else:
        spiderList = Spider.objects.filter(status__exact=0)

    return searchWord.strip(),searchTaskId,suffixWords,spiderList,extraParams

def commonSchedule(catagery,isChangeScheduleStatus):
    if catagery==1:
        results = MovieCrawlState.objects.filter(task__exact=catagery)
    else:
        results=MovieCrawlState.objects.filter(manage__exact=0).filter(task__exact=catagery)
    for item in results:
        dictParam=json.loads(item.json) if item.json else {}
        searchWord, searchTaskId,suffixWords,spiderList,extraParams=setDeParams(dictParam)
        extraParams = json.dumps(extraParams, ensure_ascii=False, separators=(',', ':'))
        scheduleServer = getRunServer()
        if scheduleServer:
            scrapyd = ScrapydAPI(scheduleServer, timeout=8)
            if isChangeScheduleStatus:
                item.manage = 1
            item.startNum = len(spiderList)
            item.save()
            if len(searchWord):
                for spider in spiderList:
                    print(spider.deployProject,spider.name,searchWord,searchTaskId,suffixWords,extraParams)
                    project=spider.deployProject
                    scrapyd.schedule(project=project,spider=spider.name,keyword=searchWord,searchTaskId=searchTaskId,suffixWords=suffixWords,extraParams=extraParams)

@periodic_task(run_every=3)
def sheduleCustomerTask(**kwargs):
    commonSchedule(0,isChangeScheduleStatus=True)
    return True

@periodic_task(run_every=crontab(minute=0,hour=18))
def sheduleUserTask(**kwargs):
    commonSchedule(1, isChangeScheduleStatus=False)
    return True