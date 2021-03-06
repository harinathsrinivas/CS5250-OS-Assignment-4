'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
   input.txt
Output files:
   FCFS.txt
   RR.txt
   SRTF.txt
   SJF.txt
'''
import sys
import copy
import math

input_file = 'input.txt'

class Process:
   last_scheduled_time = 0
   def __init__(self, id, arrive_time, burst_time):
       self.id = id
       self.arrive_time = arrive_time
       self.burst_time = burst_time
       self.waiting_time = 0
       self.lastSchedule_time = arrive_time
       self.expected_burst_time = 0
   #for printing purpose
   def __repr__(self):
       return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
   #store the (switching time, proccess_id) pair
   schedule = []
   current_time = 0
   waiting_time = 0
   print(process_list)
   for process in process_list:
       print(process.id, current_time)
       if(current_time < process.arrive_time):
           current_time = process.arrive_time
       print("Changed to",process.id, current_time)
       schedule.append((current_time,process.id))
       waiting_time = waiting_time + (current_time - process.arrive_time)
       print("Waiting time is",waiting_time)
       current_time = current_time + process.burst_time
       print("Curr time is", current_time)
   average_waiting_time = waiting_time/float(len(process_list))
   return schedule, average_waiting_time

def print_q(process_queue):
   for p in process_queue:
       print(p.id, end =" ")

def get_proc(cur_time, process_queue,proc_position,process_list):
   j=proc_position
   #print("In function proc_pos:",proc_position, " cur_time is ", cur_time, end=" ")
   for i in range(proc_position, len(process_list)):
       #print(i,process_list[i],process_list[i].arrive_time)
       if process_list[i].arrive_time <= cur_time :
           process_queue.append(process_list[i])
           j=i+1
   #print(" before return queue :", end =" ")
   #print_q(process_queue)
   #print("\n")
   return process_queue, j


#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
   #print(process_list)
   process_list_copy = copy.deepcopy(process_list)
   tot_num_processes=len(process_list_copy)
   #print("tot proc", tot_num_processes)
   cur_time = 0
   completed_proc=0
   prev_proc=None
   schedule = []
   process_queue = []
   proc_position = 0
   while completed_proc < tot_num_processes:
       process_queue,proc_position = get_proc(cur_time, process_queue,proc_position,process_list_copy)
       #print("Initial Queue",process_queue)
       while len(process_queue) > 0:
           # Always take the first process from the queue
           process = process_queue[0]
           # If new proc, write the proc in schedule
           if prev_proc == None:
               prev_proc = process
               schedule.append((cur_time, process.id))
           elif prev_proc != process:
               schedule.append((cur_time, process.id))
               prev_proc = process

           # Waiting time for each process
           process.waiting_time += cur_time - process.lastSchedule_time

           # Run the process for time quoantum or process burst time
           if process.burst_time <= time_quantum:
               cur_time += process.burst_time
               process.lastSchedule_time = cur_time
               process.burst_time = 0
               #print("cur_time",cur_time,"proc", process.id, " doneeeeeeeeeeeeeeeeeeeeeee after wait time ", process.waiting_time)
               process_queue.remove(process)
               process_queue, proc_position = get_proc(cur_time, process_queue, proc_position, process_list_copy)
               completed_proc += 1
               if(completed_proc == tot_num_processes):
                   break
           elif process.burst_time > time_quantum:
               cur_time += time_quantum
               process.lastSchedule_time = cur_time
               process.burst_time -= time_quantum
               #print("cur_time",cur_time,"proc", process.id, " executed for ",time_quantum,"after wait time ", process.waiting_time)
               process_queue, proc_position = get_proc(cur_time, process_queue, proc_position, process_list_copy)
               process_queue.append(process_queue.pop(0))

       cur_time += 1
   #print(schedule)
   # Calculating avg waiting time
   tot_wait = 0
   for process in process_list_copy:
       tot_wait += process.waiting_time
   avg_wait_time = tot_wait / tot_num_processes
   return schedule, avg_wait_time

def SRTF_scheduling(process_list):
   process_list_copy = copy.deepcopy(process_list)
   tot_num_processes = len(process_list_copy)
   # print("tot proc", tot_num_processes)
   cur_time = 0
   completed_proc = 0
   prev_proc = None
   schedule = []
   process_queue = []
   proc_position = 0
   while completed_proc < tot_num_processes:
       process_queue,proc_position = get_proc(cur_time, process_queue,proc_position,process_list_copy)
       #print(process_queue)
       while len(process_queue) > 0:
           process_queue.sort(key= lambda x: x.burst_time)
           #print(process_queue)
           process = process_queue[0]
           #print("Scehduling ",process_queue[0].id)
           if prev_proc == None:
               prev_proc = process
               schedule.append((cur_time, process.id))
           elif prev_proc != process:
               schedule.append((cur_time, process.id))
               prev_proc = process

           process.waiting_time += cur_time - process.lastSchedule_time
           # Run the proc for 1 time unit
           process.burst_time -= 1
           cur_time += 1
           # Get new list of proc available
           process_queue, proc_position = get_proc(cur_time, process_queue, proc_position, process_list_copy)

           process.lastSchedule_time = cur_time
           # Increment count if process completes
           if process.burst_time == 0:
               process_queue.remove(process)
               completed_proc += 1
       cur_time += 1
   #print(schedule)
   # Calculating avg waiting time
   tot_wait = 0
   for process in process_list_copy:
       tot_wait += process.waiting_time
   avg_wait_time = tot_wait / tot_num_processes
   return schedule, avg_wait_time

def find_expected_burst_time(actual_burst_time,predicted_burst_time,alpha):
   expected_burst_time = (alpha*actual_burst_time) + ((1-alpha) * predicted_burst_time)
   return expected_burst_time

def SJF_scheduling(process_list, alpha):
   cur_time = 0
   waiting_time = 0
   current_processing_queue = []
   schedule = []
   process_list_copy = copy.deepcopy(process_list)
   initial_guess = 5
   completed_proc = 0
   expected_burst_time = {}
   tot_num_processes=len(process_list)
   for process in process_list_copy:
       expected_burst_time[process.id] = initial_guess
   while completed_proc < tot_num_processes:
       while len(process_list_copy) > 0:
           tba_process = process_list_copy[0]
           process_arrival_time = tba_process.arrive_time
           if process_arrival_time <= cur_time:
               process_id = tba_process.id
               tba_process.expected_burst_time = expected_burst_time[process_id]
               current_processing_queue.append(tba_process)
               process_list_copy.pop(0)
           else:
               break

       if len(current_processing_queue) > 0:
           current_processing_queue = sorted(current_processing_queue, key=lambda process: process.expected_burst_time)
           current_process = current_processing_queue.pop(0)
           waiting_time += (cur_time - current_process.lastSchedule_time)
           completed_proc += 1  # current process done
           schedule.append((cur_time, current_process.id))  # processing
           cur_time += current_process.burst_time
           expected_burst_time[current_process.id] = find_expected_burst_time(current_process.burst_time, current_process.expected_burst_time, alpha)
       else:
           cur_time += 1

   avg_wait_time = waiting_time / tot_num_processes
   #print(avg_wait_time)
   return schedule, avg_wait_time

def read_input():
   result = []
   with open(input_file) as f:
       for line in f:
           array = line.split()
           if (len(array)!= 3):
               print ("wrong input format")
               exit()
           result.append(Process(int(array[0]),int(array[1]),int(array[2])))
   return result
def write_output(file_name, schedule, avg_waiting_time):
   with open(file_name,'w') as f:
       for item in schedule:
           f.write(str(item) + '\n')
       f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
   process_list = read_input()
   print ("printing input ----")
   for process in process_list:
       print (process)
   #print (Changed"simulating FCFS ----")
   #FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
   #write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
   print ("simulating RR ----")
   #print("proc list b4 RR",process_list)
   min_val = None
   min_pos = 0
   RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list, time_quantum=2)
   # This code was used to test multiple values for quantum and find minimum avg time value
   '''for i in range(1,1000):
       RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = i)
       print("For ",i,"waiting time:",RR_avg_waiting_time)
       if min_val == None:
           min_val = RR_avg_waiting_time
       else:
           if RR_avg_waiting_time < min_val:
               min_val = RR_avg_waiting_time
               min_pos = i
   print("the min pos and min value is ", min_pos, min_val)'''

   #print("proc list after RR", process_list)
   write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
   print ("simulating SRTF ----")
   SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
   write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
   print ("simulating SJF ----")
   SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.75)
   write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
   main(sys.argv[1:])
