# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz

PATH = ''#'C:\\Users\\许荣海\\Desktop\\一些实验\\python实验\\pset5\\'
#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1

# TODO: NewsStory
# newstory类比较简单，建立类属性，以及建立类函数用于获取属性
class NewsStory(object):
    #guid, title, description, link, pubdate 
    def __init__(self,guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid
    
    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_link(self):
        return self.link

    def get_pubdate(self):
        return self.pubdate

#======================
# Triggers
#======================
# evaluate不用修改，被子类方法覆盖
class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS

# Problem 2
# TODO: PhraseTrigger 
class PhraseTrigger(Trigger):
    def __init__(self,phrase):
        self.phrase = phrase
    # 思想：把text文本的标点符号用空格替换，且单词与单词之间只有一个空格，
    # 再用find方法进行匹配。

    # 将text的标点符号用空格代替，
    # 再根据空格把text分割成单词列表，同时去掉空字符串，再通过空格字符把单词连接在一起
    # 这样单词间就只有一个空格了
    # 调用字符串的find方法匹配词组
    # 这里需要注意的是find查到后，还得保证下一个字符是空格或者结束
    def is_phrase_in(self,Text):
        ph = self.phrase.lower()
        text = Text.lower()
        #空格替换标点
        for s in string.punctuation:
            text = text.replace(s,' ')
        words = text.split(' ')

        for i in range(words[:].count('')):
            words.remove('')
                
        text = ' '.join(words)

        k=text.find(ph)
        if k == -1 or(k+len(ph)<len(text) and text[k+len(ph)]!=' '):
            return False
        else:
            return True
  
        
# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhraseTrigger):
    # 子类调用父类构造函数的两种方法：
    # PhraseTrigger.__init__(self,title)
    # super().__init__(title)
    def __init__(self,title):
        PhraseTrigger.__init__(self,title)
    
    # 子类调用父类方法  PhraseTrigger.is_phrase_in
    def evaluate(self, story):
        if PhraseTrigger.is_phrase_in(self,story.get_title()):
            return True
        return False

# Problem 4
# TODO: DescriptionTrigger
class DescriptionTrigger(PhraseTrigger):
    def __init__(self,description):
        PhraseTrigger.__init__(self,description)

    def evaluate(self, story):
        if PhraseTrigger.is_phrase_in(self,story.get_description()):
            return True
        return False    
# TIME TRIGGERS

# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.
class TimeTrigger(Trigger):
    def __init__(self, t_str):
        #strptime函数按格式生成时间元组
        self.time = time.strptime(t_str, "%d %b %Y %H:%M:%S")

# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def __init__(self,str_time):
        TimeTrigger.__init__(self,str_time)

    def evaluate(self,story):
        #直接比较两个元组大小,pubdate是datetime类型，需要转化为元组才能进行比较
        return self.time > story.pubdate.timetuple()

class AfterTrigger(TimeTrigger):
    def __init__(self,str_time):
        TimeTrigger.__init__(self,str_time)

    def evaluate(self,story):
        #直接比较两个元组大小,pubdate是datetime类型，需要转化为元组才能进行比较
        return self.time < story.pubdate.timetuple()


# COMPOSITE TRIGGERS
#复合触发器的一个实例，初始函数添加两个不同短语触发器作为属性。
#只有当这两个触发器都触发时，才算触发复合触发器
'''
class CompositeTrigger(Trigger):
    def __init__(self,phrase1,phrase2):
        self.phTrigger1 = PhraseTrigger(phrase1)
        self.phTrigger2 = PhraseTrigger(phrase2)
    
    def evaluate(self, story):
        if self.phTrigger1.is_phrase_in(story.title) and self.phTrigger2.is_phrase_in(story.title):
            return True
        return False
'''


# Problem 7
# TODO: NotTrigger
# 传递触发器给构造函数，作为属性
# 当触发器都返回的相反值，为not触发器的返回值
class NotTrigger(Trigger):
    def __init__(self,trigger):
        self.trigger = trigger

    def evaluate(self, story):
        return not self.trigger.evaluate(story)
# Problem 8
# TODO: AndTrigger
# 传递两个触发器给构造函数，作为属性
# 当两个触发器都返回true时，才真正触发and触发器
class AndTrigger(Trigger):
    def __init__(self,trigger1,trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self, story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)
# Problem 9
# TODO: OrTrigger
# 传递两个触发器给构造函数，作为属性
# 当其中一个触发器都返回true时，才真正触发and触发器
class OrTrigger(Trigger):
    def __init__(self,trigger1,trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self, story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)

#======================
# Filtering
#======================

# Problem 10
# 当任意一个故事满足一个触发器时，就添加到触发故事列表中
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.
    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    t_story=[]
    for story in stories:#每个故事遍历一次列表，触发则添加到触发列表中，且break
        for trigger in triggerlist:
            if trigger.evaluate(story):
                t_story.append(story)
                break
    return t_story        

    # TODO: Problem 10
    # This is a placeholder
    # (we're just returning all the stories, with no filtering)
    



#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)
            
    # 建立命令列表和字典
    # 触发列表用于返回
    # 触发字典用于and or not 等复合触发器
    comment_list=[]
    comment_dic ={}
    for line in lines:
        # 将命令分割成字典
        comment = line.split(',')
        print(comment) # 打印用于测试

        # add指令时，将add后的所有触发器添加到列表中
        if comment[0].lower()== 'add':
            for i in range(1,len(comment)):
                comment_list.append(comment_dic[comment[i]])

        # comment长度为3时，按照不同触发器类型添加到字典中
        elif len(comment)==3:
            type = comment[1].lower()
            property = comment[2].lower()
            #添加到字典中
            if   type =='title':
                comment_dic[comment[0]] = TitleTrigger(property)
            elif type == 'description':
                comment_dic[comment[0]] = DescriptionTrigger(property)
            elif type == 'after':
                comment_dic[comment[0]] = AfterTrigger(property)
            elif type == 'before':
                comment_dic[comment[0]] = BeforeTrigger(property)
            elif type == 'not':
                t = comment_dic[comment[2]]
                comment_dic[comment[0]] = OrTrigger(t)
        elif len(comment)==4:
            type = comment[1].lower()
            if type == 'or':
                t1 = comment_dic[comment[2]]
                t2 = comment_dic[comment[3]]
                comment_dic[comment[0]] = OrTrigger(t1,t2)
            elif type == 'and':
                t1 = comment_dic[comment[2]]
                t2 = comment_dic[comment[3]]
                comment_dic[comment[0]] = AndTrigger(t1,t2)
    return comment_list
    # TODO: Problem 11
    # line is the list of lines that you need to parse and for which you need
    # to build triggers

    # for now, print it so you see what it contains!



SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("china")
        t2 = DescriptionTrigger("iphone")
        #t3 = DescriptionTrigger("china")
        #t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t2]

        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line 
        triggerlist = read_trigger_config(PATH+'triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            #"http://news.google.com/news?output=rss"
            stories = process("http://news.yahoo.com/rss/topstories")

            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.google.com/news?output=rss"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

