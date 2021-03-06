# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, os, urllib, sys, urllib2, time
#nt=time.time()
PLUGIN_NAME   = 'plugin.video.pazl.tv'
handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.pazl.tv')
__settings__ = xbmcaddon.Addon(id='plugin.video.pazl.tv')

siteUrl = 'viks.tv'
httpSiteUrl = 'http://' + siteUrl

Pdir = addon.getAddonInfo('path')
icon = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'icon.png'))
fanart = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'fanart.png'))
Logo = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'logo'))
UserDir = xbmc.translatePath(os.path.join(xbmc.translatePath("special://masterprofile/"),"addon_data","plugin.video.pazl.tv"))

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

sys.path.append(os.path.join(addon.getAddonInfo('path'),"serv"))
ld=os.listdir(os.path.join(addon.getAddonInfo('path'),"serv"))
Lserv=[]
for i in ld:
	if i[-3:]=='.py': Lserv.append(i[:-3])

#Lserv=['p01_peers', 'p02_onelike', 'p03_1ttv', 'p04_asplaylist']

sys.path.append(os.path.join(addon.getAddonInfo('path'),"arh"))
ld=os.listdir(os.path.join(addon.getAddonInfo('path'),"arh"))
Larh=[]
for i in ld:
	if i[-3:]=='.py': Larh.append(i[:-3])


from xid import *
from DefGR import *
#Ldf=eval(__settings__.getSetting("Groups"))
def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def fs_enc(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode('utf-8').encode(sys_enc)

def fs_dec(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode(sys_enc).encode('utf-8')

def lower(s):
	try:s=s.decode('utf-8')
	except: pass
	try:s=s.decode('windows-1251')
	except: pass
	s=s.lower().encode('utf-8')
	return s

if __settings__.getSetting("ACE_API")=='true': 
	import socket, threading, re

	class _TSServ(threading.Thread):
		def __init__(self, socket):
			self.pkey = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'
			threading.Thread.__init__(self)
			self._sock = socket
			self._buffer = 65 * 1024
			self._last_received = ''
			self.active = True
			self.err = False
			self.auth_ok = False
			self.version = None
			self.files = None
			self.key = None
			self.index = None
			self.content_url = None
			self.can_save = False
			self.save_info = None
			self.state = 0
			self.status = [0, '', '']
			self.pause = False
			self.vod = True

		def push(self, command):
			print ('TSSERV: [%s]' % command)
			try:
				self._sock.send(command + '\r\n')
			except:
				self.err = True

		def run(self):
			while self.active and not self.err:
				try:
					self.temp = self._sock.recv(self._buffer)
				except:
					self.temp = ''
				self._last_received += self.temp
				ind = self._last_received.find('\r\n')
				if ind != -1:
					fcom = self._last_received
					while ind != -1:
						self._last_received = fcom[:ind]
						self.exec_com()
						fcom = fcom[(ind + 2):]
						ind = fcom.find('\r\n')
					self._last_received = ''

		def exec_com(self):
			line = self._last_received
			cmd = self._last_received.split(' ')[0]
			params = self._last_received.split(' ')[1::]
			if cmd != 'STATUS':
				print('TSSERV: {%s}' % self._last_received)
			if cmd == 'HELLOTS':
				try:
					self.version = params[0].split('=')[1]
				except:
					self.version = '1.0.6'
				try:
					if params[2].split('=')[0] == 'key':
						self.key = params[2].split('=')[1]
				except: 
					try:
						self.key = params[1].split('=')[1]
					except:
						print('TSSERV: no HELLO key received')
			elif cmd == 'AUTH':
				self.auth_ok = True
			elif cmd == 'LOADRESP':
				self.files = line[line.find('{'):len(line)]
			elif cmd == 'EVENT':
				if params[0] == 'cansave':
					if int(self.index) == int(params[1].split('=')[1]):
						self.can_save = True
						self.save_info = [params[1], params[2]]
				elif params[0] == 'getuserdata':
					self.push('USERDATA [{"gender": 1}, {"age": 3}]')
					self.err = True
			elif cmd == 'START':
				try:
					self.content_url = urllib2.unquote(params[0].split('=')[1])
				except:
					self.content_url = params[0]
			elif cmd == 'RESUME':
				self.pause = False
			elif cmd == 'PAUSE':
				self.pause = True
			elif cmd == 'SHUTDOWN':
				self.active = False
			elif cmd == 'STATE':
				self.state = int(params[0])
				if self.state == 6:
					self.err = True
			elif cmd == 'STATUS':
				self._get_status(params[0])

		def _get_status(self, params):
			ss = re.compile(r'main:[a-z]+', re.S)
			s1 = re.findall(ss, params)[0]
			st = s1.split(':')[1]

		def end(self):
			self.active = False

	try:
		import _winreg
		try:
			t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r'Software\AceStream')
		except:
			t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r'Software\TorrentStream')
		port_file = os.path.join(os.path.dirname(_winreg.QueryValueEx(t, 'EnginePath')[0]), r'acestream.port')
		gf = open(port_file, 'r')
		tsport=int(gf.read())
	except:
			#return "X PORT"
			tsport=62062

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('127.0.0.1', tsport))
	#sock.settimeout(3)
	tsserv = _TSServ(sock)


class xPlayer(xbmc.Player):

	def __init__(self):
		self.tsserv = None
		self.active = True
		self.started = False
		self.ended = False
		self.paused = False
		self.buffering = False
		xbmc.Player.__init__(self)
		width, height = xPlayer.get_skin_resolution()
		w = width
		h = int(0.14 * height)
		x = 0
		y = (height - h) / 2
		self._ov_window = xbmcgui.Window(12005)
		self._ov_label = xbmcgui.ControlLabel(x, y, w, h, '', alignment=6)
		self._ov_background = xbmcgui.ControlImage(x, y, w, h, fs_dec(xPlayer.get_ov_image()))
		self._ov_background.setColorDiffuse('0xD0000000')
		self.ov_visible = False


	def onPlayBackPaused(self):
		xbmc.sleep(300)
		self.ov_show()
		self.ov_update('[B]I I[/B]')
		if __settings__.getSetting("split")=='true':  cnn=unmark(__settings__.getSetting("cplayed"))#.replace(" #1","")
		else:                                         cnn=colormark(__settings__.getSetting("cplayed"))#.replace(" #1","[COLOR 40FFFFFF] #1[/COLOR]")
		if __settings__.getSetting("epgosd")=='true':
			cgide=get_cgide(get_idx(__settings__.getSetting("cplayed")), 'serv')
		else:
			cgide=""
		self.ov_update("[B]I I\n[COLOR FFFFFF00]"+cnn+"[/COLOR][/B]\n"+xt(cgide))

	def onPlayBackStarted(self):
		self.ov_hide()

	def onPlayBackResumed(self):
		self.ov_hide()

	def onPlayBackEnded(self):
		pass
		if __settings__.getSetting("ACE_API")=='true':ACE2_end()
		
	def onPlayBackStopped(self):
		self.ov_hide()
		if __settings__.getSetting("ACE_API")=='true':ACE2_end()
		#xbmcplugin.endOfDirectory(handle, False, False)
		if __settings__.getSetting("epgon")=='true':
			#xbmc.sleep(600)
			#time.sleep(1)
			if __settings__.getSetting("frsup")=='true':xbmc.executebuiltin("Container.Refresh")
	
	def onPlayBackSpeedChanged(self, ofs):
		ct=int(time.strftime('%Y%m%d%H%M%S'))
		pt=int(__settings__.getSetting("play_tm"))
		tt=ct-pt
		if tt>3:
			if ofs>1: #след. канал
				self.ov_show()
				self.ov_update('[B]>>[/B]')
				__settings__.setSetting("n_play","0")
				__settings__.setSetting("lastnx",">")
				next ('>')
			elif ofs<0: # пред. канал
				self.ov_show()
				self.ov_update('[B]<<[/B]')
				__settings__.setSetting("n_play","0")
				__settings__.setSetting("lastnx","<")
				next ('<')
		else:
			print "<8"

	def onPlayBackSeek(self, ctime, ofs):
		ct=int(time.strftime('%Y%m%d%H%M%S'))
		pt=int(__settings__.getSetting("play_tm"))
		tt=ct-pt
		if tt>3:
			if ofs>0: #след. канал
				self.ov_show()
				self.ov_update('[B]>>[/B]')
				__settings__.setSetting("n_play","0")
				__settings__.setSetting("lastnx",">")
				next ('>')
			elif ofs<0: # пред. канал
				self.ov_show()
				self.ov_update('[B]<<[/B]')
				__settings__.setSetting("n_play","0")
				__settings__.setSetting("lastnx","<")
				next ('<')
		else:
			print "<3"

	def __del__(self):
		self.ov_hide()

	@staticmethod
	def get_ov_image():
		import base64
		ov_image = fs_enc(os.path.join(addon.getAddonInfo('path'), 'bg.png'))
		if not os.path.isfile(ov_image):
			fl = open(ov_image, 'wb')
			fl.write(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='))
			fl.close()
		return ov_image

	@staticmethod
	def get_skin_resolution():
		import xml.etree.ElementTree as Et
		skin_path = fs_enc(xbmc.translatePath('special://skin/'))
		tree = Et.parse(os.path.join(skin_path, 'addon.xml'))
		res = tree.findall('./extension/res')[0]
		return int(res.attrib['width']), int(res.attrib['height'])

	def ov_show(self):
		if not self.ov_visible:
			self._ov_window.addControls([self._ov_background, self._ov_label])
			self.ov_visible = True

	def ov_hide(self):
		if self.ov_visible:
			self._ov_window.removeControls([self._ov_background, self._ov_label])
			self.ov_visible = False

	def ov_update(self, txt=" "):
		if self.ov_visible:
			self._ov_label.setLabel(txt)#'[B]'+txt+'[/B]'


def getURL(url,Referer = 'http://viks.tv/'):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	req.add_header('Referer', Referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def GETimg(target, nmi):
	#lfimg=os.listdir(Logo)
	if nmi =='':
		#print target
		return target
	LogoDir=__settings__.getSetting("logodir")
	if LogoDir=="":LogoDir=Logo
	path1 = fs_enc(os.path.join(LogoDir,nmi+'.png'))
	path2 = fs_enc(os.path.join(Logo,nmi+'.png'))
	try:
		try:
			sz=os.path.getsize(path1)
			path=path1
		except:
			try:
				sz=os.path.getsize(path2)
				path=path2
			except:
				sz=0
				path=path2
		
		if sz > 0:
			return path
		else:
			if __settings__.getSetting("dllogo")=='false': return target
			
			pDialog = xbmcgui.DialogProgressBG()
			pDialog.create('Пазл ТВ', 'Загрузка логотипа: '+ nmi)
			req = urllib2.Request(url = target, data = None)
			req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
			resp = urllib2.urlopen(req)
			fl = open(path, "wb")
			fl.write(resp.read())
			fl.close()
			pDialog.close()
			return path
	except:
			print "err:  "+target
			return target


def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		#sn=http[s:]
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L

def debug(s):
	fl = open(ru(os.path.join( addon.getAddonInfo('path'),"test.txt")), "w")
	fl.write(s)
	fl.close()

def inputbox(t):
	skbd = xbmc.Keyboard(t, 'Название:')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		return SearchStr
	else:
		return t

def next_off (dr='>'):
	print "next ok"
	ccn=__settings__.getSetting("cplayed")
	print ccn
	try:
		SG=__settings__.getSetting("Sel_gr")
	except:
		SG=''
	if SG=='':
		SG='Все каналы'
		__settings__.setSetting("Sel_gr",SG)
	
	if SG!='Все каналы':
	
		CL=get_gr()
		Lnm=[]
		Lnu=[]
		Lid=[]
		
		L=get_all_channeles()
		
		
		if __settings__.getSetting("frslst")=='true':
				NCL=[]
				for b in CL: #10
					NCL.append(unmark(b))
			
				NL=[]
				for a in L: #1000
					if unmark(a['title']) in NCL:
						NL.append(a)
		else:
				#NCL=CL
				NL=L

		if __settings__.getSetting("noserv") == 'true':
				CL2=[]
				for i in CL:
					i2=uni_mark(i)
					if i2 not in CL2: CL2.append(i2)
				CL=CL2
		
		for k in CL:
			for i in NL:
					name  = i['title']
					name3 = i['title']
					if __settings__.getSetting("noserv") == 'true': 
											name3 = uni_mark(name3)
											#k = uni_mark(k)
					name2  = i['title']
					id=get_idx(name)
					#if __settings__.getSetting("split")=='true':
					#	urls=get_allurls(id, L)
					#else:
					#	urls=[]
					if k==name3 and id not in Lid:
						
						cover = i['img']
						if __settings__.getSetting("intlogo")=='true':  cover = GETimg(cover, id.replace("xttv",""))
						if __settings__.getSetting("split")=='true':
																		urls=get_allurls(id, NL)
																		name=unmark(name)#.replace(" #1","").replace(" #2","").replace(" #3","").replace(" #4","")
						else: urls = [i['url'],]
						
						#add_item ("[B]"+name+"[/B]", 'play', urls, name, cover)
						if id!="" and __settings__.getSetting("split")=='true':Lid.append(id)
						if name2 not in Lnm:
							Lnm.append(name2)
							Lnu.append([urls,name2,cover])
		if dr=='>':
			n=0
			drs='>> \n'
		else: 
			n=-2
			drs='<< \n'
		for p in Lnm:
			n+=1
			if n>=len(Lnm):n=0
			if p==ccn:
				if __settings__.getSetting("epgosd")=='true':
					cgide=get_cgide(get_idx(Lnu[n][1]), 'serv')
				else:
					cgide=""
				if __settings__.getSetting("split")=='true':nmc=unmark(Lnu[n][1])#.replace(" #1","").replace(" #2","").replace(" #3","").replace(" #4","")
				else: nmc=Lnu[n][1]
				Player.ov_update('[B]'+drs+"[COLOR FFFFFF00]"+nmc+"[/COLOR][/B]\n"+xt(cgide))
				play(Lnu[n][0],Lnu[n][1],Lnu[n][2], False)
	else:
		Player.ov_update('[B][COLOR FFFF0000][ ! ][/COLOR]\nПереключение каналов\nдоступно только в группах.[/B]')
		xbmc.sleep(3000)
		Player.ov_hide()

def next (dr='>'):
	ccn=__settings__.getSetting("cplayed")
	print ccn
	try:
		SG=__settings__.getSetting("Sel_gr")
	except:
		SG=''
	if SG=='':
		SG='Все каналы'
		__settings__.setSetting("Sel_gr",SG)
	
	if SG!='Все каналы':
		
		if dr=='>':
			Lnu=eval(__settings__.getSetting("next_itm"))
			drs='>> \n'
		else: 
			Lnu=eval(__settings__.getSetting("prev_itm"))
			drs='<< \n'
		if __settings__.getSetting("epgosd")=='true':cgide=get_cgide(get_idx(Lnu[1]), 'serv')
		else:cgide=""
		if __settings__.getSetting("split")=='true':nmc=unmark(Lnu[1])#.replace(" #1","")
		else: nmc=Lnu[1]
		Player.ov_update('[B]'+drs+"[COLOR FFFFFF00]"+nmc+"[/COLOR][/B]\n"+xt(cgide))
		play(Lnu[0],Lnu[1],Lnu[2], False)
	else:
		Player.ov_update('[B][COLOR FFFF0000][ ! ][/COLOR]\nПереключение каналов\nдоступно только в группах.[/B]')
		xbmc.sleep(3000)
		Player.ov_hide()


def set_np ():
	ccn=__settings__.getSetting("cplayed")
	try:SG=__settings__.getSetting("Sel_gr")
	except:SG=''
	if SG=='':
		SG='Все каналы'
		__settings__.setSetting("Sel_gr",SG)
	
	if SG!='Все каналы':
		CL=get_gr()
		Lnm=[]
		Lnu=[]
		Lid=[]
		
		L=get_all_channeles()
		
		if __settings__.getSetting("frslst")=='true':
				NCL=[]
				for b in CL: #10
					NCL.append(unmark(b))
			
				NL=[]
				for a in L: #1000
					if unmark(a['title']) in NCL:
						NL.append(a)
		else:
				NL=L

		if __settings__.getSetting("noserv") == 'true':
				CL2=[]
				for i in CL:
					i2=uni_mark(i)
					if i2 not in CL2: CL2.append(i2)
				CL=CL2
		
		for k in CL:
			for i in NL:
					name  = i['title']
					name3 = i['title']
					if __settings__.getSetting("noserv") == 'true': 
											name3 = uni_mark(name3)
											#k = uni_mark(k)
					name2  = i['title']
					id=get_idx(name)
					if k==name3 and id not in Lid:
						
						cover = i['img']
						if __settings__.getSetting("intlogo")=='true':  cover = GETimg(cover, id.replace("xttv",""))
						if __settings__.getSetting("split")=='true':
																		urls=get_allurls(id, NL)
																		name=unmark(name)#.replace(" #1","")
						else: urls = [i['url'],]
						
						if id!="" and __settings__.getSetting("split")=='true':Lid.append(id)
						if name2 not in Lnm:
							Lnm.append(name2)
							Lnu.append([urls,name2,cover])
		n=0
		for p in Lnm:
			if p==ccn:
				nn=n+1
				np=n-1
				if nn>=len(Lnm):nn=0
				if __settings__.getSetting("split")=='true':nmc=unmark(Lnu[n][1])#.replace(" #1","")
				else: nmc=Lnu[n][1]
				__settings__.setSetting("next_itm",repr(Lnu[nn]))
				__settings__.setSetting("prev_itm",repr(Lnu[np]))
			n+=1
	else:
		pass

if __settings__.getSetting("xplay")=='true': 
	Player=xPlayer()
else:
	Player=xbmc.Player()


def play_ace2(url):
	s=url.find('getstream?id=')
	if s<0: return ""
	PID=url[s+13:]
	print PID
	
	tsserv.start()
	tsserv.push('HELLOBG version=3')
	#command='HELLOBG version=3'
	#sock.send(command + '\r\n')
	n=0
	while not tsserv.version:
			print tsserv.version
			n+=1
			xbmc.sleep(200)
			if n>50: return "X HELLOBG"
	import hashlib
	sha1 = hashlib.sha1()
	pkey = tsserv.pkey
	sha1.update(tsserv.key + pkey)
	key = sha1.hexdigest()
	pk = pkey.split('-')[0]
	ready_key = 'READY key=%s-%s' % (pk, key)
	tsserv.push(ready_key)
	#sock.send(ready_key + '\r\n')

	n=0
	while not tsserv.auth_ok:
			n+=1
			xbmc.sleep(200)
			if n>50: return "X READY"
	#PID=url
	tsserv.push('START PID '+PID+' 0')
	while not tsserv.state == 2:
			n+=1
			xbmc.sleep(200)
			if n>50: return "X START"
	return tsserv.content_url

def ACE2_end():
	try:
		tsserv.push('SHUTDOWN')
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	except:
		pass


def play(urls, name ,cover, ref=True):
	#xbmcplugin.endOfDirectory(handle, False, False)
	
	#print urls
	if __settings__.getSetting("split")=='true':
		try:	SG=__settings__.getSetting("Sel_gr")
		except: SG=''
		if SG=='':
			SG='Все каналы'
		id=get_idx(name)
		L  = get_all_channeles()
		
		if __settings__.getSetting("frslst")=='true' and SG!='Все каналы':
				CL = get_gr()
				NCL=[]
				for b in CL: #10
					NCL.append(unmark(b))
				NL=[]
				for a in L: #1000
					if unmark(a['title']) in NCL:
						NL.append(a)
				L=NL
		urls=get_allurls(id, L)
	
	#print urls
	__settings__.setSetting("play_tm",time.strftime('%Y%m%d%H%M%S'))
	if ref==True:
		Player.stop()
	pDialog = xbmcgui.DialogProgressBG()
	try:pDialog.create('Пазл ТВ', 'Поиск потоков ...')
	except: pass
	Lpurl=[]
	for url in urls:
		#Lcurl=get_stream(url)
		try: Lcurl=get_stream(url)
		except:Lcurl=[]
		#print Lcurl
		try:Lpurl.extend(Lcurl)
		except:Lcurl=[]
	
	Lpurl2=[]
	Lm3u8 =[]
	Lrtmp =[]
	Lp2p  =[]
	Lourl =[]
	Ltmp=[]
	
	for i in Lpurl:
		if '.m3u8' in i and i not in Lm3u8:  Lm3u8.append(i)
		elif 'rtmp' in i and i not in Lrtmp: Lrtmp.append(i)
		elif '/ace/' in i and i not in Lp2p: 
				if __settings__.getSetting("ACE_API")=='true': Lp2p.append(play_ace2(i))
				else: Lp2p.append(i)
		elif i not in Ltmp:                  Lourl.append(i)
		Ltmp.extend(Lp2p)
		Ltmp.extend(Lm3u8)
		Ltmp.extend(Lrtmp)
		Ltmp.extend(Lourl)
	
	if __settings__.getSetting("ace_start")=='true' and len(Lp2p)>0: ASE_start()
	
	if __settings__.getSetting("p2p_start")=='true':
			Lpurl2.extend(Lp2p)
			Lpurl2.extend(Lm3u8)
			Lpurl2.extend(Lrtmp)
			Lpurl2.extend(Lourl)
	else:
			Lpurl2.extend(Lm3u8)
			Lpurl2.extend(Lourl)
			Lpurl2.extend(Lp2p)
			Lpurl2.extend(Lrtmp)
	
	if Lpurl2==[]:
		pDialog.close()
		showMessage('Пазл ТВ', 'Канал недоступен')
		if __settings__.getSetting("xplay")=='true': Player.ov_hide()
		__settings__.setSetting("cplayed",name)
		try:n_play=int(__settings__.getSetting("n_play"))
		except:n_play=0
		if n_play<3:
			set_np ()
			__settings__.setSetting("n_play",str(n_play+1))
			next (__settings__.getSetting("lastnx"))
		else:
			return ""
		
	else:
		playlist = xbmc.PlayList (xbmc.PLAYLIST_VIDEO)
		playlist.clear()
		
		n=1
		if len(Lpurl2)>1:n=3
		
		for j in range (0,n): # несколько копий в плейлист
			k=0
			for purl in Lpurl2:
				k+=1
				if __settings__.getSetting("split")=='true':name2=unmark(name)#.replace(" #1","")
				else:name2=colormark(name)#.replace(" #1","[COLOR 40FFFFFF] #1[/COLOR]")
				item = xbmcgui.ListItem(name2+" [ "+str(k)+"/"+str(len(Lpurl2))+" ]", path=purl, thumbnailImage=cover, iconImage=cover)
				playlist.add(url=purl, listitem=item)
		
		for j in range (0,3):
			purl2=os.path.join(addon.getAddonInfo('path'),"2.mp4")
			item = xbmcgui.ListItem(" > ", path=purl2, thumbnailImage=cover, iconImage=cover)
			playlist.add(url=purl2, listitem=item)
		
		
		#purl1="plugin://plugin.video.pazl.tv/?mode=next"
		#item = xbmcgui.ListItem(" > ", path=purl, thumbnailImage=cover, iconImage=cover)
		#playlist.add(url=purl2, listitem=item)
		
		pDialog.close()
		
		__settings__.setSetting("cplayed",name)
		
		Player.play(playlist)
		#time.sleep(1)
		#xbmc.sleep(1000)
		set_np ()
		#xbmcplugin.endOfDirectory(handle)
		
		if __settings__.getSetting("epgon")=='true' or __settings__.getSetting("xplay")=='true':
			while not xbmc.Player().isPlaying():
				time.sleep(1)
				#xbmc.sleep(1000)
			
			while  xbmc.Player().isPlaying():
				#time.sleep(0.5)
				xbmc.sleep(300)
				
				#print "========================  playing "+str(time.time())+"======================"
			if __settings__.getSetting("ACE_API")=='true': ACE2_end()
			if ref==True and __settings__.getSetting("epgon")=='true' and __settings__.getSetting("xplay")=='false':
				#xbmcplugin.endOfDirectory(handle)
				#xbmc.sleep(300)
				#showMessage("", "Обновляем список", times = 3000)
				if __settings__.getSetting("frsup")=='true':xbmc.executebuiltin("Container.Refresh")
				print "========================  Refresh ======================"

def play_b(urls, name ,cover, ref=True):
	if __settings__.getSetting("split")=='true':
		try:	SG=__settings__.getSetting("Sel_gr")
		except: SG=''
		if SG=='':
			SG='Все каналы'
		id=get_idx(name)
		L  = get_all_channeles()
		
		if __settings__.getSetting("frslst")=='true' and SG!='Все каналы':
				CL = get_gr()
				NCL=[]
				for b in CL: #10
					NCL.append(unmark(b))
				NL=[]
				for a in L: #1000
					if unmark(a['title']) in NCL:
						NL.append(a)
				L=NL
		urls=get_allurls(id, L)
	
	__settings__.setSetting("play_tm",time.strftime('%Y%m%d%H%M%S'))
	if ref==True:
		Player.stop()
	pDialog = xbmcgui.DialogProgressBG()
	try:pDialog.create('Пазл ТВ', 'Поиск потоков ...')
	except: pass
	Lpurl=[]
	for url in urls:
		try: Lcurl=get_stream(url)
		except:Lcurl=[]
		try:Lpurl.extend(Lcurl)
		except:Lcurl=[]
	
	Lpurl2=Lcurl
	
	if Lpurl2==[]:
		pDialog.close()
		showMessage('Пазл ТВ', 'Канал недоступен')
		if __settings__.getSetting("xplay")=='true': 
			Player.ov_hide()
			__settings__.setSetting("cplayed",name)
			try:n_play=int(__settings__.getSetting("n_play"))
			except:n_play=0
			if n_play<3:
				set_np ()
				__settings__.setSetting("n_play",str(n_play+1))
				next (__settings__.getSetting("lastnx"))
			else:
				return ""
		
	else:
		playlist = xbmc.PlayList (xbmc.PLAYLIST_VIDEO)
		playlist.clear()
		
		k=0
		for purl in Lpurl2:
				k+=1
				if __settings__.getSetting("split")=='true':name2=unmark(name)
				else:name2=colormark(name)
				item = xbmcgui.ListItem(name2+" [ "+str(k)+"/"+str(len(Lpurl2))+" ]", path=purl, thumbnailImage=cover, iconImage=cover)
				playlist.add(url=purl, listitem=item)
		
		pDialog.close()
		
		Player.play(playlist)
		if  __settings__.getSetting("xplay")=='true':
			__settings__.setSetting("cplayed",name)
			set_np ()
			while not xbmc.Player().isPlaying():
				time.sleep(1)
			while  xbmc.Player().isPlaying():
				xbmc.sleep(300)

def play_archive(urls, name ,cover, ref=True):
	#print urls
	Player.stop()
	pDialog = xbmcgui.DialogProgressBG()
	try:pDialog.create('Пазл ТВ', 'Поиск потоков ...')
	except: pass
	Lpurl=[]
	for url in urls:
		#Lcurl=get_stream(url)
		try: Lcurl=get_archive(url)
		except:Lcurl=[]
		#print Lcurl
		try:Lpurl.extend(Lcurl)
		except:Lcurl=[]
	
	Lpurl2=[]
	Lm3u8 =[]
	Lrtmp =[]
	Lp2p  =[]
	Lourl =[]
	Ltmp=[]
	
	for i in Lpurl:
		if '.m3u8' in i and i not in Lm3u8:  Lm3u8.append(i)
		elif 'rtmp' in i and i not in Lrtmp: Lrtmp.append(i)
		elif '/ace/' in i and i not in Lp2p: Lp2p.append(i)
		elif i not in Ltmp:                  Lourl.append(i)
		Ltmp.extend(Lp2p)
		Ltmp.extend(Lm3u8)
		Ltmp.extend(Lrtmp)
		Ltmp.extend(Lourl)
	
	if __settings__.getSetting("ace_start")=='true' and len(Lp2p)>0: ASE_start()
	
	if __settings__.getSetting("p2p_start")=='true':
			Lpurl2.extend(Lp2p)
			Lpurl2.extend(Lm3u8)
			Lpurl2.extend(Lrtmp)
			Lpurl2.extend(Lourl)
	else:
			Lpurl2.extend(Lm3u8)
			Lpurl2.extend(Lourl)
			Lpurl2.extend(Lp2p)
			Lpurl2.extend(Lrtmp)
	
	if Lpurl2==[]:
		pDialog.close()
		showMessage('Пазл ТВ', 'Канал недоступен')
		return ""
		
	else:
		playlist = xbmc.PlayList (xbmc.PLAYLIST_VIDEO)
		playlist.clear()
		
		n=1
		if len(Lpurl2)>1:n=3
		
		for j in range (0,n): # несколько копий в плейлист
			k=0
			for purl in Lpurl2:
				k+=1
				if __settings__.getSetting("split")=='true':name2=unmark(name)#.replace(" #1","")
				else:name2=colormark(name)#.replace(" #1","[COLOR 40FFFFFF] #1[/COLOR]")
				item = xbmcgui.ListItem(name2+" [ "+str(k)+"/"+str(len(Lpurl2))+" ]", path=purl, thumbnailImage=cover, iconImage=cover)
				playlist.add(url=purl, listitem=item)
		
		for j in range (0,5):
			purl2=os.path.join(addon.getAddonInfo('path'),"2.mp4")
			item = xbmcgui.ListItem(" > ", path=purl2, thumbnailImage=cover, iconImage=cover)
			playlist.add(url=purl2, listitem=item)
		
		
		pDialog.close()
		
		Player.play(playlist)
		xbmc.sleep(1000)
		xbmcplugin.endOfDirectory(handle)


def unmark(nm):
	for i in range (0,20):
		nm=nm.replace(" #"+str(i),"")
	return nm

def uni_mark(nm):
	for i in range (0,20):
		nm=lower(nm.replace(" #"+str(i),""))
	return nm

def colormark(nm):
	for i in range (0,20):
		nm=nm.replace(" #"+str(i),"[COLOR 40FFFFFF] #"+str(i)+"[/COLOR]")
	return nm

def get_ttv(url):
		http=getURL(url)
		#print http
		ss1='this.loadPlayer("'
		ss2='this.loadTorrent("'
		es='",{autoplay: true})'
		srv=__settings__.getSetting("p2p_serv")
		prt=__settings__.getSetting("p2p_port")
		
		try:
			if ss1 in http:
				CID=mfindal(http,ss1,es)[0][len(ss1):]
				lnk='http://'+srv+':'+prt+'/ace/getstream?id='+CID
				if len(CID)<30:lnk=''
				return lnk
			elif ss2 in http:
				AL=mfindal(http,ss2,es)[0][len(ss2):]
				lnk='http://'+srv+':'+prt+'/ace/getstream?url='+AL
				if len(AL)<30:lnk=''
				return lnk
			else: return ""
		except:
			return ""

def pars_m3u8(url):
	if __settings__.getSetting("pm3u")=='true':
		#print 'pars_m3u8'
		k1=url.find(".m3u8")
		tmp=url[:k1]
		k2=tmp.rfind("/")
		u2=url[:k2+1]
		try:http=getURL(url)
		except: return []
		L=http.splitlines()
		L2=[]
		for i in L:
			if '.m3u8' in i: L2.append(u2+i)
		if len(L2)>1:
			L2.reverse()
			return L2
		else: return [url,]
	else:
		return [url,]

def get_stream(url):
	for i in Lserv:
		ids=i[4:].replace('_','-')
		#print ids
		if 'torrent-tv.ru' in url and ids=='1ttv': ids='torrent-tv'
		if ids in url:
			print ids
			exec ("import "+i+"; serv="+i+".PZL()")
			return serv.Streams(url)
	return []


def get_archive(url):
	for i in Larh:
		ids=i[4:].replace('_','-')
		#print ids
		if ids in url:
			print ids
			exec ("import "+i+"; serv="+i+".ARH()")
			return serv.Streams(url)
	return []

def get_cepg(id, serv):
	try:
		E=get_inf_db(id)
		L=eval(E)
		itm=''
		n=0
		n2=0
		stt=int(__settings__.getSetting('shift'))-6
		h=int(time.strftime('%H'))
		m=int(time.strftime('%M'))
		
		cdata = int(time.strftime('%Y%m%d'))
		Ln=[]
		
		for i in L:
			if int(i['start_at'][:11].replace('-',''))==cdata: Ln.append(i)
		
		for n in range (1,len(Ln)):
			i=Ln[n-1]
			name=i['name']
			if '\\u0' in name: name=eval("u'"+i['name']+"'")
			try:
				h3 = int(L[n-1]['start_at'][11:13])-stt
				m3 = int(L[n-1]['start_at'][14:16])
			except:
				h3=h
				m3=m
			try:
				h2 = int(L[n]['start_at'][11:13])-stt
				m2 = int(L[n]['start_at'][14:16])
			except:
				h2=h
				m2=m
			t1=h*60+m
			t2=h2*60+m2
			if h3>23:hh=str(h3-24)
			elif h3>9:hh=str(h3)
			else:   hh="0"+str(h3)
			if m3>9:mm=str(m3)
			else:   mm="0"+str(m3)

			stm =hh+":"+mm
			t3=h3*60+m3
			if (t2>=t1 and t1>=t3) or n2>0: 
				n2+=1
				# ------ Прогресс бар
				if n2==1:
					
					vv=t2-t3
					if vv>600:vv=1440-vv
					vp=t2-t1
					if vp>600:vp=1440-vp
					prc=20-(vp*20/vv)
					
					if h2>23:hh2=str(h2-24)
					elif h2>9:hh2=str(h2)
					else:   hh2="0"+str(h2)
					if m2>9:mm2=str(m2)
					else:   mm2="0"+str(m2)
					etm =hh2+":"+mm2

					iii='---------------------------'
					pb1='[COLOR FF5555FF][B]'+iii[:prc]+"[/B][/COLOR]"
					pb2='[COLOR FFFFFFFF][B]'+iii[:20-prc]+"[/B][/COLOR]"
					
					itm+= " "+stm+" "+pb1+pb2+" "+etm+'\n'
					itm+='[COLOR FFFFFFFF][B]'+name+'[/B][/COLOR]'+'\n'
				else:
					itm+= '[COLOR FF888888]'+stm+' '+name+"[/COLOR]"'\n'
					if n2>3: return itm
		return itm
	except:
		return ""

def get_cgide(id, serv):
	if serv=='tivix': id='t'+id
	
	try:
		E=get_inf_db(id)
		L=eval(E)
		itm=''
		n=0
		n2=0
		stt=int(__settings__.getSetting('shift'))-6
		h=int(time.strftime('%H'))
		m=int(time.strftime('%M'))
		
		cdata = int(time.strftime('%Y%m%d'))
		Ln=[]
		
		for i in L:
			if int(i['start_at'][:11].replace('-',''))==cdata: Ln.append(i)
		
		for i in Ln:
			n+=1
			name=i['name']
			if '\\u0' in name: name=eval("u'"+name+"'")
			try:
				h3 = int(L[n-1]['start_at'][11:13])-stt
				m3 = int(L[n-1]['start_at'][14:16])
			except:
				h3=h
				m3=m
			try:
				h2 = int(L[n]['start_at'][11:13])-stt
				m2 = int(L[n]['start_at'][14:16])
			except:
				h2=h
				m2=m
			t1=h*60+m
			t2=h2*60+m2
			if h3>23:hh=str(h3-24)
			elif h3>9:hh=str(h3)
			else:   hh="0"+str(h3)
			if m3>9:mm=str(m3)
			else:   mm="0"+str(m3)

			stm =hh+":"+mm
			t3=h3*60+m3
			if t2>=t1 and t1>=t3: 
				#n2+=1
					#print '------ Прогресс бар'
				#if n2==1:
					
					#print t3 #нач
					#print t2 #кон
					#print t1 #вр
					vv=t2-t3
					#print str(t2)+'-'+str(t3)+'='+str(vv)
					if vv>800:vv=1440-vv
					vp=t2-t1
					#print str(t2)+'-'+str(t1)+'='+str(vp)
					if vp>800:vp=1440-vp
					prc=vp*100/vv
					#print prc
					p2=20*prc/100
					p1=20-p2
					
					if h2>23:hh2=str(h2-24)
					elif h2>9:hh2=str(h2)
					else:   hh2="0"+str(h2)
					if m2>9:mm2=str(m2)
					else:   mm2="0"+str(m2)
					etm =hh2+":"+mm2
					#print stm
					#print etm
					iii='----------------------------------'
					#pb1='[B][COLOR FF5555FF]'+iii[:prc]+"[/COLOR]"
					#pb2='[COLOR FFFFFFFF]'+iii[:20-prc]+"[/COLOR][/B]"
					
					pb1='[COLOR FF5555FF]'+iii[:p1]+"[/COLOR]"
					pb2='[COLOR FFFFFFFF]'+iii[:p2]+"[/COLOR]"
					
					itm+= stm+" [B]"+pb1+pb2+"[/B] "+etm+'[COLOR FFFFFFFF][B] '+name+'[/B][/COLOR]'#
					return itm
	except:
		return ""

def tvgide():
	try:SG=__settings__.getSetting("Sel_gr")
	except:SG=''
	
	if SG=='':
		SG='Все каналы'
		__settings__.setSetting("Sel_gr",SG)
	add_item ('[COLOR FF55FF55][B]Группа: '+SG+'[/B][/COLOR]', 'select_gr', "", 'tvgide')
	
	CL=get_gr()
	ttl=len(CL)
	if ttl==0:ttl=250
	Lnm=[]
	
	L=get_all_channeles()
	
	if SG=='Все каналы':
			for i in L:
				id = ""
				namec  = i['title']
				url   = i['url']
				id = get_idx(namec)
				cover = i['img']
				if __settings__.getSetting("intlogo") == 'true':  cover = GETimg(cover, id.replace("xttv",""))
				name=get_cgide(id, 'xmltv')
				
				if name!="" and name!=None and id not in Lnm:
						mr=name.find('[/COLOR]')
						pr='[COLOR 0000ff00][B]'+str(mr)+'[/B][/COLOR]'
						add_item (pr+name, 'play', [url,], namec, cover)
						if __settings__.getSetting("split")=='true': Lnm.append(id)

	else:
		
			if __settings__.getSetting("frslst")=='true':
				NCL=[]
				for b in CL: 
					NCL.append(unmark(b))
			
				NL=[]
				for a in L: 
					if unmark(a['title']) in NCL:
						NL.append(a)
				L=NL

			if __settings__.getSetting("noserv") == 'true':
				CL2=[]
				for i in CL:
					i2=uni_mark(i)
					if i2 not in CL2: CL2.append(i2)
				CL=CL2
		
		
			#for k in CL:
			for i in L:
					namec  = i['title']
					name3 = i['title']
					if __settings__.getSetting("noserv") == 'true': name3 = uni_mark(name3)
					if name3 in CL:
						url   = i['url']
						id = get_idx(namec)
						cover = i['img']
						if __settings__.getSetting("intlogo") == 'true':  cover = GETimg(cover, id.replace("xttv",""))
						name=get_cgide(id, 'xmltv')
						if name!="" and name!=None and id not in Lnm: 
							mr=name.find('[/COLOR]')
							pr='[COLOR 0000ff00][B]'+str(mr)+'[/B][/COLOR]'
							add_item (pr+name, 'play', [url,], namec, cover)
							if __settings__.getSetting("split")=='true': Lnm.append(id)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)




def set_num_cn(name):
	try:L=open_Groups()
	except:
		L=Ldf
		save_Groups(L)

	try:SG=__settings__.getSetting("Sel_gr")
	except:SG=''
	if SG=='':SG='Все каналы'
	
	if SG!='Все каналы':
		CLc=get_gr()
		n=CLc.index(name)
		sel = xbmcgui.Dialog()
		CLc.append(' - В конец списка - ')
		r = sel.select("Перед каналом:", CLc)
		CL=CLc[:-1]
		if r>=0 :#and r<len(CL)
			CL.remove(name)
			CL.insert(r, name)
			k=0
			for i in L:
				if i[0]==SG:
					L[k]=(SG,CL)
					save_Groups(L)
				k+=1
	xbmc.sleep(300)
	xbmc.executebuiltin("Container.Refresh")

def upd_canals_db(i):
	exec ("import "+i+"; serv="+i+".PZL()")
	return serv.Canals()

def upd_archive_db(i):
	exec ("import "+i+"; serv="+i+".ARH()")
	return serv.name2id()

def save_channels(n, L):
		ns=str(n)
		fp=xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'Channels'+ns+'.py'))
		fl = open(fp, "w")
		fl.write('# -*- coding: utf-8 -*-\n')
		fl.write('Channels=[\n')
		for i in L:
			fl.write(repr(i)+',\n')
		fl.write(']\n')
		fl.close()




def select_gr(ind):
	try:L=open_Groups()
	except:
		L=Ldf
		save_Groups(L)
	
	Lg=['Все каналы',]
	for i in L:
		Lg.append(i[0])
		
	if Lg!=[]:
		sel = xbmcgui.Dialog()
		r = sel.select("Группа:", Lg)
	if r>=0:
		SG=Lg[r]
		__settings__.setSetting("Sel_gr",SG)
	
	try:root_tm = float(__settings__.getSetting("root_tm"))
	except: root_tm = 0
	
	if __settings__.getSetting("frsup")=='true' or ind=="tvgide":
		#xbmc.sleep(300)
		print 'Refresh'
		xbmc.executebuiltin("Container.Refresh")

def list_gr():
	try:L=open_Groups()
	except:
		L=Ldf
		save_Groups(L)
	Lg=[]
	for i in L:
		Lg.append(i[0])
		
	return Lg

def get_gr():
	try:SG=__settings__.getSetting("Sel_gr")
	except:
		SG=''
	if SG=='':
		SG='Все каналы'
		__settings__.setSetting("Sel_gr",SG)
	try:L=open_Groups()
	except:L=[]
	CL=[]
	for i in L:
		if i[0]==SG: CL=i[1]
	return CL

def add(id):
	try:L=open_Groups()#L=open_Groups()
	except:L=Ldf
	Lg=[]
	for i in L:
		Lg.append(i[0])
		
	if Lg!=[]:
		sel = xbmcgui.Dialog()
		r = sel.select("Группа:", Lg)
		if id not in L[r][1]:
			L[r][1].append(id)
		
	save_Groups(L)

def open_Groups():
		fp=xbmc.translatePath(os.path.join(UserDir, 'UserGR.py'))
		
		try:sz=os.path.getsize(fp)
		except:sz=0
		if sz==0:
			save_Groups(Ldf)
			return Ldf
		
		fl = open(fp, "r")
		ls=fl.read().replace('\n','')#.replace('# -*- coding: utf-8 -*-Lgr=','')
		fl.close()
		return eval(ls)

def save_Groups(L):
		fp=xbmc.translatePath(os.path.join(UserDir, 'UserGR.py'))
		fl = open(fp, "w")
		#fl.write('# -*- coding: utf-8 -*-\n')
		#fl.write('Lgr=[\n')
		fl.write('[\n')
		for i in L:
			fl.write(repr(i)+',\n')
		fl.write(']\n')
		fl.close()


def rem(id):
	try:L=open_Groups()
	except:L=Ldf
	L2=[]
	for i in L:
			lj=[]
			for j in i[1]:
				if __settings__.getSetting("split")=='true': nm=id[:-1]
				else: nm=id
				if nm not in j:
				#if j!=id: 
					lj.append(j)
			L2.append([i[0],lj])
	save_Groups(L2)#__settings__.setSetting("Groups",repr(L2))
	xbmc.executebuiltin("Container.Refresh")

def add_gr():
	name=inputbox('')
	try:L=open_Groups()
	except:L=Ldf
	st=(name,[])
	if st not in L:L.append(st)
	save_Groups(L)

def rem_gr():
	try:L=open_Groups()
	except:L=Ldf
	Lg=[]
	for i in L:
		Lg.append(i[0])
		
	if Lg!=[]:
		sel = xbmcgui.Dialog()
		r = sel.select("Группа:", Lg)
	if r>=0:
		name=Lg[r]
	
		L2=[]
		for i in L:
			if i[0]!=name: L2.append(i)
		save_Groups(L2)#__settings__.setSetting("Groups",repr(L2))


def get_all_channeles():
	pDialog = xbmcgui.DialogProgressBG()
	L=[]
	for i in Lserv:
		serv_id=str(int(i[1:3]))
		if __settings__.getSetting("serv"+serv_id+"")=='true' :
			
			try: exec ("import Channels"+serv_id+"; Ls=Channels"+serv_id+".Channels")
			except:Ls=[]
			if Ls==[]: 
				pDialog.create('Пазл ТВ', 'Обновление списка каналов #'+serv_id+' ...')
				Ls=upd_canals_db(i)
				pDialog.close()
		else: Ls=[]
		L.extend(Ls)
	
	return L

def get_all_archive():
	pDialog = xbmcgui.DialogProgressBG()
	L=[]
	for i in Larh:
		serv_id=str(int(i[1:3]))
		if True:#__settings__.getSetting("serv"+serv_id+"")=='true' :
			
			try: exec ("import aid"+serv_id+"; Ds=aid"+serv_id+".n2id")
			except:Ds={}
			if Ds=={}: 
				pDialog.create('Пазл ТВ', 'Обновление архива #'+serv_id+' ...')
				Ds=upd_archive_db(i)
				pDialog.close()
		else: Ds={}
		if Ds !={}:
			Ds['srv_id']=i
			L.append(Ds)
	return L


if __settings__.getSetting("grincm")=='true':
	ContextGr=[('[B]Все каналы[/B]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=context_gr&name=Все каналы")'),]
	for grn in list_gr():
		ContextGr.append(('[B]'+grn+'[/B]','Container.Update("plugin://plugin.video.pazl.tv/?mode=context_gr&name='+urllib.quote_plus(grn)+'")'))
		ContextGr.append(('[COLOR FF55FF55][B]ПЕРЕДАЧИ[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=tvgide")'))


def add_item (name, mode="", path = Pdir, ind="0", cover=None, funart=None):
	if __settings__.getSetting("fanart")=='true':funart=cover
	else: funart=fanart
	if __settings__.getSetting("icons")!='true':cover=icon

	listitem = xbmcgui.ListItem(name, iconImage=cover)
	listitem.setProperty('fanart_image', funart)
	uri = sys.argv[0] + '?mode='+mode
	uri += '&url='  + urllib.quote_plus(repr(path))
	uri += '&name='  + urllib.quote_plus(xt(ind))
	uri += '&ind='  + urllib.quote_plus(str(ind))
	if cover!=None:uri += '&cover='  + urllib.quote_plus(cover)
	#if funart!=None and funart!="":uri += '&funart='  + urllib.quote_plus(funart)
	
	if mode=="play":
		if __settings__.getSetting("epgon")=='true':
				id = get_idx(ind)
				cepg=get_cepg(id,'xmltv').replace('&quot;','"').replace('&apos;',"'")
				if cepg !="":
					dict={"plot":cepg}
					try:listitem.setInfo(type = "Video", infoLabels = dict)
					except: pass

		fld=False
		#fld=True
		

		ContextCmd=[
			('[COLOR FF55FF55][B]ГРУППА[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=select_gr")'),
			('[COLOR FF55FF55][B]+ Добавить в группу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=add&name='+urllib.quote_plus(ind)+'")'),
			('[COLOR FFFF5555][B]- Удалить из группы[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=rem&name='+urllib.quote_plus(ind)+'")'),
			('[COLOR FF55FF55][B]<> Переместить канал[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=set_num&name='+urllib.quote_plus(ind)+'")'),
		('[COLOR FFFFFF55][B]* Обновить каналы[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=update")'),
			('[COLOR FFFFFF55][B]* Обновить программу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=updateepg")'),
			('[COLOR FF55FF55][B]ПЕРЕДАЧИ[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=tvgide")')]
		if test_rec(ind): ContextCmd.append(('[COLOR FF55FF55][B]АРХИВ[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=archive&name='+urllib.quote_plus(ind)+'")'))
			
		if __settings__.getSetting("grincm")=='true':listitem.addContextMenuItems(ContextGr, replaceItems=True)
		else:										listitem.addContextMenuItems(ContextCmd, replaceItems=True)
	
	elif mode=="play2" or mode=="select_date":
		fld=False
	else: 
		fld=True
		listitem.addContextMenuItems([
			('[COLOR FF55FF55][B]+ Создать группу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=addgr")'),
			('[COLOR FFFF5555][B]- Удалить группу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=remgr")'),
			('[COLOR FFFFFF55][B]* Обновить каналы[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=update")'),
			('[COLOR FFFFFF55][B]* Обновить программу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=updateepg")'),
			('[COLOR FFFFFF55][B]Управление каналами[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=grman")'),])
	xbmcplugin.addDirectoryItem(handle, uri, listitem, fld)#, ind)

def add_item_b (name, mode="", path = Pdir, ind="0", cover=None, funart=None):
	if __settings__.getSetting("fanart")=='true':funart=cover
	if __settings__.getSetting("icons")!='true':cover=icon

	listitem = xbmcgui.ListItem(name, iconImage=cover)
	if __settings__.getSetting("fanart")=='true': listitem.setProperty('fanart_image', funart)
	uri = sys.argv[0] + '?mode='+mode
	uri += '&url='  + urllib.quote_plus(repr(path))
	uri += '&name='  + urllib.quote_plus(xt(ind))
	uri += '&ind='  + urllib.quote_plus(str(ind))
	if cover!=None:uri += '&cover='  + urllib.quote_plus(cover)
	
	if mode=="play":
		fld=False
		ContextCmd=[
			('[COLOR FF55FF55][B]ГРУППА[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=select_gr")'),
			('[COLOR FF55FF55][B]+ Добавить в группу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=add&name='+urllib.quote_plus(ind)+'")'),
			('[COLOR FFFF5555][B]- Удалить из группы[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=rem&name='+urllib.quote_plus(ind)+'")'),
			('[COLOR FF55FF55][B]<> Переместить канал[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=set_num&name='+urllib.quote_plus(ind)+'")'),
		('[COLOR FFFFFF55][B]* Обновить каналы[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=update")'),
			('[COLOR FFFFFF55][B]* Обновить программу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=updateepg")'),
			('[COLOR FF55FF55][B]ПЕРЕДАЧИ[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=tvgide")')]
		ContextCmd.append(('[COLOR FF55FF55][B]АРХИВ[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=archive&name='+urllib.quote_plus(ind)+'")'))
		
		if __settings__.getSetting("grincm")=='true':listitem.addContextMenuItems(ContextGr, replaceItems=True)
		else:										listitem.addContextMenuItems(ContextCmd, replaceItems=True)
	
	elif mode=="play2" or mode=="select_date":
		fld=False
	else: 
		fld=True
		listitem.addContextMenuItems([
			('[COLOR FF55FF55][B]+ Создать группу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=addgr")'),
			('[COLOR FFFF5555][B]- Удалить группу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=remgr")'),
			('[COLOR FFFFFF55][B]* Обновить каналы[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=update")'),
			('[COLOR FFFFFF55][B]* Обновить программу[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=updateepg")'),
			('[COLOR FFFFFF55][B]Управление каналами[/B][/COLOR]', 'Container.Update("plugin://plugin.video.pazl.tv/?mode=grman")'),])
	xbmcplugin.addDirectoryItem(handle, uri, listitem, fld)


def root():
		#nt=time.time()
		try:	SG=__settings__.getSetting("Sel_gr")
		except: SG=''
			
		if SG=='':
			SG='Все каналы'
			__settings__.setSetting("Sel_gr",SG)
		add_item ('[COLOR FF55FF55][B]Группа: '+SG+'[/B][/COLOR]', 'select_gr', cover=icon)
		
		CL=get_gr()
		ttl=len(CL)
		if ttl==0:ttl=250
		Lnm=[]
		nserv=0
		for k in range (1,len(Lserv)+1):
			if __settings__.getSetting("serv"+str(k))=='true': nserv+=1
		
		L=get_all_channeles()
		
		intlogo =__settings__.getSetting("intlogo")
		grinnm  =__settings__.getSetting("grinnm")
		splitcn   =__settings__.getSetting("split")
		
		#ct= time.time()
		if SG=='Все каналы':
			for i in L:
					name  = i['title']
					url   = i['url']
					cover = i['img']
					id=get_idx(name)
					name2=add_rec(name)
					#if id=="": print unmark(lower(name))+" : "+url#.replace(" #1","")
					if intlogo == 'true': cover = GETimg(cover, id.replace("xttv",""))
					if grinnm =='true': name2=add_grn(name2)
					#else: name2=name
					
					if __settings__.getSetting("split")=='true' or nserv==1: name2=unmark(name2)#.replace(" #1","")
					else: name2=colormark(name2)#.replace(" #1","[COLOR 40FFFFFF] #1[/COLOR]")
					
					
					#print cover
					if id not in Lnm:
						add_item ("[B]"+name2+"[/B]", 'play', [url,], name, cover)
						if id!="" and splitcn =='true': Lnm.append(id)
			if __settings__.getSetting("abc")=='true':  xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)

		else: # Группы
			if __settings__.getSetting("frslst")=='true':
				NCL=[]
				for b in CL: #10
					NCL.append(unmark(b))
				NL=[]
				for a in L: #1000
					if unmark(a['title']) in NCL:
						NL.append(a)
			else:
				#NCL=CL
				NL=L
			
			if __settings__.getSetting("noserv") == 'true':
				CL2=[]
				for i in CL:
					i2=uni_mark(i)
					if i2 not in CL2: CL2.append(i2)
				CL=CL2
			
			for k in CL: #10
					for i in NL: #30
						name  = i['title']
						name2 = i['title']
						name3 = i['title']
						if __settings__.getSetting("noserv") == 'true': name3 = uni_mark(name3)
						id=get_idx(name)
						if k==name3 and id not in Lnm:
							cover = i['img']
							if intlogo == 'true':  cover = GETimg(cover, id.replace("xttv",""))
							#if splitcn =='true':	urls=get_allurls(id, NL) #30
							#else: 					
							urls = [i['url'],]
							
							if splitcn =='true' or nserv==1: name=unmark(name)#.replace(" #1","")
							else: name=colormark(name)#.replace(" #1","[COLOR 40FFFFFF] #1[/COLOR]")
							
							name=add_rec(name)
							add_item ("[B]"+name+"[/B]", 'play', urls, name2, cover)
							if id!="" and splitcn =='true':Lnm.append(id)
		
		if intlogo =='true': ctd=False
		else:                ctd=True
		#print "------ time -----"
		#print str(long(time.time())*100)
		#debug (str(time.time()-nt))
		xbmcplugin.endOfDirectory(handle, cacheToDisc=ctd)
		__settings__.setSetting("Sel_sday",'0')


def root_b():
		#nt=time.time()
		try:	SG=__settings__.getSetting("Sel_gr")
		except: SG=''
		if SG=='':
			SG='Все каналы'
			__settings__.setSetting("Sel_gr",SG)
		add_item_b ('[COLOR FF55FF55][B]Группа: '+SG+'[/B][/COLOR]', 'select_gr')
		
		CL=get_gr()
		Lnm=[]
		L=get_all_channeles()
		
		intlogo =__settings__.getSetting("intlogo")
		grinnm  =__settings__.getSetting("grinnm")
		splitcn =__settings__.getSetting("split")
		
		if SG=='Все каналы':
			for i in L:
					name  = i['title']
					url   = i['url']
					cover = i['img']
					if grinnm =='true': name2=add_grn(name2)
					add_item_b ("[B]"+name+"[/B]", 'play', [url,], name, cover)
			xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)

		else: # Группы
			NCL=[]
			for b in CL:
					NCL.append(unmark(b))
			NL=[]
			for a in L:
					if unmark(a['title']) in NCL:
						NL.append(a)
			for k in CL:
					for i in NL:
						name  = i['title']
						if k==name and name not in Lnm:
							cover = i['img']
							urls = [i['url'],]
							add_item_b ("[B]"+name+"[/B]", 'play', urls, name, cover)
							if splitcn =='true':Lnm.append(name)
		#print "------ time -----"
		#debug (str(time.time()-nt))
		xbmcplugin.endOfDirectory(handle)
		__settings__.setSetting("Sel_sday",'0')


def root_test():
	nt=time.time()
	for i in range (1,1000):
		name=str(i)
		urls=str(i)
		listitem = xbmcgui.ListItem(name, iconImage=icon)
		uri = sys.argv[0] + '?mode=play'
		#xbmcplugin.addDirectoryItem(handle, uri, listitem, True)
		
		add_item ("[B]"+name+"[/B]", 'play', urls, name)
	debug (str(time.time()-nt))
	xbmcplugin.endOfDirectory(handle)

def add_rec(name):
	for i in Larh:
		serv_id=str(int(i[1:3]))
		try: 
			exec ("import aid"+serv_id+"; dict=aid"+serv_id+".n2id")
			nm=lower(unmark(name))
			#print nm
			if nm in dict.keys():
				return name+" [COLOR 5FFF1010][R][/COLOR]"
		except: pass
	return name



def test_rec(name):
	for i in Larh:
		serv_id=str(int(i[1:3]))
		try: 
			exec ("import aid"+serv_id+"; dict=aid"+serv_id+".n2id")
			nm=lower(unmark(name))
			if nm in dict.keys():
				return True
		except: pass
	return False

def archive_off(name):#, sd='0'
	try:sd=__settings__.getSetting("Sel_sday")
	except: sd='0'
	if sd=="":sd='0'
	La=get_all_archive()
	for n2id in La:
		serv_id=n2id['srv_id']
		#try: 
		exec ("import "+serv_id+"; arh="+serv_id+".ARH()")
		#except:Ds={}
		

		#import p03_1ttv
		#arh=p03_1ttv.PZL()
		#n2id=arh.name2id()
		try:aid=n2id[lower(unmark(name))]
		except: aid=""
		#from aid3 import *
		#n2id
		if aid!="":
			ssec=int(sd)*24*60*60
			t=time.localtime(time.time() - ssec)
			#dt=time.strftime('-%d-%m-%Y',t).replace('-0','-')[1:]
			#print dt
			#dt='12-7-2016'
			add_item ('[COLOR FF10FF10][B]'+time.strftime('%d.%m.%Y',t)+" - "+unmark(name)+"[/B][/COLOR]", "select_date", 'url', '0' )
			L=arh.Archive(aid, t)
			for i in L:
				url=i['url']
				title=i['title']
				st=i['time']
				add_item (st+" - "+title, "play2", [url,], 'archive' )
			xbmcplugin.endOfDirectory(handle)

def archive(name):#, sd='0'
	try:sd=__settings__.getSetting("Sel_sday")
	except: sd='0'
	if sd=="":sd='0'
	La=get_all_archive()
	ssec=int(sd)*24*60*60
	t=time.localtime(time.time() - ssec)
	add_item ('[COLOR FF10FF10][B]'+time.strftime('%d.%m.%Y',t)+" - "+unmark(name)+"[/B][/COLOR]", "select_date", 'url', '0' )
	da={}
	Lm=[]
	for n2id in La:
		serv_id=n2id['srv_id']
		#try: 
		exec ("import "+serv_id+"; arh="+serv_id+".ARH()")
		#n2id=arh.name2id()
		try:aid=n2id[lower(unmark(name))]
		except: aid=""
		#from aid3 import *
		#n2id
		if aid!="":
			L=arh.Archive(aid, t)
			for i in L:
				#url=i['url']
				#title=i['title']
				st=i['time']
				#add_item (st+" - "+title, "play2", [url,], 'archive' )
				try: 
					i2=da[st]
					urls=i2['url']
					url=i['url']
					urls.append(url)
					i2['url']=urls
					da[st]=i2
				except: 
					url=i['url']
					i['url']=[url,]
					da[st]=i
	for d in da.keys():
			urls=da[d]['url']
			title=da[d]['title']
			st=da[d]['time']
			add_item (st+" - "+title, "play2", urls, 'archive' )
			
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)


def select_date():
		L=[]
		for i in range (0,10):
			ssec=i*24*60*60
			t=time.localtime(time.time() - ssec)
			st=time.strftime('%d.%m.%Y',t)
			L.append(st)
		sel = xbmcgui.Dialog()
		r = sel.select("Дата:", L)
		__settings__.setSetting("Sel_sday",str(r))
		xbmc.executebuiltin("Container.Refresh")



def get_allurls_off(xid, L):
	id=xid[1:]
	L2=[]
	for i in xmlid.items():
		if i[1]==id:
			L2.append(i[0])
	L3=[]
	for j in L:
		name = unmark(lower(j['title']))#.replace(" #1","")
		if name in L2:
			L3.append(j['url'])
	return L3

def get_allurls(xid, L):
	L3=[]
	for j in L:
		name = j['title']
		id=get_idx(name)
		if id == xid and id !="":
			L3.append(j['url'])
	return L3

def add_grn(name):
	try:L=open_Groups()
	except:L=[]
	for i in L:
		gr=i[0]
		if name.replace(" [COLOR 5FFF1010][R][/COLOR]", "") in i[1]: name=name+"  [COLOR 40FFFFFF]["+gr+"][/COLOR]"
	return name


def get_id_off(url):
		try:
			if 'viks.tv' in url:ss='viks.tv/'
			else:               ss='tivix.net/'
			es='-'
			id=mfindal(url,ss,es)[0][len(ss):]
			return id
		except:
			return '0'

def get_idx(name):
	name=unmark(lower(name))#.replace(" #1","").replace(" #2","").replace(" #3","").replace(" #4","")
	try:
		id="x"+xmlid[name]
	except: 
		id=''
	return id

# ------------------------------------ БД ------------------------------------------------
import sqlite3 as db
db_name = os.path.join( addon.getAddonInfo('path'), "epg.db" )
c = db.connect(database=db_name)
cu = c.cursor()
def add_to_db(n, item):
		item=item.replace("'","XXCC").replace('"',"XXDD")
		err=0
		tor_id="n"+n
		litm=str(len(item))
		try:
			cu.execute("DROP TABLE "+tor_id+";")
			c.commit()
		except: pass
		try:
			cu.execute("CREATE TABLE "+tor_id+" (db_item VARCHAR("+litm+"), i VARCHAR(1));")
			c.commit()
		except: 
			err=1
			print "Ошибка БД"
		if err==0:
			cu.execute('INSERT INTO '+tor_id+' (db_item, i) VALUES ("'+item+'", "1");')
			c.commit()
			#c.close()

def get_inf_db(n):
		tor_id="n"+n
		cu.execute(str('SELECT db_item FROM '+tor_id+';'))
		c.commit()
		Linfo = cu.fetchall()
		info=Linfo[0][0].replace("XXCC","'").replace("XXDD",'"')
		return info
# ----------------------------------- данные ----------------------------------------------------
def dload_epg_xml():
	try:
			target='http://api.torrent-tv.ru/ttv.xmltv.xml.gz'
			#print "-==-=-=-=-=-=-=- download =-=-=-=-=-=-=-=-=-=-"
			fp = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'tmp.zip'))
			
			req = urllib2.Request(url = target, data = None)
			req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
			resp = urllib2.urlopen(req)
			fl = open(fp, "wb")
			fl.write(resp.read())
			fl.close()
			#print "-==-=-=-=-=-=-=- unpak =-=-=-=-=-=-=-=-=-=-"
			xml=ungz(fp)
			#print "-==-=-=-=-=-=-=- unpak ok =-=-=-=-=-=-=-=-=-=-"
			#os.remove(fp)
			return xml
	except Exception, e:
			print 'HTTP ERROR ' + str(e)
			return ''


def ungz(filename):
	import gzip
	with gzip.open(filename, 'rb') as f:
		file_content = f.read()
		return file_content

def unzip(filename):
	from zipfile import ZipFile
	fil = ZipFile(filename, 'r')
	for name in fil.namelist():
		f=fil.read(name)
		return f

def ASE_start():
	srv=__settings__.getSetting("p2p_serv")
	prt=__settings__.getSetting("p2p_port")
	lnk='http://'+srv+':'+prt+'/webui/api/service?method=get_version&format=jsonp&callback=mycallback'#getstream?id='+CID
	try:
		http=getURL(lnk)
		return False
	except:
		#showMessage('Пазл ТВ', 'Запуск Ace Stream')
		pDialog.create('Пазл ТВ', 'Запуск Ace Stream ...')
		pDialog.update(0, message='Запуск Ace Stream ...')
		start_linux()
		start_windows()
		for i in range (0,10):
			pDialog.update(i*10, message='Запуск Ace Stream ...')
			xbmc.sleep(1500)
			try:
				http=getURL(lnk)
				pDialog.close()
				return True
			except: pass
		pDialog.close()
		return False

def start_linux():
        import subprocess
        try:
            subprocess.Popen(['acestreamengine', '--client-console'])
        except:
            try:
                subprocess.Popen('acestreamengine-client-console')
            except: 
                try:
                    xbmc.executebuiltin('XBMC.StartAndroidActivity("org.acestream.engine")')
                except:
                    return False
        return True
    
def start_windows():
        try:
            import _winreg
            try:
                t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r'Software\AceStream')
            except:
                t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r'Software\TorrentStream')
            path = _winreg.QueryValueEx(t, r'EnginePath')[0]
            os.startfile(path)
            return True
        except:
            return False


def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

params = get_params()

try:mode = urllib.unquote_plus(params["mode"])
except:mode =""
try:name = urllib.unquote_plus(params["name"])
except:name =""
try:url = eval(urllib.unquote_plus(params["url"]))
except:url =[]
try:cover = urllib.unquote_plus(params["cover"])
except:cover =""
try:ind = urllib.unquote_plus(params["ind"])
except:ind ="0"
pDialog = xbmcgui.DialogProgressBG()

if mode==""         : #root
	if __settings__.getSetting("boost")=='true': root_b()
	else: root()

if mode=="context_gr"  :
		__settings__.setSetting("Sel_gr",name)
		xbmc.sleep(300)
		xbmc.executebuiltin("Container.Refresh")

if mode=="updateepg"   :
			add_to_db ("udata", str(0))
			xbmcplugin.endOfDirectory(handle, False, False)

if mode=="grman"   :
	import GrBox
	GrBox.run("GrBox")

if mode=="tvgide"   : tvgide()
if mode=="add"      : add(name)
if mode=="rem"      : rem(name)
if mode=="addgr"    : add_gr()
if mode=="remgr"    : rem_gr()
if mode=="set_num"  : set_num_cn(name)
if mode=="update"   : 
			xbmcplugin.endOfDirectory(handle, False, False)
			pDialog = xbmcgui.DialogProgressBG()
			pDialog.create('Пазл ТВ', 'Обновление списка каналов ...')
			for i in Lserv:
				serv_id=str(int(i[1:3]))
				if __settings__.getSetting("serv"+serv_id)=='true' :
						pDialog.update(int(serv_id)*100/len(Lserv), message='Обновление списка каналов #'+serv_id+' ...')
						Ls=upd_canals_db(i)
			pDialog.close()
			xbmc.executebuiltin("Container.Refresh")

if mode=="select_gr": select_gr(ind)
if mode=="play"     : 
	if __settings__.getSetting("boost")=='true': play_b(url, name, cover)
	else: play(url, name, cover)
if mode=="play2"    : play_archive(url, name, cover)
if mode=="next"     : 
	#video=xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), '1.wmv'))
	xbmc.executebuiltin('Container.Update("plugin://plugin.video.pazl.tv/?mode=next2")')

if mode=="next2"     : next ('>')
if mode=="archive"   : archive(name)#, ind
if mode=="select_date": select_date()
c.close()
#debug (str(time.time()-nt))
