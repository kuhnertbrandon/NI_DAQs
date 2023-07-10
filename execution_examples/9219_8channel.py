import numpy as np 
import pandas as pd 
import time 

import nidaqmx
import threading
import cDAQ_api as cDAQ_api

from datetime import datetime

def main():

	while(True):
		prompt = input('\n What do you want to call this test? \n' )
		if len(prompt) >3:
			break
		else:
			print('Actually type a decent sample name')

	column_list=['Time (s)','Resistance_1','Resistance_2','Resistance_3','Resistance_4','Resistance_5','Resistance_6','Resistance_7','Resistance_8']
	big_data=np.empty((0,len(column_list)))
	now = datetime.now()
	timestamp = now.strftime("_%Y_%m_%d_%H_%M")
	title = 

	print('\n Starting up')
	c = cDAQ_api.cDAQ()
	list_o_channels = ['cDAQ2Mod2/ai0','cDAQ2Mod2/ai1','cDAQ2Mod2/ai2','cDAQ2Mod2/ai3','cDAQ2Mod3/ai0','cDAQ2Mod3/ai1','cDAQ2Mod3/ai2','cDAQ2Mod3/ai3',]

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
	start_time = time.time()
	try:
		while(True): 
			current_time = time.time() - start_time  ## Tracking cycle time as need

			buff =  c.return_buffer()  				 # Pulls buffer

			#
			new_row = np.array([[current_time,buff[0,-1],buff[1,-1],buff[2,-1],buff[3,-1],buff[4,-1],buff[5,-1],buff[6,-1],buff[7,-1]]])
			big_data = np.vstack((big_data,new_row))
			
			if (current_time % 10) < 0.02:
				bigdf = pd.DataFrame(big_data,columns=column_list)  # This is slow
				bigdf.to_csv(title + '.csv',index=False)
				print(new_row)
				
			time.sleep(0.01)

	except KeyboardInterrupt:
		c.end()
		bigdf = pd.DataFrame(big_data,columns=column_list)
		bigdf.to_csv(title + '.csv',index=False)
		print('Bye!!')



if __name__ == '__main__':
	main()