import nidaqmx
import time
from nidaqmx.stream_readers import AnalogMultiChannelReader
import numpy as np

class cDAQ():
	def __init__(self):
		self.running = False
		self.is_valid = None
		### Too many of these are hardcoded right now 
		self.sampling_freq_in = 200 	# This is how fast the channel stream will sampling, python limit is 1.0e5, 4 chan 9219 is 
												# Need to experiment more with effect on final but for now leave high
		self.buffer_in_size = 5 		# Keep low for speed increase for large moving averages, min is 5 keep for speed
		self.buffer_in_size_cfg = round(self.buffer_in_size*1) # necessary for clock config
		self.bufsize_callback = self.buffer_in_size
		self.channels_in = 1 			# Assumes only one channel
		self.min_res_expected = 0.8		# Set to lowest resistance, mainly chooses the bias 
		self.max_res_expected = 1000    # Both expected resistance values are needed for 4 wire
		self.current_excit = 500.0e-6	# This can be a constant, highest current allowed by 9219
		self.task = None				# Used as the main task object
		self.channel_list = None		# Creates a channel list to input into configuration functions
		self.buffer_in = None			# Buffer input into the stream read function
		self.create_task()

	#### Instantiates the task within the class
	def create_task(self):
		task = nidaqmx.Task()
		self.task = task

	#### The end
	def end(self):
		self.task.close()

	#### Pretty self explanatory, starts the task after configured
	def start_task(self):
		print(self.running)
		if self.running == True:
			self.task.start()


	### Adding a for loop that assumes 9219s and starting in slot 1
	### create 
	def create_chan_list_generic(self,channel_creator_num):
		### Assumes only one cDAQ
		chass = 'cDAQ1'
		channel_list = []

		for i in range(0,channel_creator_num):
			if i < 4:
				mod = 'Mod1/'
			elif i >= 4 and i < 8:
				mod ='Mod2/'
			elif i >= 8 and i < 12:
				mod = 'Mod3/'
			elif i >= 12 and i < 16:
				mod ='Mod4/'
			elif i >= 16 and i < 20:
				mod = 'Mod5/'
			elif i >= 24 and i < 28:
				mod ='Mod6/'
			elif i >= 28 and i < 32:
				mod = 'Mod7/'
			else:
				mod = 'Mod8/' #### Can add more if we get a 14 units

			chan = chass + mod + 'ai' + str((i%4))
			channel_list.append(chan)

		self.channel_list = channel_list


	## This will allow you to add in a channel list, more likely to get task errors
	## Example
	def intake_chan_list(self,premade_channel_list):
		if any('cDAQ' in x for x in premade_channel_list):
			self.channel_list = premade_channel_list
		else:
			print('Error!!! Your channel list is either not a list or does not contain a cDAQ reference')
		
		
	##### This function creates the input stream, basically turns on excitation current and puts values into a callable object
	def create_in_stream(self):
		self.stream_in = AnalogMultiChannelReader(self.task.in_stream)
		self.task.register_every_n_samples_acquired_into_buffer_event(self.bufsize_callback,self.reading_task_callback)
		self.running = True


	### This will configure the channels 
	def cfg_voltage_channels(self):  # uses above parameters
		if self.channel_list is not None:
			self.channels_in = len(self.channel_list)
		else:
			print('Error! Need to establish channel list')
			sys.exit()

		### Creates a basic voltage channel for each of list
		for i in self.channel_list:
			self.task.ai_channels.add_ai_voltage_chan(i)

		## configure the timing module 
		self.task.timing.cfg_samp_clk_timing(rate=self.sampling_freq_in, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
											   samps_per_chan=self.buffer_in_size_cfg)

		

	### Configures all 4 wire channels based on channel list
	def cfg_4wire_channels(self):  # uses above parameters

		if self.channel_list is not None:
			self.channels_in = len(self.channel_list)
		else:
			print('Error! Need to establish channel list')
			sys.exit()


		for i in self.channel_list:
			self.task.ai_channels.add_ai_resistance_chan(i, min_val=self.min_res_expected, max_val=self.max_res_expected, 
				units=nidaqmx.constants.ResistanceUnits.OHMS, resistance_config=nidaqmx.constants.ResistanceConfiguration.FOUR_WIRE, 
				current_excit_source=nidaqmx.constants.ExcitationSource.INTERNAL, current_excit_val=self.current_excit)
		## configure the timing module 
		self.task.timing.cfg_samp_clk_timing(rate=self.sampling_freq_in, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
											   samps_per_chan=self.buffer_in_size_cfg)


	### This is reading from the stream, the read_many_sample basically reads all samples that have been updated
	def reading_task_callback(self,task_idx, event_type, num_samples, callback_data):
		if self.running:
			self.buffer_in = np.zeros((self.channels_in,num_samples))
			self.stream_in.read_many_sample(self.buffer_in,num_samples, timeout = nidaqmx.constants.WAIT_INFINITELY)
			self.buffer_out=self.buffer_in
		return 0 # Very important to not break, basically ints are how NI handles error codes


	def return_buffer(self):
		return self.buffer_out
		### buffer is returned as an np.array of size (number of channels,buffer)
		### call the last in one with buffer_in[channel number,-1] i.e. channel 0 [0,-1]
		### averaging could be good if we want to take time