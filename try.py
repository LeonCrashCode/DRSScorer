import multiprocessing

def worker(procnum, return_dict):
    '''worker function'''
    print(str(procnum) + ' represent!')
    if "ret" not in return_dict:
        return_dict["ret"] = procnum
    else:
        return_dict["ret"] += procnum


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for i in range(10):
        p = multiprocessing.Process(target=worker, args=(i,return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    print(return_dict.values())