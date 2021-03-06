#!/usr/bin/env python3
# file getcookie.py
import sys
from PyQt4.QtGui     import *
from PyQt4.QtCore    import *
from PyQt4.QtWebKit  import *
from PyQt4.QtNetwork import *


class GetCookieWindow(QWebView):
  
  def __init__(self, parent=None):
    QWebView.__init__(self, parent)
    #self.setWindowFlags(Qt.WindowStaysOnBottomHint | Qt.FramelessWindowHint)
    self.setContextMenuPolicy(Qt.NoContextMenu)
    #self.setMinimumSize(450,580)
    self.resize(410,520)
    self.setWindowTitle("Login")
    self.cookiejar = QNetworkCookieJar()
    self.page().networkAccessManager().setCookieJar(self.cookiejar)
    QObject.connect(self, SIGNAL("loadFinished(bool)"), self.onLoad)
    defaultSettings = QWebSettings.globalSettings()
    defaultSettings.setAttribute(QWebSettings.JavascriptEnabled, True)
    defaultSettings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
    self.firstload = True
    self.cookieStatus = [False, False, False]
    self.cookieList = []
    self.load(QUrl("https://secure.bilibili.com/login"))
    self.show()
    
  def onLoad(self, _bool):
    
    listCookies = self.page().networkAccessManager().cookieJar().cookiesForUrl(QUrl("http://member.bilibili.com"))
    for cookie in listCookies:
      cookiestr = str(cookie.toRawForm(), "utf-8")
      if cookiestr.find("DedeUserID=") == 0:
        self.cookieList.append(cookiestr.split("; ")[0])
        self.cookieStatus[0] = True
      if cookiestr.find("DedeUserID__ckMd5=") == 0:
        self.cookieList.append(cookiestr.split("; ")[0])
        self.cookieStatus[1] = True
      if cookiestr.find("SESSDATA=") == 0:
        self.cookieList.append(cookiestr.split("; ")[0])
        self.cookieStatus[2] = True
      
    if self.cookieStatus == [True, True, True]:
      print(";".join(self.cookieList))
      self.page().mainFrame().evaluateJavaScript("""
        setTimeout(function(){
          dQtConnect.jsCloseWindow();
          }, 400);
      """)
    self.page().mainFrame().addToJavaScriptWindowObject("dQtConnect", self)

    if self.firstload is True:
      self.firstload = False
      self.page().mainFrame().scroll(40,240)

  @pyqtSlot()
  def jsCloseWindow(self):
    self.close()
  
  
  
if __name__ == '__main__':
  app = QApplication(sys.argv)
  MainWindow = GetCookieWindow()
  MainWindow.show()
  sys.exit(app.exec_())