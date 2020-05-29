# -*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import kjxx
import datetime
import time
import os.path
import csv
from selenium import webdriver

failed_connections=[]
def get_page(url):
	#发起请求，获得源码
	try:
		requests.adapters.DEFAULT_RETRIES=5
		s=requests.session()
		s.keep_alive=False
		response=requests.get(url)
		if response.status_code==200:
			response.encoding='gbk'
			html=response.text
			response.close()
			del response
			return html
	except requests.exceptions.ConnectionError:
		'''time.sleep(5)
		for i in range(0,10):
			response = requests.get(url)
			if response.status_code == 200:
				response.encoding = 'gbk'
				html = response.text
				return html'''
		#failed_connections.append(url)
		pass

def parse(text):
	#解析网页内容
	if text==None:
		return None
	doc=pq(text)
	number_rule = ".ball_box01 li"  # 获取开奖号码，按照从大到小，先红后蓝的顺序
	try:
		ball_num=list(map(lambda x:int(x),doc(number_rule).text().split()))
	except:
		return None

	period_rule=".kj_tablelist02 .td_title01 .span_left .cfont2"
	try:
		period='20'+doc(period_rule).text()+'\t'
	except:
		return None

	date_rule=".td_title01 .span_right" #获取当次开奖日期，结果“本期销量：100元 奖池滚存：100元”
	try:
		history_date=doc(date_rule).text().split()[0].split('：')[1]
		date=convert_date_format(history_date)+'\t'
		weekday=get_weekday(date)
	except:
		return None

	sales_and_prizepool_rule = ".cfont1"  # 获取本期销量和奖池滚存
	try:
		sales,prize_pool=list(map(lambda x:x[:-1].replace(',',''),doc(sales_and_prizepool_rule).text().split()[:2]))
	except:
		return None
	try:
		float(sales)
		sales+='\t'
	except:
		sales='0\t'
	try:
		float(prize_pool)
		prize_pool+='\t'
	except:
		prize_pool='0\t'

	#rule3 = ".kj_tablelist02"  # 获取一至六等奖开奖详情

	history=kjxx.Two_Color_Balls(period=period,date=date,weekday=weekday,balls=ball_num,sales=sales,prize_pool=prize_pool)
	return history

def convert_date_format(date):
	year = date.split('年')[0]
	month = date.split('年')[1].split('月')[0]
	day = date.split('年')[1].split('月')[1].split('日')[0]
	return year+'/'+month+'/'+day

def get_weekday(date):
	year,month,day=list(map(lambda x:int(x),date.split('/')))
	weekday=datetime.datetime(year,month,day)
	return weekday.weekday()+1

def get_all_url(init_url):
	urls=[]
	html=get_page(init_url)
	doc=pq(html)
	rule=".iSelectList a"
	its=doc(rule).items()
	for it in its:
		urls.append(it.attr('href'))
	return urls

def retry_failed_connection(driver,period):
	retry_times=5
	while retry_times>0:
		try:
			#显示自定义查询选项
			if not driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/dl/dd/ul/li[4]/div').is_displayed():
				js='document.querySelector("body > div.wqkj.ssq > div > div.gjl > div.aqcx > dl > dd > ul > li.zdy.dqzt > div").style.display="block";'
				driver.execute_script(js)
			#显示按期数查询界面

			if not driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/dl/dd/ul/li[4]/div/div[2]/div/div[2]/div[2]').is_displayed():
				js='document.querySelector("body > div.wqkj.ssq > div > div.gjl > div.aqcx > dl > dd > ul > li.zdy.dqzt > div > div.zdyTcNr > div > div.sqN > div:nth-child(2)").className+=" dq";'
				driver.execute_script(js)

			#重置查询期号
			driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/dl/dd/ul/li[4]/div/div[2]/div/div[2]/div[2]/button[2]').click()
			#修改查询开始期数
			driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/dl/dd/ul/li[4]/div/div[2]/div/div[2]/div[2]/div/input[1]').send_keys(period)
			#修改查询结束期数
			driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/dl/dd/ul/li[4]/div/div[2]/div/div[2]/div[2]/div/input[2]').send_keys(period)
			#提交查询
			driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/dl/dd/ul/li[4]/div/div[2]/div/div[2]/div[2]/button[1]').click()

			page_source=driver.page_source
			break
		except:
			driver.refresh()
			time.sleep(10)
			retry_times-=1
	if retry_times<=0:
		return None
	doc = pq(page_source)
	rule = ".wqkj.ssq .containerHome .bgzt table tbody"
	td=doc(rule).text()#期号，日期（周几），6个红色球，一个蓝色球，销售额，一等奖注数，一等奖单注金额，二等奖注数，二等奖单注金额，三等奖注数，三等奖单注金额，奖池
	            #样例['2017001', '2017-01-01(日)', '091114202526', '15', '376,155,592', '9', '7522351', '184', '154219', '1511', '3000', '1007519355']
	ans=td.split()
	cur_period=period+'\t'
	date=ans[1][:10].replace('-','/')+'\t'
	weekday=get_weekday(ans[1][:10].replace('-','/'))
	balls_str=ans[2]+ans[3]
	balls=[]
	for i in range(0,7):
		balls.append(int(balls_str[i*2:(i+1)*2]))
	sales=ans[4].replace(',','')+'\t'
	prize_pool=ans[11]+'\t'
	history=kjxx.Two_Color_Balls(period=cur_period,date=date,weekday=weekday,balls=balls,sales=sales,prize_pool=prize_pool)
	return history



def main():
	init_url="http://kaijiang.500.com/shtml/ssq/20028.shtml"
	urls=get_all_url(init_url)#获取所有的开奖记录网页链接
	file='prize_history.csv'
	file_exit = True
	if not os.path.isfile(file):
		file_exit = False

	opt = webdriver.ChromeOptions()
	opt.set_headless()
	driver = webdriver.Chrome(options=opt)
	url = 'http://www.cwl.gov.cn/kjxx/ssq/kjgg/'
	driver.get(url)
	time.sleep(10)

	with open(file, 'a') as csvfile:
		writeCSV = csv.writer(csvfile, lineterminator='\n')
		if not file_exit:  # 如果文件不存在，需要创建文件，并设置表头
			writeCSV.writerow(['期数', \
							   '日期', \
							   '星期', \
							   '红球一', \
							   '红球二', \
							   '红球三', \
							   '红球四', \
							   '红球五', \
							   '红球六', \
							   '蓝球', \
							   '销量（元）', \
							   '奖池（元）', \
							   '一等奖单注奖金', \
							   '二等奖单注奖金', \
							   '三等奖单注奖金', \
							   '四等奖单注奖金', \
							   '五等奖单注奖金', \
							   '六等奖单注奖金'])
		for i in range(len(urls) - 1, 0, -1):
			html = get_page(urls[i])
			history = parse(html)
			if history != None:
				ready_to_write_row = history.prepare_to_write()
				writeCSV.writerow(ready_to_write_row)
			else:
				period = '20' + urls[i].split('/')[-1].split('.')[0]
				ans=retry_failed_connection(driver,period)
				if ans==None:
					failed_connections.append(urls[i])
				else:
					ready_to_write_row = ans.prepare_to_write()
					writeCSV.writerow(ready_to_write_row)
			print("{}".format(i))
	csvfile.close()
	driver.quit()

	print("有{}条开奖记录获取失败".format(len(failed_connections)))
	if len(failed_connections)!=0:
		print(failed_connections)

def test():
	init_url = "http://kaijiang.500.com/shtml/ssq/20028.shtml"
	urls = get_all_url(init_url)  # 获取所有的开奖记录网页链接
	file = 'prize_history.csv'
	for i in range(1,10):
		html = get_page(urls[i])
		history = parse(html)
		history.write_to_csv(file)
	print("有{}条开奖记录获取失败".format(len(failed_connections)))
	if len(failed_connections) != 0:
		print(failed_connections)

if __name__=="__main__":
	main()
	'''
	period='2017001'
	opt = webdriver.ChromeOptions()
	opt.set_headless()
	driver = webdriver.Chrome(options=opt)
	url = 'http://www.cwl.gov.cn/kjxx/ssq/kjgg/'
	driver.get(url)
	time.sleep(10)
	retry_failed_connection(driver,'2017001')
	retry_failed_connection(driver, '2017002')
	driver.quit()'''