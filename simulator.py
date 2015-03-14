########################### IMPORTS #########################
import copy
import operator
import random
import sys

###################### GLOBAL CONSTANTS #####################

num_processes = 12     # total number of processes per
num_max_bursts = 6     # total number of bursts for CPU bound processes
cs_time = 4            # time needed for context switch (in ms)
num_cpus = 4
initial_processes = []
total_cpu_bound = 0

###################### GLOBAL VARIABLES #####################

time_elapsed = 0      # total time elapsed since the start of the current algorithm
cpu_bound = 0         # number of CPU bound processes left
turnaround_total = 0
wait_total = 0
num_bursts = 0

max_total_wait = 0
min_total_wait = sys.maxint
max_turnaround = 0
min_turnaround = sys.maxint

processes = []
all_cpu = []

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
		self.cpu_index = -1

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
		print "[time %dms] %s process ID %d CPU burst done on CPU %d (turnaround time %dms, total wait time %dms)" % (time_elapsed, self.type_string, self.id, self.cpu_index, turnaround, total_wait_time)
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
		if self.type == 1 and len(self.burst_start_times) >= num_max_bursts:
			return True
		else:
			return False

	# handles context switching
	def switch_from(self, other):
		global time_elapsed, cs_time
		if other != None and self != other:	
			print "[time %dms] Context switch (swapping out process ID %d for process ID %d)" %(time_elapsed, other.id, self.id)
			time_elapsed += cs_time

	def done(self):
		avg_turnaround = sum(self.all_turnarounds) / float(len(self.all_turnarounds))
		avg_wait_times = sum(self.all_wait_times) / float(len(self.all_wait_times))
		print "[time %dms] %s process ID %d terminated (avg turnaround time %dms, avg total wait time %dms)" % (time_elapsed, self.type_string, self.id, avg_turnaround, avg_wait_times)

class CPU:
	def __init__(self, _id):
		self.id = _id
		self.current_processes = []
		self.load = 0
	def set_load(self):
		for p in self.current_processes:
			self.load += p.cpu_time
	def print_processes(self):
		print "~~~~~~~~~~~~~ Processes currently in CPU %d ~~~~~~~~~~~~~" % self.id
		for p in self.current_processes:
			print "Process %d with cpu time %d" % (p.id, p.cpu_time)


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

def reset_conditions():
	global time_elapsed, cpu_bound, total_cpu_bound, turnaround_total, wait_total, num_bursts, max_total_wait, min_total_wait, max_turnaround, min_turnaround
	time_elapsed = 0
	cpu_bound = total_cpu_bound
	turnaround_total = 0
	wait_total = 0
	num_bursts = 0

	max_total_wait = 0
	min_total_wait = sys.maxint
	max_turnaround = 0
	min_turnaround = sys.maxint

def create_CPUs(m):
	all_cpu = []
	for i in range(0, m):
		c = CPU(i)
		all_cpu.append(c)
	return all_cpu


def find_least_busy(cpus):
	least_busy = cpus[0]
	for c in cpus:
		if c.load < least_busy.load:
			least_busy = c
	return least_busy.id

def burst_time_lt(self, other):
	return self.cpu_time < other.cpu_time

def start_process(p):
	if p.cpu_index == -1: #process is not on any CPU yet
		p.cpu_index = find_least_busy(all_cpu)
		all_cpu[p.cpu_index].current_processes.append(p)
		all_cpu[p.cpu_index].set_load()
	return p.burst()

def finish_process(p, finished):
	global cpu_bound
	# remove process from CPU
	all_cpu[p.cpu_index].current_processes.remove(p)
	all_cpu[p.cpu_index].set_load()
	p.cpu_index = -1
	finished.append(p)
	processes.remove(p)
	cpu_bound -= 1

def swap_process(p, location):
	p.burst_start_times.append(time_elapsed)
	tmp = p
	processes.remove(p)
	processes.insert(location, tmp)

################### SCHEDULING ALGORITHMS ##################
def fcfs():
	global cpu_bound
	finished = []
	prev = None
	while(True):
		p = processes[0]
		p.switch_from(prev)
		if p.status == "ready":
			done = start_process(p)
			if done == True: #CPU Bound Process has finished it's last burst
				# remove process from CPU
				finish_process(p, finished)
			else:
				swap_process(p, len(processes)) #reinsert process at end of queue
			p.status = "blocked"
			p.wait()
			prev = p
		if cpu_bound == 0:
			finished.extend(processes)
			p.done()
			break
	analysis(finished)

def sjf_nonpreemptive(all, all_cpu):
	global cpu_bound

	all.sort(key = operator.attrgetter('cpu_time'))
	finished = []

	prev = None
	while(True):
		p = all[0]
		p.switch_from(prev)
		if p.status == "ready":
			if p.cpu_index == -1: #process is not on any CPU yet
				p.cpu_index = find_least_busy(all_cpu)
				all_cpu[p.cpu_index].current_processes.append(p)
				all_cpu[p.cpu_index].set_load()
			done = p.burst()
			if done == True:
				# remove process from CPU
				all_cpu[p.cpu_index].current_processes.remove(p)
				all_cpu[p.cpu_index].set_load()
				p.cpu_index = -1
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
			prev = p

		if cpu_bound == 0:
			finished.extend(all)
			p.done()
			break
	analysis(finished)

def sjf_preemptive(all):
	return

def roundRobin(all):
	return

####################### MAIN ################################

# set up initial processes and save them
for i in range(1, num_processes+1):
	if i <= 0.8*num_processes:
		x = Process(i, 0)
	else:
		x = Process(i, 1)
	initial_processes.append(x)
total_cpu_bound = cpu_bound

#create m CPUs
all_cpu = create_CPUs(num_cpus)

# working list of processes is a deep copy of the initial conditions
processes = copy.deepcopy(initial_processes)
fcfs()

processes = copy.deepcopy(initial_processes)
sjf_nonpreemptive(processes, all_cpu)
reset_conditions()
