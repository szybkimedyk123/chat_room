from threading import Thread
import subprocess

t1 = Thread(target=subprocess.run, args=(["python", "server.py"],))
t2 = Thread(target=subprocess.run, args=(["python", "client1.py"],))
#t3 = Thread(target=subprocess.run, args=(["python", "client2.py"],))

t1.start()
t2.start()
#t3.start()

t1.join()
t2.join()
#t3.join()