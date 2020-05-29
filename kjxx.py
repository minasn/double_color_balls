import os.path
import csv
class Two_Color_Balls:
	def __init__(self,period='1',date='2020/4/23',weekday=4,balls=[],sales='0',prize_pool='0',six_prizes=[]):
		self.period=period          #开奖期数
		self.date=date              #开奖日期
		self.weekday=weekday        #开奖星期，每周二、四、日开奖
		self.balls=balls            #开奖双色球号码
		self.sales=sales            #当期销量，单位元
		self.prize_pool=prize_pool  #当期奖池，单位元
		self.six_prizes=six_prizes  #一至六等奖获奖情况

	def prepare_to_write(self):
		write_row=[]
		write_row.append(self.period)
		write_row.append(self.date)
		write_row.append(self.weekday)
		for ball in self.balls:
			write_row.append(ball)
		write_row.append(self.sales)
		write_row.append(self.prize_pool)
		for prize in self.six_prizes:
			write_row.append(prize)
		return write_row

	def write_to_csv(self,file='prize_history.csv'):
		ready_to_write_row=self.__prepare_to_write()
		file_exit=True
		if not os.path.isfile(file):
			file_exit=False
		with open(file, 'a') as csvfile:
			writeCSV = csv.writer(csvfile,lineterminator='\n')
			if not file_exit: #如果文件不存在，需要创建文件，并设置表头
				writeCSV.writerow(['期数',\
								   '日期',\
								   '星期',\
								   '红球一',\
								   '红球二',\
								   '红球三',\
								   '红球四',\
								   '红球五',\
								   '红球六',\
								   '蓝球',\
								   '销量（元）',\
								   '奖池（元）',\
								   '一等奖单注奖金',\
								   '二等奖单注奖金',\
								   '三等奖单注奖金',\
								   '四等奖单注奖金',\
								   '五等奖单注奖金',\
								   '六等奖单注奖金'])
			writeCSV.writerow(ready_to_write_row)
		csvfile.close()