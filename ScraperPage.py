from flask import Flask, render_template, make_response, request, jsonify
import Scraper
import datetime
import threading
import json

app = Flask(__name__,template_folder="./")

htmlPathDict = {

    "topPage":"topPage.htm"

}

resultJsonPath = "result/"

liveLimit = 60 * 60  * 24 * 120 #秒指定

resultDict = {}

#sessionクラス
class Session:
    def __init__(self):
        self.NoSession = "NoSession"
        self.sessionID = "sessionID"
        self.SID = 0
    def getSID(self):
        self.SID += 1
        return self.SID-1

session = Session()
threadDict = {}
scraperDict = {}

@app.route("/")
def getIndex():
    retStr = ""
    with open(htmlPathDict["topPage"],"r",encoding="utf-8") as f:
        retStr = f.read()
    # Cookieの設定を行う
    response = make_response(retStr)
    max_age = liveLimit
    expires = int(datetime.datetime.now().timestamp()) + max_age
    response.set_cookie(session.sessionID, value=str(session.getSID()), max_age=max_age, expires=expires, path='/', secure=None, httponly=False)
    return response

def wrapScraping(scraperObj,keyword,times):
    scraperObj.scraping(keyword,times)
    print("finished")
    with open(resultJsonPath+keyword,"w",encoding="utf-8") as res:
        json.dump(scraperObj.result,res,ensure_ascii=False, indent=4, sort_keys=False, separators=(',', ': '))
        print("jsonSaved")

@app.route("/scraping/<keyword>")
def startScraping(keyword=None):
    global resultDict
    SID = request.cookies.get(session.sessionID,None)
    if keyword == "":
        return """ <script> window.location.href = "/" </script>"""
    if SID in scraperDict.keys():
        if threadDict[SID].is_alive():
            return "ただいま処理中です。お待ちください。{now}".format(now=str(datetime.datetime.now()))
        else:
            try:
                with open(resultJsonPath+keyword,"r",encoding="utf-8") as res:
                    return res.read()
            except FileNotFoundError:
                response = make_response("""<script> window.location.href = "/scraping/{keyword}" </script>""".format(keyword=keyword))
                max_age = liveLimit
                expires = int(datetime.datetime.now().timestamp()) + max_age
                response.set_cookie(session.sessionID, value=str(session.getSID()), max_age=max_age, expires=expires, path='/', secure=None, httponly=False)
                return response
    else:
        scraperDict[SID] = Scraper.Scraper(0,0)
        threadDict[SID] = threading.Thread(target=wrapScraping,args=(scraperDict[SID],keyword,10,))
        threadDict[SID].daemon = True
        threadDict[SID].start()
        return "ただいま処理中です。お待ちください。{now}".format(now=str(datetime.datetime.now()))

if __name__ == "__main__":
    app.run(threaded = True,debug=True,host="0.0.0.0", port=80)