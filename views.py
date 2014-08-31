from django.shortcuts import render_to_response
from models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ipware.ip import get_real_ip
import requests
import json
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Count
import random
flag_list=['ac', 'ae', 'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'ap', 'aq', 'ar', 'as', 'at', 'au', 'aw', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bm', 'bn', 'bo', 'br', 'bs', 'bt', 'bv', 'bw', 'by', 'bz', 'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'cr', 'cs', 'cu', 'cv', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'ee', 'eg', 'eh', 'er', 'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'mg', 'mh', 'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'nc', 'ne', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'pa', 'pe', 'pf', 'pg', 'ph', 'philippines_flagsm', 'pk', 'pl', 'pm', 'pn', 'pr', 'priv-172', 'priv-192', 'priv-localhost', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'ru', 'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'st', 'sv', 'sy', 'sz', 'tc', 'td', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'tt', 'tv', 'tw', 'tz', 'ua', 'ug', 'uk', 'um', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu', 'wf', 'ws', 'xx', 'ye', 'yt', 'yu', 'za', 'zm', 'zw']
from django.db.models import Count
import hoover
import re
from datetime import datetime
import logging
from random import shuffle

from django.views.generic import TemplateView, FormView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

log = logging.getLogger('MyApp')
logging.addLevelName(logging.INFO, 'info')
log.setLevel(logging.INFO)

logglyhandler = hoover.LogglyHttpHandler(token='1a7691aa-097d-4c0e-a0e8-7b45dd7b170f')
logglyhandler.setLevel(logging.WARNING)
logglyformatter = logging.Formatter('{"time": "%(asctime)s", "level":"%(levelname)s",' \
 '"error_number": "%(error_number)s", "message":"%(message)s", "other":"%(other)s"}' ) 
logglyhandler.setFormatter(logglyformatter)
log.addHandler(logglyhandler)


from logentries import LogentriesHandler

logenter = LogentriesHandler('1a7691aa-097d-4c0e-a0e8-7b45dd7b170f')
logenter.setFormatter(logglyformatter)
log.addHandler(logenter)



class HttpResponseBadRequest(HttpResponse):
    status_code = 400

def logglier(msg, state=0, number=0, other=' '):
	try:
		if state==0:
			log.error(msg, extra={'error_number':number, 'other':str(other)})
		else:
			log.critical(msg, extra={'error_number':number, 'other':str(other)})
	except Exception as e:
		pass
'''
def home(request):
	args = {}
	args.update(csrf(request))
	#args['count'] = WebsiteStatus.objects.count()
	return render_to_response('index.html', args)

def getinvolved(request):
	args = {}
	args.update(csrf(request))
	#rgs['count'] = WebsiteStatus.objects.count()
	return render_to_response('getinvolved.html', args)
'''

@csrf_exempt
def news(request):
	log.debug(request)
	if request.method == 'POST': 
		try:
			data = request.POST
			title = data['title']
			agency = data['agency']
			description = data['description']
			link_to_news = data['link_to_news']
			try:
				published_date = data['published_date']
			except:
				published_date = None
		except Exception as e:
			return HttpResponseBadRequest(e)
		try:
			News.objects.create(link_to_news=link_to_news, title=title, agency=agency, description= description)
		except Exception as e:
			return HttpResponseBadRequest("bad link to news.")	
		return HttpResponse()
	else:
		result = {}
		top_news=News.objects.all()[:50]
		result['news']= [{"news_title": n.title, "description": n.description, "link":n.link_to_news, "agency":n.agency} for n in top_news]
		return HttpResponse(json.dumps(result, indent=2), content_type="application/json")

def software_version(request):
	#args = {}
	#args.update(csrf(request))
	#rgs['count'] = WebsiteStatus.objects.count()
	return HttpResponse('1.1.0')

#from difflib import get_close_matches as mtch
def mkReporter(ip_add):
	if not ip_add:
		logglier("no ip address", number=100)
		ip_add="0.0.0.0"
	else:
		logglier("ip address", number=10000, other=ip_add)
	webip='http://ip-api.com/json/'+ip_add

	try:
		r=requests.get(webip)
		if r.status_code==200 and r.json()['status']=='success':
			isp=r.json()['isp']
			#all_countries= [c.name for c in Country.objects.all()]
			#con=mtch(str(r.json()['country']), all_countries)[0]
			country=Country.objects.get(alpha2=(r.json()['countryCode']))
			region=str(r.json()['region'])+"@"+str(r.json()['country'])
			city=r.json()['city']
			zipcode=r.json()['zip']
			lat=r.json()['lat']
			lon=r.json()['lon']
			org=r.json()['org']
		else:
			logglier("ip-api didn't work", number=102, state=1)
			isp=region=city=zipcode=lat=lon=org=country='None'
	except Exception as e:
		logglier("exception webip", number=134, state=1, other=e)
		isp=region=city=zipcode=lat=lon=org='None'
		r, created = IPidentity.objects.get_or_create(ip_add=ip_add, isp=isp,region=region,city=city,zipcode=zipcode,lat=lat,lon=lon,org=org)
		return r
	
	try:
		r, created = IPidentity.objects.get_or_create(ip_add=ip_add, isp=isp,country=country,region=region,city=city,zipcode=zipcode,lat=lat,lon=lon,org=org)
	except Exception as e:
		logglier("mkReporter exception", number=104, state=1, other=e)
	return r

import tldextract
def validRedirect(history):
	first=history[0]
	last=history[-1]
	if "blogspot" in first and "blogspot" in last:
		return True
	first=tldextract.extract(first)
	last=tldextract.extract(last)
	if first.domain!=last.domain:
		return False
	else:
		return True

def decide_one_report(report):   #timeout=0  open=1  partial=2 blocked=3  
	if report.final_url == '0': #timeout
		new_decision=0
	elif report.length < 1000: #tiny webpage, blocked
		new_decision=3
	elif report.history != '[]':
		historyplus=re.findall(r"u\'([A-Za-z0-9\/\:\.]+)\'",report.history)
		historyplus.append(report.final_url)
		if validRedirect(historyplus):
			new_decision=1
		else:
			new_decision=3
	else:
		new_decision=1
	return new_decision 

def makeDecision(url, country): 
	all_reports=ReportDecision.objects.filter(report__uid__chosen_country=country, report__url=url)
	decisions=[x.decision for x in all_reports]
	if decisions:
		blocked=(3 in decisions) or decisions.count(0)>len(decisions)/2
		op=(1 in decisions)
		if op and blocked:
			decision=2
		elif op:
			decision=1
		elif blocked:
			decision=3
		else:
			decision=0
		ud, created=UrlDecision.objects.get_or_create(country=country, url=url)
		ud.decision=decision
		ud.save()
	else:
		logglier("no reports", number=355, state=1, other=(url, country))

def processReport(repList, ipidentity, uid):
	for rep in repList:
		try:
			u=Url.objects.get(address=rep["url"])
			content_object= PageContent.objects.create(content=rep["content"])
			report=UrlReport.objects.create(ipidentity=ipidentity, uid=uid, epoch=rep["epoch"], url=u,
				final_url=rep["final_url"], length=rep["length"], elapsed=rep["elapsed"], history=rep["history"], 
				headers=rep["headers"], cookies=rep["cookies"], status_code= rep["status_code"], content=content_object)
			
			new_decision = decide_one_report(report)
			flag= (new_decision==3)
			ReportDecision.objects.create(report=report, decision=new_decision, flag= flag)

			if ipidentity.country.id == uid.chosen_country.id:
				makeDecision(u, uid.chosen_country)

		except Exception as e:
			logglier("processReport. exception. ", number=123, state=1, other=e)

@csrf_exempt
def report(request):
	logglier("all", number=10231, other=request)
	if request.method == 'POST':
		try:
			data = json.loads(request.raw_post_data)
			reportList = data['report']
			uid = int(data['uid'])
		except Exception as e:
			logglier("report bad request", number=150, other=e)
			return HttpResponseBadRequest(e)
		try:
			uid = ReporterUID.objects.get(uid=uid)
		except Exception as e:
			logglier("report bad request", number=152, other=e)
			return HttpResponseBadRequest()

		if len(reportList)>0 :
			ip = get_real_ip(request)
			ipidentity = mkReporter(ip)

			if ipidentity.country.id != uid.chosen_country.id:
				logglier("NON MATCHING COUNTRY", number=10006, state=1)

			processReport(reportList, ipidentity, uid)
			return HttpResponse()
		else:
			logglier("empty reportlist", number=106, state=1)
			return HttpResponseBadRequest()
	else:
		return HttpResponse()

from time import time
@csrf_exempt
def websiteGenerator(request):
	return HttpResponseBadRequest()
	logglier("request", number=1000, other=request)
	if request.method == 'POST':
		try:
			data=json.loads(request.raw_post_data)
			chosen_country=data['country']
			email=data['email']
		except Exception as e:
			logglier("report bad request", number=150, other=e)
			return HttpResponseBadRequest(e)

		ip = get_real_ip(request)
		ipidentity = mkReporter(ip)

		try:
			chosen_country=Country.objects.get(name=chosen_country)
		except Exception as e:
			chosen_country=Country.objects.get(id=1)
			logglier("websitegenerator chosen country problem", number=2014, state=1, other=e)	

		uid,_ = ReporterUID.objects.get_or_create(chosen_country= chosen_country, email= email,ipidentity=ipidentity)
		return HttpResponse(json.dumps({'uid':uid.uid}), content_type="application/json")
	elif 'uid' in request.GET:
		try:
			uid=int(request.GET['uid'])
		except Exception as e:
			logglier("websitegenerator bad request", number=150, other=e)
			return HttpResponseBadRequest("bad params!")
		try:
			load_count = int(request.GET['load_count'])
		except:
			load_count = Url.objects.all().exclude(group=5).count()

		# get reports from this uid in the last 5 days
		# use urls that are not reported
		# or empty []
		lst=[l.address for l in Url.objects.all().exclude(group=5)]
		shuffle(lst)
		lst=lst[:load_count]
		return HttpResponse(json.dumps({'websites':lst, 'uid':uid}), content_type="application/json")		
	else:
		logglier("websiteGenerator bad request", number=13350)
		return HttpResponseBadRequest("Missing params")
		
@csrf_exempt
def report_debug(request):
	if request.method == 'POST':
		try:
			data=json.loads(request.raw_post_data)
			uid=data['uid']
			reportList=data['report']
		except Exception as e:
			return HttpResponseBadRequest("There should be a 'report' parameter which is a list of 'reports', and also 'country' and 'email' and 'uid' params. \n The error is :"+str(e))

		if len(reportList)>0 :
			x=[]
			for rep in reportList:
				try:
					x.append((rep["url"], rep["content"], rep["epoch"], rep["final_url"], rep["length"], rep["elapsed"], rep["history"], rep["headers"], rep["cookies"]))
				except Exception as e:
					return HttpResponseBadRequest("each report should have all these values: rep[url], rep[content], rep[epoch], rep[final_url], rep[length], rep[elapsed], rep[history], rep[headers], rep[cookies] \n The error is "+str(e))
				
			return HttpResponse()
		else:
			return HttpResponseBadRequest("empty reportlist. The report param should be a list of reports.")
	else:
		return HttpResponse("what do you GET?")

def data(request):
	if 'country' in request.GET and 'v' in request.GET:
		version=request.GET['v']
		cty=request.GET['country']
		try:
			c=Country.objects.get(alpha2=cty)
		except:
			return HttpResponse(json.dumps({'status':'ERROR', 'message':'wrong country param.'}, indent=2), content_type="application/json")

		if version=='0':   #horizonal stacked graph
			result={}

			lst=UrlDecision.objects.filter(country=c)
			cats=list(set([s.url.category for s in lst]))

			result['title']="Blocked Vs. Open Pages Of All The Websites Scanned"
			data=[]
			blocked=UrlDecision.objects.filter(country=c, decision=3).values('url__category').annotate(Count("id")).order_by()
			blk2=[]
			if len(blocked)>0:
				for b in blocked:
					blk2.append({'x':str(b.pop('url__category')), 'y': int(b.pop('id__count'))})

			partial=UrlDecision.objects.filter(country=c, decision=2).values('url__category').annotate(Count("id")).order_by()
			
			partial2=[]
			if len(partial)>0:
				for b in partial:
					partial2.append({'x':str(b.pop('url__category')), 'y': int(b.pop('id__count'))})

			opn=UrlDecision.objects.filter(country=c, decision=1).values('url__category').annotate(Count("id")).order_by()
			opn2=[]
			if len(opn)>0:
				for b in opn:
					opn2.append({'x':str(b.pop('url__category')), 'y': int(b.pop('id__count'))})
				
			if blk2 or partial2 or opn2:
				blkkeys=[k['x'] for k in blk2]
				partialkeys=[k['x'] for k in partial2]
				opnkeys=[k['x'] for k in opn2]

				for k in partial2:
					if not k['x'] in blkkeys:
						blk2.append({'x':k['x'], 'y': 0})
						blkkeys.append(k['x'])
					if not k['x'] in opnkeys:
						opn2.append({'x':k['x'], 'y': 0})
						opnkeys.append(k['x'])
						
				for k in blk2:
					if not k['x'] in partialkeys:
						partial2.append({'x':k['x'], 'y': 0})	
						partialkeys.append(k['x'])					
					if not k['x'] in opnkeys:
						opn2.append({'x':k['x'], 'y': 0})
						opnkeys.append(k['x'])

				for k in opn2:
					if not k['x'] in partialkeys:
						partial2.append({'x':k['x'], 'y': 0})
						partialkeys.append(k['x'])						
					if not k['x'] in blkkeys:
						blk2.append({'x':k['x'], 'y': 0})
						blkkeys.append(k['x'])

				blk2.sort(key=lambda x:x['x'])
				partial2.sort(key=lambda x:x['x'])
				opn2.sort(key=lambda x:x['x'])

				data.append({"key": "Blocked", "color": "#BD362F", "values": blk2})
				data.append({"key": "Partially/Inconsistently Blocked", "color": "#BD3620", "values": partial2})
				data.append({"key": "Open", "color": "#51A351", "values": opn2})

				result['data']=data
			if len(data)>0:
				result['status']='OK'
				result['v']=int(version)
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
			else:
				return HttpResponse(json.dumps({'v':int(version), 'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")

		elif version=='1': # all data
			result={}
			dic=model_to_dict(c)
			for key, val in dic.items():
				if val==None: del dic[key]

			items=[]
			if "internet_code" in dic: items.append("Internet Code: "+dic["internet_code"])
			if "population" in dic: items.append("Country population: "+dic["population"])
			if "population_with_internet" in dic: items.append("Population with internet access: "+dic["population_with_internet"])
			if "median_age" in dic: items.append("Country median age: "+dic["median_age"])
			if "upload_speed" in dic: items.append("Average Internet Upload Speed: "+dic["upload_speed"])
			if "download_speed" in dic: items.append("Average Internet Download Speed: "+dic["download_speed"])
			if "press_freedom_rank" in dic: items.append("Press Freedom Index according to Reporters Without Borders: "+ str(dic["press_freedom_rank"]))

			result['title']="More Information"
			result['bullets']=items

			if len(items)>0:
				result['status']='OK'
				result['v']=int(version)
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
			else:
				return HttpResponse(json.dumps({'v':int(version),'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")

		elif version=='2': # quick details

			result={}

			lst=UrlDecision.objects.filter(country=c)
			op=[o for o in lst if o.decision==1]
			partial=[o for o in lst if o.decision==2]
			cl=[gg for gg in lst if gg.decision==3]
			timeout=[gg for gg in lst if gg.decision==0]

			items=[]
			items.append(str(c.name))
			if c.official_name!=None: items.append('Official Name: '+ str(c.official_name) )
			if len(cl)>0: items.append('Number of websites blocked: '+ str(len(cl)))
			if len(timeout)>0: items.append('Number of websites inaccessible due to timeout: '+ str(len(timeout)))
			if len(partial)>0: items.append('Number of websites partially or inconsistently blocked: '+ str(len(partial)))
			if len(op)>0: items.append('Number of websites open: '+ str(len(op)))
			if not (op or cl or partial): items.append("We don't have any data from this location. <strong>We need your help.</strong>")
			numReporters=Reporter.objects.filter(country=c).count()
			if numReporters>0: 
				last_reporter=list(Reporter.objects.filter(country=c))[-1]
				timeofreport=list(UrlReport.objects.filter(reporter=last_reporter))[-1].epoch
				timeofreport=datetime.fromtimestamp(timeofreport).strftime('%Y-%m-%d')

				items.append("We have had {0} reporters from this country. Last one was on {1}.".format(numReporters,timeofreport))

			items.append("Please go to our <a href=\"http://www.blockedonline.com/getinvolved\">Get Involved</a> page and help us gather more data.")

			result['title']="Quick Summary"
			result['bullets']=items

			if len(items)>0:
				result['status']='OK'
				result['v']=int(version)
				
				if c.alpha2.lower() in flag_list:
					result['flag']="http://blockedonline.github.io/index_files/flags/{0}.gif".format(c.alpha2.lower())
				else:
					result['flag']="http://blockedonline.github.io/index_files/flags/0.gif"
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
			else:
				return HttpResponse(json.dumps({'v':int(version),'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")

		elif version=='3': # Top websites
			result={}

			lst=UrlDecision.objects.filter(country=c, url__base_url=None)
			blocked=[o for o in lst if o.decision==3]

			items=sorted(blocked, key=lambda x: x.url.global_rank)
			items=items[:10]
			items=[x.url.address for x in items]

			result['title']="Top Blocked Websites With Highest Global Rank"
			result['websites']=items

			
			if len(items)>0:
				result['status']='OK'
				result['v']=int(version)
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
			else:
				return HttpResponse(json.dumps({'v':int(version),'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")

		elif version=='4':  #Donut

			result={}
			lst=UrlDecision.objects.filter(country=c)
			cats=list(set([s.url.category for s in lst]))
			result['title']="Blocked Websites By Category"
			data=[]
			for ccc in cats:
				lst=UrlDecision.objects.filter(country=c, url__category=ccc)
				cl=[gg for gg in lst if gg.decision==3]
				if len(cl)>0:
					data.append({"label": str(ccc) , "value": len(cl)})

			result['data']=data
			if len(data)>0:
				result['status']='OK'
				result['v']=int(version)
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
			else:
				return HttpResponse(json.dumps({'v':int(version),'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")

		
		elif version=='5':  #news
			result={}
			lst=News.objects.filter(country=c)
			result['title']="News"

			data=[]
			for n in lst:
				data.append({"news_title": n.title, "description": n.description, "link":n.link_to_news, "agency":n.agency})
			result['data']=data
			if len(data)>0:
				result['status']='OK'
				result['v']=int(version)
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
			else:
				return HttpResponse(json.dumps({'v':int(version),'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")

		else:
			return HttpResponse(json.dumps({'v':int(version),'status':'ERROR', 'message':'wrong v param.'}, indent=2), content_type="application/json")
	
	elif 'url_query' in request.GET:
		q=request.GET['url_query']
		q=q.replace('www.', '')
		urls=Url.objects.filter(base_url=None)
		items=[]
		for u in urls:
			if u.address.find(q)!=-1:
				items.append(str(u.address))
		items=items[:10]
		items=[{"url": x} for x in items]
		return HttpResponse(json.dumps({'result':items}, indent=2), content_type="application/json")
	elif 'url' in request.GET and 'v' in request.GET:
		ur=request.GET['url']
		v=int(request.GET['v'])
		try:
			u=Url.objects.get(address=ur)
		except:
			return HttpResponse(json.dumps({'v':v,'status':'ERROR', 'message':'wrong url param.'}, indent=2), content_type="application/json")
		if v==0:
			items=[]
			items.append("Alexa Gobal Rank: "+str(u.global_rank))

			decisions=UrlDecision.objects.filter(url=u)
			openCountries=[d.country.name for d in decisions if d.decision==1]
			partialCountries=[d.country.name for d in decisions if d.decision==2]
			blockedCountries=[d.country.name for d in decisions if d.decision==3]

			items.append("This website has been scanned from {0} countries".format(len(decisions)))
			if len(openCountries): 
				items.append("It has shown to be OPEN in {0} countries.".format(len(openCountries)))
			if len(partialCountries): 
				items.append("It has shown to be PARTIALLY OR INCONSISTENTLY BLOCKED in {0} countries including {1}.".format(len(partialCountries), ', '.join(partialCountries[:5])))
			if len(blockedCountries): 
				items.append("It has shown to be BLOCKED in {0} countries including {1}.".format(len(blockedCountries), ', '.join(blockedCountries[:5])))


			result={}
			result['status']='OK'
			result['v']=v
			result['bullets']=items
			result['title']="Quick Summary"
			return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
		elif v==1:

			decisions=UrlDecision.objects.filter(url=u)
			openCountries=[d.country for d in decisions if d.decision==1]
			partialCountries=[d.country for d in decisions if d.decision==2]
			blockedCountries=[d.country for d in decisions if d.decision==3]
			if not decisions:
				return HttpResponse(json.dumps({'v':v,'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")
			else:
				result={}
				result['status']='OK'
				result['v']=v
				result['title']="Status Of The Website Around The World"
				data={}
				for op in openCountries:
					#data[op.alpha3]={"fillKey": "open", "number": UrlReport.objects.filter(url=u).count()}
					data[op.alpha3]={"fillKey": "open"}
				for bl in blockedCountries:
					#data[bl.alpha3]={"fillKey": "blocked", "number": UrlReport.objects.filter(url=u).count()}
					data[bl.alpha3]={"fillKey": "blocked"}
				for pr in partialCountries:
					#data[pr.alpha3]={"fillKey": "partially_blocked", "number": UrlReport.objects.filter(url=u).count()}
					data[pr.alpha3]={"fillKey": "partially_blocked"}

				result['data']=data
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
		
		elif v==2:  #news
			result={}
			lst=News.objects.filter(url=u)
			result['title']="News"

			data=[]
			for n in lst:
				data.append({"news_title": n.title, "description": n.description, "link":n.link_to_news, "agency":n.agency})
			result['data']=data
			if len(data)>0:
				result['status']='OK'
				result['v']=int(v)
				return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
			else:
				return HttpResponse(json.dumps({'v':int(v),'status':'ERROR', 'message':'No data!'}, indent=2), content_type="application/json")

		else:
			return HttpResponse(json.dumps({'status':'ERROR', 'message':'wrong v param.'}, indent=2), content_type="application/json")
	
	elif 'homepage' in request.GET:
		result={}
		result['status']='OK'
		terms=[]
		decidedCountry=UrlDecision.objects.values('country__name').distinct()
		for x in decidedCountry:
			num=UrlDecision.objects.filter(country__name=x['country__name'], decision=3).count()
			if num>0:
				terms.append({'n':str(num), 'c':x['country__name']})

		terms.append({'n':"How many", 'c':'in your country?'})
		result['terms']=terms

		top_news=News.objects.all()[:10]
		result['news']= [{"news_title": n.title, "description": n.description, "link":n.link_to_news, "agency":n.agency} for n in top_news]
		return HttpResponse(json.dumps(result, indent=2), content_type="application/json")
	else:
		return HttpResponse(json.dumps({'status':'ERROR', 'message':'wrong params.'}, indent=2), content_type="application/json")

#def addURL(url):
	#check if valid
	#get rank
	#categorize
	#get words used

	#check if it wasn't base, add category, etc. for the base too.

class Moderation(TemplateView):
    template_name = 'reporter/moderation.html'
    set_approve = 2 # Set value for ReportDecision when pressed Approve Button
    set_reject = 3 # Set value for ReportDecision when pressed Reject Button
    set_skip = -1 # Set value for ReportDecision when pressed Skip Button
    flag = 1 # default value when report need Moderation

    def make_decision(self, url, country):
        """
        This function is called only when Approved is clicked, takes as input, url and country
        :param url:
        :param country:
        :return:
        """
        makeDecision(url, country)
        pass

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):

        if request.method == 'POST':
            """
            Method is POST, when the user clicked in any of 3 button Options(Approve, Reject or Skip)
            """

            if request.POST['respond'] == 'Approve':
                """
                User Clicked Approve Button
                """

                # get the Report Decision getting Id for POST['flag'] included in template like hidden input field
                report_decision = ReportDecision.objects.get(id=request.POST['flag'])
                # if is Approve, set the correspond value self.approve
                report_decision.flag = self.set_approve
                #save
                report_decision.save()

            elif request.POST['respond'] == 'Reject':
                """
                Executed when user Clicked on Reject Button
                """
                # get the Report Decision getting Id for POST['flag'] included in template like hidden input field
                report_decision = ReportDecision.objects.get(id=request.POST['flag'])
                report_decision.flag = self.set_reject
                report_decision.decision = 0
                report_decision.save()
                #Call Special function...
                self.make_decision(
                    report_decision.report.url,
                    report_decision.report.reporter.country
                )


            elif request.POST['respond'] == 'Skip':
                """
                Execute when user Clicked on Respond Button
                """
                report_decision = ReportDecision.objects.get(id=request.POST['flag'])
                report_decision.flag = self.set_skip
                report_decision.save()

            #Get actual "Country Code" for redirect to appropiate url /moderate/COUNTRY_CODE
            country_code = request.POST['country_code']

            # Keep in the same page (Skip Page) if the user is in Skip page (/moderate/COUNTRY_CODE/SKIP)
            # When pressed any button (Approved, Reject or SKip

            if request.POST.get('skip', None):
                # keep in Skip Page.
                return HttpResponseRedirect(reverse('moderation_page', args=[country_code, 'skip']))

            return HttpResponseRedirect(reverse('moderation_page', args=[country_code]))

        return super(Moderation, self).dispatch(request, *args, **kwargs)

    def get_report(self, reporter):
        """
        Get report..function, only a auxilia function that get a Reporter Model Object and verify this has
        ReportDecisions for get and return only 1
        :param reporter:
        :return:
        """
        # get all ReportDecision of this reporter
        reports = ReportDecision.objects.filter(
            report__reporter=reporter,
            flag = self.flag,  #comment or change according the requirements
        )
        if reports:
            # if this Reporter has ReportDecisions Record..Return the first..
            return reports[0]
        else:
            # if not have more ReportDecisions..return False
            return False

    def get_context_data(self, **kwargs):
        """
        Return Context Data for templates: moderation.html or moderate.html
        :param kwargs:
        :return:
        """
        # get Default Context data
        context = super(Moderation, self).get_context_data()

        # Get option selected for the User, if user select YES in the option "View reports skipped:" (moderation.html)
        # so this add a prefix /skip/ to the URL that we can acces via "choose_opt". urls.py Line:15
        view_reports_skipped = self.kwargs.get('choose_opt', None)
        # Get country_code. See Urls.py
        country_code = self.kwargs.get('country_code', None)

        # Save Country Code for show in templates
        context['country_code'] = country_code
        # Get all Countries ..used for template moderation.html (Select OPtion) Line: 25 to 29 ,
        # but show only Countries with existing Reporters
        context['countries'] = Reporter.objects.values('country__alpha3', 'country__name').distinct()

        if view_reports_skipped == 'skip':
            """
            If user selected see only Skipped reports on template moderation.html. Line 34 to 36,
            so set flag default value from 1 to -1 for use of function get_report. Line: 83
            """
            self.flag = -1
            context['skip'] = 'skip'

        if country_code:
            """
            If url has a Country Code defined..so the user are selected a option and we need render a diferent template:
            moderate.html, this template show all fields of a Report.
            """

            self.template_name = 'reporter/moderate.html'

            # get exact Country based on the unique country_code (alpha3)
            country = Country.objects.get(alpha3__iexact=country_code)
            # Now get all Reporters for this Country.
            reporter = Reporter.objects.filter(country=country)

            # If exists Reporters for this Country..
            if reporter:
                # Get the first ReporDecision to moderate of this Reporter..
                report = self.get_report(reporter[0])
                # set context for the first ReportDecision returned
                context['reporter'] = report
                context['country'] = country
                context['report_decision'] = report

                # this value is used in themplate for determinated if a Country or Reporter has or don't have more Reports to moderate
                # and show the corresponding message, moderate.html 48 to 51
                context['has_reports'] = True if report else False
            else:
                context['has_reports'] = False

        return contex