# !/usr/bin/python
# -*- coding:UTF-8 -*-

import DCPredictor
import tensorflow as tf

def main():
	filename='prize_history.txt'
	'''
	data=funcs.get_data_txt(filename)
	balls_list=list(map(lambda x:x[3:],data))
	for days in range(len(balls_list)):
		for i in range(7):
			balls_list[days][i]=int(balls_list[days][i])
	print(balls_list[:6])
'''
	preNumber=[]
	for i in range(7):
		predictor = DCPredictor.DCPredictor(filename)
		predictor.loadData()
		predictor.getOnePosBall(i)
		predictor.buildTrainDataSet()
		with tf.variable_scope('train'):
			predictor.trainLstm()
		with tf.variable_scope('train',reuse=True):
			preNumber.append(predictor.prediction())
	print(preNumber)

if __name__=="__main__":
	main()