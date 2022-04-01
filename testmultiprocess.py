from multiprocessing import Lock, Pool, Pipe
import time

def function(index):
    print("start process:",index)
    time.sleep(10)
    print("end")

if __name__ == '__main__':
    pool = Pool(processes = 3)
    for i in range(4):
        pool.apply_async(function,(i,))

    pool.close()
    pool.join()

