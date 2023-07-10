import numpy as np 
import pandas as pd 
import time 

import nidaqmx

import threading

import cDAQ_api as cDAQ_api

def main():

	column_list=['Time (s)','Resistance_1','Resistance_2']
	big_data=np.empty((0,len(column_list)))
	delta_loop = 0

	print('\n Starting up')
	c = cDAQ_api.cDAQ()
	list_o_channels = ['cDAQ4Mod2/ai0','cDAQ4Mod2/ai1']

	c.intake_chan_list(list_o_channels)  # intakes a premade channel list
	time.sleep(1)
	c.cfg_4wire_channels() 				 # Configures for 4 wire (A lot of 4 wire configuration is hard coded)
	print('\n Configured channels')
	c.create_in_stream()				 # Creates the data stream
	print('\n Created the stream')       
	c.start_task()						 # Start the task
	print('\n Intializing task')
	time.sleep((len(column_list)-1))


	 ## Modulo for tracking and saving
	print('Data Aquisition starts now')
	start_time = time.time()
	try:
		while(True): 
			delta_start = time.time()
			current_time = time.time() - start_time  ## Tracking cycle time as need

			buff =  c.return_buffer()  				 # Pulls buffer

			new_row = np.array([[current_time,buff[0,-1],buff[1,-1]]])
			big_data = np.vstack((big_data,new_row))
			delta_loop = time.time()-delta_start
			
		
			#bigdf = pd.DataFrame(big_data,columns=column_list)  # This is slow
			#bigdf.to_csv('stress_test.csv',index=False)
			print(new_row)
				
			time.sleep(0.1)

	except KeyboardInterrupt:
		c.end()
		bigdf = pd.DataFrame(big_data,columns=column_list)
		bigdf.to_csv('stress_test.csv',index=False)
		print('Bye!!')



if __name__ == '__main__':
	main()