# Written by Vamei
import os
import multiprocessing
import time
#==================
# input worker
def inputQ(queue):
    info = str(os.getpid()) + '(put):' + str(time.time())
    queue.put(info)

# output worker
def outputQ(queue,lock):
    info = queue.get()
    lock.acquire()
    print (str(os.getpid()) + '(get):' + info)
    lock.release()

if __name__ == '__main__':
    #===================
    # Main
    record1 = []   # store input processes
    record2 = []   # store output processes
    lock  = multiprocessing.Lock()    # To prevent messy print
    queue = multiprocessing.Queue(3)

    multiprocessing.freeze_support()

    # input processes
    for i in range(10):
        process = multiprocessing.Process(target=inputQ,args=(queue,))
        process.start()
        record1.append(process)

    # output processes
    for i in range(10):
        process = multiprocessing.Process(target=outputQ,args=(queue,lock))
        process.start()
        record2.append(process)

    for p in record1:
        p.join()

    queue.close()  # No more object will come, close the queue

    for p in record2:
        p.join()
