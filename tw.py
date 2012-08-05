# This Python file uses the following encoding: utf-8
import myLib.tweepy as tweepy
import time
import datetime
import sys
import myLib.pywapi as pywapi
import string
import urllib
import traceback
import threading
#import pytz

#bookmark={'homeTimeline':datetime.datetime.utcnow(),'mention':datetime.datetime.utcnow()}
weatherSubscription=[{'screen_name':'silencedrop','location':'Bowling Green, OH','time':'8:00','language':'zh-cn','last_sent':datetime.date(2000,1,1)},
                     
                     #{'screen_name':'baspland','location':'San Francisco','time':'9:00','language':'en','last_sent':datetime.date(2000,1,1)},
                     ]
replyHome=[{'screen_name':'silencedrop'},
              #{'screen_name':'hELLoELL'},
              #{'screen_name':'Anya042'},
              #{'screen_name':'its_LilianaJans'},
              ]
timelineLog={'home':datetime.datetime.utcnow()}
loopInterval={'status':3600,'homeTimeline':300,'weather':60,'autoFo':3600,'job':10800}
jobSearchQuery=["job developer python","job developer JavaScript PHP","job developer C++",]

def getweatherReport(location,language):
    google_result = pywapi.get_weather_from_google(location,language)
    msg=google_result['forecast_information']['forecast_date']+', '
    msg+=google_result['forecast_information']['city']+'\n'
    msg+=google_result['current_conditions']['condition']+', '
    msg+=google_result['current_conditions']['temp_c']+'C, '
    msg+=google_result['current_conditions']['humidity']+', '
    msg+=google_result['current_conditions']['wind_condition']+'\n'
    for item in google_result['forecasts']:
        msg+=item['day_of_week']+': '
        msg+=item['condition']+' '
        msg+=item['low']+'~'
        msg+=item['high']+'\n'
    return msg

def getQuote():
    handler=urllib.urlopen("http://www.iheartquotes.com/api/v1/random?max_characters=120&show_permalink=false&show_source=false")
    #msg=handler.read()
    #handler=urllib.urlopen("http://wap.unidust.cn/api/searchout.do?type=client&ch=1001&appid=61")
    msg=handler.read()
    msg=unicode(msg,"utf-8")
    return msg
    #msg=msg[30:170]

def connectTwitter():
    consumer_key="kv3ReRJ4EfN0UsqBqhMx6w"
    consumer_secret="7j22oH7UPZ7BzHUVpKbsEfNDlVwSqOQU5eJPFmTNvlI"
    access_token="475314640-fFDfX85bc5sM0BZ4yIvXKe0S7ieufIR1QdNbPESM"
    access_token_secret="jML8973BOpYXy1tmwRxVSDyKRY1dLpIFh3Mk1BN0PYw"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    global api
    api = tweepy.API(auth)
    print api.me().name
    #api.update_status('Updating usindg2 ')
    
def weatherReport():
    for user in weatherSubscription:
        userTime=datetime.datetime.strptime(user['time'],"%H:%M").time()
        #print userTime.hour,userTime.minute
        current=datetime.datetime.now().time()
        #print datetime.date.today()
        #print user['last_sent']
        if userTime.hour!=current.hour or userTime.minute>current.minute or datetime.date.today()<=user['last_sent']:
            #print userTime.hour,current.hour,userTime.minute,current.minute
            continue
        msg=getweatherReport(user['location'],user['language'])
        msg=msg[:140]
        api.send_direct_message(screen_name=user['screen_name'],text=msg)
        user['last_sent']=datetime.date.today()
        print "sent weather message to "+user['screen_name']
    #print api.get_user('silencedrop').id
    #api.send_direct_message(screen_name='silencedrop',text='hello')
    
def checkHomeTimeline():
    #global replyMessage
    print "Checking Home Timeline"
    statuses = tweepy.Cursor(api.home_timeline).items()
    utcNow=datetime.datetime.utcnow()
    #utcAgo=utcNow-datetime.timedelta(seconds=loopInterval['homeTimeline'])
    for status in statuses:
        #print dir(status)
        #print dir(status.author)
        #print type(status.created_at)
        if status.created_at<=timelineLog['home']:
            break
        for item in replyHome:
            if(status.author.screen_name==item['screen_name']):
                #api.update_status("@"+status.author.screen_name+" "+item['text']+"\nUTC: "+datetime.datetime.utcnow().ctime(),in_reply_to_status_id = status.id)
                api.update_status("@"+status.author.screen_name+" "+getQuote(),in_reply_to_status_id = status.id)
                print "reply to "+status.author.screen_name
                time.sleep(5)
    timelineLog['home']=utcNow
def seekJob():
    print "seeking job"
    utcNow=datetime.datetime.utcnow()
    utcAgo=utcNow-datetime.timedelta(seconds=loopInterval['job'])
    reply='''Hi, I am a twitter bot created by J.L, he is looking for a programmer job\nlinkedin: http://alturl.com/ajyhr\nemail: jialinliu7@gmail.com\n'''
    list=[]
    for queryKeywords in jobSearchQuery:
        pageIndex=1
        #print queryKeywords
        items=api.search(q=queryKeywords,rpp=100,lang='en',page=pageIndex)
        #print pageIndex
        #pageIndex+=1
        for item in items:
            #print item.created_at
            #print item.from_user
            #print item.id
            if item.created_at<=utcAgo:
                break
            if item.from_user in list:
                continue
            #print item.text.encode("utf-8")
            api.update_status("@"+item.from_user+" "+reply,in_reply_to_status_id=item.id)
            list.append(item.from_user)
            print "job reply to "+item.from_user
            time.sleep(300)
        
        
#def checkDirectMessage():
#    messages=api.direct_messages()
#    for message in messages:    
#        for item in message.text.split():
#            if item.isdigit():
#                print int(item)
#def directMessageTimer(interval,user_id,text):
    #sleep(interval)
    #api.send_direct_message(screen_name=user['screen_name'],text=msg)
    
def postTweet():
    print "post tweet"
    api.update_status(getQuote())
def autoFollow():
    print "auto follow"
    for id in api.followers_ids():
        if id not in api.friends_ids():
            api.create_friendship(id)
            print "followed "+api.get_user(id).screen_name

def loopMaster(func,interval):
    while(1):
        try:
            func()
            time.sleep(interval)
        except:
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            time.sleep(interval)

           
if __name__ == "__main__":
    connectTwitter()
    status=threading.Thread(target=loopMaster,args=(postTweet,loopInterval['status'],))
    homeTimeline=threading.Thread(target=loopMaster,args=(checkHomeTimeline,loopInterval['homeTimeline'],))
    weather=threading.Thread(target=loopMaster,args=(weatherReport,loopInterval['weather'],))
    autoFo=threading.Thread(target=loopMaster,args=(autoFollow,loopInterval['autoFo'],))
    #job=threading.Thread(target=loopMaster,args=(seekJob,loopInterval['job'],))
    status.start()
    homeTimeline.start()
    weather.start()
    autoFo.start()
    #job.start()



    
 