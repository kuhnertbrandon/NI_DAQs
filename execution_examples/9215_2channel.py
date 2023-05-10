import numpy as np 
import pandas as pd 
import time 

import nidaqmx

import threading

import cDAQ_api as cDAQ_api

def main():

	column_list=['Time (s)','Voltage_1','Voltage_2','Time for last cycle']
	big_data=np.empty((0,len(column_list)))
	delta_loop = 0

	print('\n Starting up')
	c = cDAQ_api.cDAQ()				# Instantiate the class
	c.create_chan_list_generic(2)	# This creates a channel list assuming you start from the first slot
	time.sleep(1)	
	c.cfg_voltage_channels()		# This configures simple voltage channels (+/- 10 V)
	print('\n Configured channels')
	c.create_in_stream()			# Creates the stream
	print('\n Created the stream')
	c.start_task()					# Starts the task 
	print('\n Intializing task')
	time.sleep((len(column_list)-1))

	 ## Modulo for tracking and saving
	start_time = time.time()
	try:
		while(True): 
			delta_start = time.time()
			current_time = time.time() - start_time  ## Tracking cycle time as need

			buff =  c.return_buffer()    			 ## This is all you need to call the buffer
			## buffer format is numpy array of size 5,n_channels
			
			new_row = np.array([[current_time,buff[0,-1],buff[1,-1],delta_loop]])
			big_data = np.vstack((big_data,new_row))
			delta_loop = time.time()-delta_start
			
			if (current_time % 10) < 0.02:
				bigdf = pd.DataFrame(big_data,columns=column_list) ## This saves things very slowly
				bigdf.to_csv('stress_test.csv',index=False)
				print(new_row)
				
			time.sleep(0.01)

	except KeyboardInterrupt:
		c.end()
		bigdf = pd.DataFrame(big_data,columns=column_list)
		bigdf.to_csv('stress_test.csv',index=False)
		print('Bye!!')
			



if __name__ == '__main__':
	main()