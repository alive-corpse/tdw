#!/usr/bin/python
# -*- coding: utf-8 -*-

import string, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, sys, cookielib, urllib, urllib2, time
addon = xbmcaddon.Addon(id='plugin.video.pazl.tv')
__settings__ = xbmcaddon.Addon(id='plugin.video.pazl.tv')
#-----------------------------------------

icon = ""
serv_id = '8'
siteUrl = '545-tv.com'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), siteUrl+'.sid')

cj = cookielib.FileCookieJar(sid_file) 
hr  = urllib2.HTTPCookieProcessor(cj) 
opener = urllib2.build_opener(hr) 
urllib2.install_opener(opener) 

def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)
def fs_enc(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode('utf-8').encode(sys_enc)

def fs_dec(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode(sys_enc).encode('utf-8')

from xid import *

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def getURL(url, Referer = httpSiteUrl):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	req.add_header('Referer', Referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L

def lower(s):
	try:s=s.decode('utf-8')
	except: pass
	try:s=s.decode('windows-1251')
	except: pass
	s=s.lower().encode('utf-8')
	return s

def get_idx(name):
	name=lower(name).replace(" #1","").replace(" #2","").replace(" #3","").replace(" #4","")
	try:
		id="x"+xmlid[name]
	except: 
		id=''
	return id

def save_channels(n, L):
		ns=str(n)
		fp=xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'Channels'+ns+'.py'))
		fl = open(fp, "w")
		fl.write('# -*- coding: utf-8 -*-\n')
		fl.write('Channels=[\n')
		for i in L:
			fl.write(repr(i)+',\n')
		fl.write(']\n')
		fl.write('udata545='+str(time.strftime('%Y%m%d')))
		fl.close()

def BL(name):
	bl=['[Premium]','(резерв','(тест)']
	for i in bl:
		if i in name: return False
	return True

class PZL:
	def __init__(self):
		pass

	def Streams(self, url):
		try:
			import Channels8
			udata=int(Channels8.udata545)
			#udata = int(__settings__.getSetting('udata545'))
		except:udata = 0
		cdata = int(time.strftime('%Y%m%d'))
		if cdata>udata: self.Canals()
			#__settings__.setSetting('udata545', time.strftime('%Y%m%d'))
			
		#srv=__settings__.getSetting("p2p_serv")
		#prt=__settings__.getSetting("p2p_port")
		return [url+'|User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:35.0) Gecko/20100101 Firefox/35.0',]

	def Canals(self):
		#__settings__.setSetting('udata545', time.strftime('%Y%m%d'))
		Logo = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'logo'))
		import logodb
		Ldb=logodb.ttvlogo
		LL=[]
		url='http://545-tv.com/iptvRU.m3u'
		http=getURL(url)
		http=http.replace(chr(10),"").replace(chr(13),"").replace("#EXTINF:-1 ", "\n#EXTINF:-1 ")
		#debug (http)
		L=http.splitlines()
		Lu=[]
		fdbc=False
		for i in L:
			no_err=True
			try:
			#if 'http://545' in i:
				#print "=================================================================="
				ss='http://545'
				url=i[i.find(ss):]
				#print url
					
				ss='",'
				es='http://545'
				title=mfindal(i,ss,es)[0][len(ss):]
				#print title
				
				if BL(title):
					xtitle=title.replace(' (18+)','').replace(' (+2)','').replace(' (+3)','').replace(' (+4)','').replace(' (+5)','').replace(' (+6)','').replace(' (+7)','').replace(' (Россия)','').replace(' (360р)','').replace(' (480р)','').replace(' (720р)','').replace(' (новосибирск)','').replace(' (екатеринбург)','').replace(' (челябинск)','')
					id = get_idx(xtitle).replace("xttv","")
					if id=="":
							xtitle=xtitle.replace(' HD','').replace(' Channel','').replace(' TV','').replace(' Tv','').replace(' ТВ','').replace(' (Молдова)','').replace(' (Azerbaijan)','').replace(' Music channel','').replace(' (Teen TV)','')#.replace('','').replace('','').replace('','')
							
							id = get_idx(xtitle).replace("xttv","")
							#print "-------------------- Нет ID -------------------"
							#if id=="": print lower(xtitle)

					if id!="" and url not in Lu:
						#print id
						
						try:
							#print "-------------------- Поиск логотипа в БД по ID -------------------"
							img=Ldb[id]
							#print img
						except:
							#try:
								#print "------------ Логотип отсутствует в БД > Грузим с 1ttv ------------"
								#u2='http://1ttv.net/iframe.php?site=1714&channel='+id
								#tmp=getURL(u2)
								#ss='http://torrent-tv.ru/uploads/'
								#es='.png" style="vertical-align'
								#img=mfindal(tmp,ss,es)[0]+'.png'
								#print '"'+id+'":"'+img+'"'
								#Ldb[id]=img
								#fdbc=True
								#print "-------------------- Логотип сохранен в БД -------------------------"
							#except:
								#print "---------------------- Ошибка поиска на 1ttv > ищем локально -----------------------"
								path = fs_enc(os.path.join(Logo, id+'.png'))
								try: sz=os.path.getsize(path)
								except: sz=0
								if sz >0:
									img=path
								else:
										#print "------------------! Логотип незвестен !-------------------------"
										#print url
										#print id
										#print lower(title)
										img="http://televizorhd.ru/templates/Server-Torrent-TV/dleimages/no_image.jpg"
										#no_err=False
						
					else:
						#print " --------------- ОШИБКА ЗАГРУЗКИ КАНАЛА ----------------- "
						#print i
						#no_err=False
						img="http://televizorhd.ru/templates/Server-Torrent-TV/dleimages/no_image.jpg"
						
					if no_err: 
						LL.append({'url':url, 'img':img, 'title':title+' #'+serv_id})
						Lu.append(url)
					
			except: 
			#else:
					#print " --------------- ОШИБКА  ----------------- "
					#print i
					pass
				
		if fdbc:
			fp=xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'logodb.py'))
			fl = open(fp, "w")
			fl.write('# -*- coding: utf-8 -*-\n')
			fl.write('ttvlogo={\n')
			for i in Ldb.items():
				fl.write('"'+i[0]+'":"'+i[1]+'",\n')
			fl.write('}')
			fl.close()

		if LL!=[]:save_channels(serv_id, LL)
		else: showMessage('545-tv.com', 'Не удалось загрузить каналы', 3000)

		return LL
