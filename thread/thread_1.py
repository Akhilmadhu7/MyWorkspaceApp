import threading, time

lock = threading.Lock()

def update_list_a(shared_list):
    
    print("lock b: ", lock)
    lock.acquire()
    print("a lock has been acquired.")
    for _ in range(3):
        shared_list.append('A')
        time.sleep(1)
    print("a lock has been released.")
    lock.release()

def update_list_b(shared_list):
    
    print("lock: ", lock)
    lock.acquire()
    print("b lock has been acquired.")
    for _ in range(3):
        shared_list.append('B')
        time.sleep(1)
    print("b lock has been released.")
    lock.release()
    print("a completely released.")

shared_list = []


t1 = threading.Thread(target=update_list_a, args=(shared_list,))
print("theading active count: ", threading.active_count())
t2 = threading.Thread(target=update_list_b, args=(shared_list,))
t1.start()
t2.start()
print("theading active count: ", threading.active_count())

t1.join()
t2.join()
print("shared list: ", shared_list)