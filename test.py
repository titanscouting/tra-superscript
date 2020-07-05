import threading
from multiprocessing import Process, Queue
import time
from os import system

class testcls():

	i = 0
	j = 0

	t1_en = True
	t2_en = True

	def main(self):
		t1 = Process(name = "task1", target = self.task1)
		t2 = Process(name = "task2", target = self.task2)
		t1.start()
		t2.start()
		#print(self.i)
		#print(self.j)
		
	def task1(self):
		self.i += 1
		time.sleep(1)
		if(self.i < 10):
			t1 = Process(name = "task1", target = self.task1)
			t1.start()

	def task2(self):
		self.j -= 1
		time.sleep(1)
		if(self.j > -10):
			t2 = t2 = Process(name = "task2", target = self.task2)
			t2.start()
"""
if __name__ == "__main__":

	tmain = threading.Thread(name = "main", target = main)
	tmain.start()

	t = 0
	while(True):
		system("clear")
		for thread in threading.enumerate():
			if thread.getName() != "MainThread":
				print(thread.getName())
		print(str(len(threading.enumerate())))
		print(i)
		print(j)
		time.sleep(0.1)
		t += 1
		if(t == 100):
			t1_en = False
			t2_en = False
"""