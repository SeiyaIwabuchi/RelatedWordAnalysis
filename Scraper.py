import requests
import time
from Google import Google
import re
from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer
import json

class Scraper:
    tagPattern = r"<h\d(\s.*)*>.*?</h\d>"
    def __init__(self,searchDepth,topWord):
        self.searchDepth = searchDepth #深度（ヒットしたキーワードについての検索する回数）
        self.searchedWord = []
        self.topWord = topWord
        self.result = {} #{"キーワード":["ヒットしたワード",...]}
        self.t = Tokenizer("myDict.csv", udic_enc="utf8")

    def scraping(self,keyWord,times):
        self.searchedWord.append(keyWord)
        searchWord = keyWord
        retryFlag = True
        retryNum = 0
        while(retryFlag and retryNum < 10):
            try:
                google = Google()
                retryFlag = False
            except requests.exceptions.ConnectionError:
                    print("ConnectionError")
                    print("waiting 10Sec")
                    time.sleep(10)
        result = google.Search(searchWord,maximum=times)
        sentenceList = []
        for enum,hitURL in enumerate(result):
            print("{part}/{all}".format(part=str(enum+1),all=times) + ",nowDepth:{depth}".format(depth=str(self.searchDepth)))
            try:
                res = requests.get(hitURL)
                bs = BeautifulSoup(res.text,"html.parser")
                contentList = []
                for line in bs.find_all(re.compile("(h[1-6])|^p")):
                    contentList.append(re.sub(r"\s+"," ",line.text).rstrip().lstrip())
                for cont in contentList:
                    for token in self.t.tokenize(cont):
                        tmp = str(token).replace("\t",",").split(",")
                        if tmp[1] == "名詞" and not (len(tmp[0]) == 1):
                            #if tmp[2] == "固有名詞" and not (tmp[0].isalpha and len(tmp[0]) == 1):
                            sentenceList.append(tmp) #ここでヒットしたワードをリストに格納
                        #if tmp[0] == "コス":
                        #    print("------------\nhited:コス")
                        #    print(hitURL)
                        #    print("------------")
            except requests.exceptions.SSLError:
                print("SSLError")
            except UnicodeEncodeError:
                print("UnicodeEncodeError")
            except requests.exceptions.ConnectionError:
                print("ConnectionError")
            except requests.exceptions.ContentDecodingError:
                print("ContentDecodingError")
        #以下整理
        analyzeDict = {} #keyはワード,valueは数
        for sent in sentenceList:
            if sent[0] in analyzeDict.keys():
                analyzeDict[sent[0]] += 1 #すでにある場合はインクリメント
            else:
                analyzeDict[sent[0]] = 1 #ないときは追加して値に1を設定
        tmp2 = sorted(analyzeDict.items(), key=lambda x:x[1],reverse=True) #数が多い順にソート ここで返るのはタプル
        sortedAnalyze = {} #数が多い順に並べた辞書
        for sent,num in tmp2:
            sortedAnalyze[sent] = num
        sortedAnalyzeKeys = list(sortedAnalyze.keys())
        self.result[keyWord] = sortedAnalyzeKeys
        print(self.result)
        #with open("./result.json","w",encoding="utf-8") as res:
        #    json.dump(self.result,res,ensure_ascii=False)
        if self.searchDepth > 0:
            if self.topWord == -1:
                self.topWord = len(sortedAnalyze.keys())
            for i in range(self.topWord if len(sortedAnalyze.keys()) >= self.topWord else len(sortedAnalyze.keys())):#ヒットしたワードがtopword以上ならtopword個でいいがそれより小さいときは小さいほうに合わせる
                nextKeyword = sortedAnalyzeKeys[i]
                if not nextKeyword in self.searchedWord:
                    self.searchDepth -= 1
                    self.scraping(sortedAnalyzeKeys[i],times)
        self.searchDepth += 1

if __name__ == "__main__":
    myScraper = Scraper(searchDepth=1,topWord=1)
    initsearchWord = "自作パソコン"
    searchNum = 1
    myScraper.scraping(initsearchWord,searchNum)
    print(myScraper.result)