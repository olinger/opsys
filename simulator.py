########################### IMPORTS #########################
import random
import sys

###################### GLOBAL CONSTANTS #####################
max_total_wait = 0
min_total_wait = sys.maxint
max_turnaround = 0
min_turnaround = sys.maxint

###################### GLOBAL VARIABLES #####################
time_elapsed = 0
cpu_bound = 0
turnaround_total = 0
wait_total = 0
num_bursts = 0

###################### CLASS DECLARATIONS ###################
class Process:
	def __init__(self, _id, _type):
		self.id = _id
		self.type = _type
		self.cpu_time = self.generate_burst(_type)
		self.status = "ready"
		self.type_string = self.get_type()
		self.creation_output()
		self.burst_start_times = [time_elapsed]
		self.all_turnarounds = []
		self.all_wait_times = []
		self.cpu_util = []

	def __str__(self):
		return self.type_string + " process ID " + str(self.id) 

	def get_type(self):
		if self.type == 0:
			return "Interactive"
		else:
			global cpu_bound
			cpu_bound += 1
			return "CPU-bound"

	def creation_output(self):
		global time_elapsed
		print "[time %dms] %s process ID %d entered ready queue (requires %dms CPU time)" % (time_elapsed, self.type_string, self.id, self.cpu_time)

	def generate_burst(self, type):
		if type == 0:
			burst_time = random.randint(20,200)
		else:
			burst_time = random.randint(200,3000)
		return burst_time

	def wait(self):
		global time_elapsed
		wait_time = random.randint(1000, 4500)
		time_elapsed += wait_time
		self.status = "ready"

	def burst(self):
		global time_elapsed, num_bursts, turnaround_total, wait_total, max_turnaround, min_turnaround, max_total_wait, min_total_wait
		self.status = "active"
		total_wait_time = time_elapsed - self.burst_start_times[-1]
		turnaround = total_wait_time + self.cpu_time
		time_elapsed += self.cpu_time
		print "[time %dms] %s process ID %d CPU burst done (turnaround time %dms, total wait time %dms)" % (time_elapsed, self.type_string, self.id, turnaround, total_wait_time)
		self.all_turnarounds.append(turnaround)
		self.all_wait_times.append(total_wait_time)
		#increment totals, store max and mins
		num_bursts += 1
		turnaround_total += turnaround
		wait_total += total_wait_time
		if turnaround > max_turnaround:
			max_turnaround = turnaround
		if turnaround < min_turnaround:
			min_turnaround = turnaround
		if total_wait_time > max_total_wait:
			max_total_wait = total_wait_time
		if total_wait_time < min_total_wait:
			min_total_wait = total_wait_time
		#check if last burst for CPU-bound process
		if self.type == 1 and len(self.burst_start_times) >= 6:
			return True
		else:
			return False

	def done(self):
		avg_turnaround = sum(self.all_turnarounds) / float(len(self.all_turnarounds))
		avg_wait_times = sum(self.all_wait_times) / float(len(self.all_wait_times))
		print "[time %dms] %s process ID %d terminated (avg turnaround time %dms, avg total wait time %dms)" % (time_elapsed, self.type_string, self.id, avg_turnaround, avg_wait_times)

#################### HELPER FUNCTIONS #########################
def print_list(list):
	for l in list:
		print l

def analysis(all):
	avg_turnaround = turnaround_total / num_bursts
	avg_total_wait = wait_total / num_bursts
	print "Turnaround time: min %dms; avg %dms, max %dms" %(min_turnaround, avg_turnaround, max_turnaround)
	print "Total wait time: min %dms; avg %dms; max %dms" %(min_total_wait, avg_total_wait, max_total_wait)
	print "Average CPU utilization per process:"
	for p in all:
		print "Process ID %d: %d %%" % (p.id, 0)

#Turnaround time: min ___ ms; avg ___ ms; max ___ ms
#Total wait time: min ___ ms; avg ___ ms; max ___ ms
#Average CPU utilization: ___%

#Average CPU utilization per process:
#process ID: ___%
#process ID: ___%
##...
#process ID: ___%

################### SCHEDULING ALGORITHMS ##################
def fcfs(all):
	global cpu_bound
	finished = []
	while(True):
		p = all[0]
		if p.status == "ready":
			done = p.burst()
			if done == True:
				finished.append(p)
				all.remove(p)
				cpu_bound -= 1
			else:
				tmp = p
				tmp.burst_start_times.append(time_elapsed)
				all.remove(p)
				all.append(tmp)

			p.status = "blocked"
			p.wait()
		if cpu_bound == 0:
			finished.extend(all)
			p.done()
			break
	analysis(finished)

def sjf_nonpreemptive(all):
	return

def sjf_preemptive(all):
	return

def roundRobin(all):
	return

####################### MAIN ################################
#a = Process(1, 0)
#b = Process(2, 1)
processes = []
for i in range(1,13):
	if i <= 10:
		x = Process(i, 0)
	else:
		x = Process(i, 1)
	processes.append(x)
fcfs(processes)
