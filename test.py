import asyncio
import aiohttp
import pandas as pd
import json
#from bs4 import BeautifulSoup
#from lxml import etree
import time
import async_timeout

class ZhihuCrawl:
    def __init__(self, csv_location, _workers_max):
        self.counter = 0
        self._workers = 0
        self._workers_max = _workers_max
        self.csv_location = csv_location

    def creat_url(self, url_token):
        #url = ('https://www.zhihu.com/api/v4/members/' + url_token + '/activities?limit=7&session_id=1093619935493894144&after_id=1570777388&desktop=True')
        url = ('https://www.zhihu.com/api/v3/feed/members/' + url_token + '/activities?limit=7&session_id=1208727328026877952&after_id=1584071327&desktop=True')
        return url

    def save_data(self, commentss):
        filename = 'a.csv'
        dataframe = pd.DataFrame(commentss)
        dataframe.to_csv(filename, index=False, header=False, sep=',', mode='a' ) # encoding="utf_8_sig",
        #dataframe.to_csv(filename, mode='a', index=False, sep=',', header=['name','gender','user_url','voteup','cmt_count','url'])
    
    def parse_resp(self, resp):
        next_url = 'None'
        is_end = resp['paging']['is_end']
        if(not is_end):
            next_url = resp['paging']['next']
        data = resp['data']
        comments = []
        if(len(data) != 0):
            
            for act_data in data: 
                comment_p = []
                verb = act_data['verb']
                if ((verb == "ANSWER_VOTE_UP")or(verb == "MEMBER_VOTEUP_ARTICLE")):
                    comment_p.append(act_data['actor']['url_token']) #用户id
                    #comment_p.append(verb)               #行为{"ANSWER_VOTE_UP","MEMBER_VOTEUP_ARTICLE","ANSWER_CREATE","MEMBER_CREATE_ARTICLE","QUESTION_FOLLOW","MEMBER_FOLLOW_ROUNDTABLE","QUESTION_CREATE"}
                    comment_p.append(act_data['created_time'])       #行为发生时间
                    comment_p.append(act_data['target']['id'])
                    if(verb == "ANSWER_VOTE_UP"):
                        comment_p.append(act_data['target']['question']['id'])    #questionid 
                    else:
                        comment_p.append(0)
                else:
                    continue
                comments.append(comment_p)
        return next_url, comments, is_end
                


    async def producer(self, queue):
        df = pd.read_csv(self.csv_location,usecols=[0])
        url_token_list=df.values.tolist()
        for item in url_token_list:
            url_token = item[0]
            if (type(url_token)==str):
                await queue.put(url_token)

    async def downloader(self, url):
        headers = {
            "authority": "www.zhihu.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "Connection": "close",
        }
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(300):
                async with session.get(url, timeout=None,headers= headers,verify_ssl=False) as response:
                    status = response.status
                    if(status != 200):
                        print(status, response)
                    #print('test1000')
                    text = await response.text()
                    return status, text
                #print(status, text)
        #except Exception as e:
         #   print("********\n[error]{}\n{}\n********".format(url,e))   
          #  return 1, '0x3error'         
    
    async def loop(self,num, url):
        comments = []
        is_end = False
        flag = 0
        while True:
            try:
                status, response = await self.downloader(url)
                _json = json.loads(response)
                next_url, comment, is_end = self.parse_resp(_json)
            except Exception:
                await asyncio.sleep(360)
                status, response = await self.downloader(url)
                _json = json.loads(response)
                next_url, comment, is_end = self.parse_resp(_json)
            if (len(comment) != 0):
                comments.extend(comment)
                flag = 1
            if (is_end == True):
                if(flag == 1):
                    self.save_data(comments)
                return 0
            url = next_url
            
    async def worker2(self,num, queue):
        while True:
            token = await queue.get()
            #todo_http(
            first_url = self.creat_url(token)
            await self.loop(num,first_url)
            #await asyncio.sleep(2)
                #)todo_http
            queue.task_done()
            self.counter += 1
            print(self.counter, token)


    async def worker(self,num, queue):
        try:
            while True:
                #try:
                token = await queue.get()
                #todo_http(
                first_url = self.creat_url(token)
                await self.loop(num,first_url)
                #await asyncio.sleep(2)
                    #)todo_http
                queue.task_done()
                self.counter += 1
                print(self.counter, token)
        except Exception:
            await asyncio.sleep(600)
            asyncio.create_task(self.worker2(999,queue))
        
    async def threadCtrl(self,):
        queue = asyncio.Queue()
        await self.producer(queue)
        tasks = []
        for i in range(self._workers_max):
            i = asyncio.create_task(self.worker(i,queue))
            tasks.append(i)
        print(len(tasks))
        await asyncio.gather(*tasks)
        await queue.join()
        st, res = await self.downloader('https://www.zhihu.com/api/v3/feed/members/ha-ha-ha-ha-ha-ha-43-23-66/activities?limit=7&session_id=1208727328026877952&after_id=1584071327&desktop=True')
        #await self.downloader('https://www.zhihu.com/api/v4/members/keiga/activities?limit=7&session_id=1093619935493894144&after_id=1570777388&desktop=True')
        print(res)
        _json = json.loads(res)
         #= 
        #print(res.read())
        #html = await res
        #result = json.loads(res)
        #a = json.loads(e.xpath()[0].text)
        #a = json.loads(["paging"]["is_end"])
        #print(_json)
        #self.parse_resp(result)
        
        

    
    def run(self):
        try:
            asyncio.run(self.threadCtrl())
            print('test1')
        except KeyboardInterrupt:
            print('stopped by yourself!')
            pass

if __name__ == '__main__':
    nc = ZhihuCrawl('excited-vczh(fellower).csv',190,)#file, coroutine number
    nc.run()
    print('end')
