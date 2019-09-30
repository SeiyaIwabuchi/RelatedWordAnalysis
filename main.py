import requests
import time
from Google import Google
import re
from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer

tagPattern = r"<h\d(\s.*)*>.*?</h\d>"
searchDepth = 1
initsearchWord = "自作パソコン"
searchedWord = []
searchNum = 50
topWord = 10

def scraper(keyWord,times):
    global searchDepth
    global searchedWord
    searchedWord.append(keyWord)
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
        print("{part}/{all}".format(part=str(enum+1),all=times) + ",nowDepth:{depth}".format(depth=str(searchDepth)))
        try:
            res = requests.get(hitURL)
            bs = BeautifulSoup(res.text,"html.parser")
            contentList = []
            for line in bs.find_all(re.compile("(h[1-6])|^p")):
                contentList.append(re.sub(r"\s+"," ",line.text).rstrip().lstrip())
            #print(contentList)
            t = Tokenizer()
            for cont in contentList:
                for token in t.tokenize(cont):
                    tmp = str(token).replace("\t",",").split(",")
                    if tmp[1] == "名詞":
                        if tmp[2] == "固有名詞" and not (tmp[0].isalpha and len(tmp[0]) == 1):
                            sentenceList.append(tmp)
        except requests.exceptions.SSLError:
            print("SSLError")
        except UnicodeEncodeError:
            print("UnicodeEncodeError")
        except requests.exceptions.ConnectionError:
            print("ConnectionError")
        except requests.exceptions.ContentDecodingError:
            print("ContentDecodingError")
    analyzeDict = {}
    for sent in sentenceList:
        if sent[0] in analyzeDict.keys():
            analyzeDict[sent[0]] += 1
        else:
            analyzeDict[sent[0]] = 1
    tmp2 = sorted(analyzeDict.items(), key=lambda x:x[1],reverse=True)
    sortedAnalyze = {}
    for sent,num in tmp2:
        sortedAnalyze[sent] = num
    tmpStr = ""
    for i in range(topWord if len(sortedAnalyze.keys()) >= topWord else len(sortedAnalyze.keys())):
        sortedAnalyzeKeys = list(sortedAnalyze.keys())
        tmpStr += sortedAnalyzeKeys[i] + "\n"
    with open("./result/{key}.txt".format(key=searchWord),"w",encoding="utf-8") as f:
        f.write(tmpStr)
    if searchDepth > 0:
        for i in range(topWord if len(sortedAnalyze.keys()) >= topWord else len(sortedAnalyze.keys())):
            sortedAnalyzeKeys = list(sortedAnalyze.keys())
            nextKeyword = sortedAnalyzeKeys[i]
            if not nextKeyword in searchedWord:
                searchDepth -= 1
                scraper(sortedAnalyzeKeys[i],times)
    searchDepth += 1

if __name__ == "__main__":
    scraper(initsearchWord,searchNum)