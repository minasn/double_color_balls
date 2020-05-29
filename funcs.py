import csv
import os
import pandas as pd
def get_data_csv(filename):
	file_exits(filename,'csv')
	data=pd.read_csv(filename,encoding='gbk',usecols=[0,1,2,3,4,5,6,7,8,9]) #获取期号，日期，星期，6个红球，1个蓝球
	data_list=data.values.tolist()
	for row in data_list:
		row[1]=row[1].replace('\t','')
	return data_list

def get_data_txt(filename):
	file_exits(filename,'txt')
	data=[]
	reader=open(filename,'r')
	for period in reader.readlines():
		data.append(period.split())
	return data


def file_exits(filename,type='csv'):
	assert os.path.exists(filename), "no such file"
	assert filename.split('.')[-1] == type, 'input file is not {} file'.format(type)

def csv_to_txt(filename):
	file_exits(filename,'csv')
	new_filename=os.path.splitext(filename)[0]+'.txt'
	csv_data=get_data_csv(filename)
	with open(new_filename,'w') as o:
		for row in csv_data:
			for item in row:
				o.write(str(item)+' ')
			o.write('\n')