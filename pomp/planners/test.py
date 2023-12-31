from __future__ import print_function,division
from six import iteritems
from builtins import range

from .profiler import Profiler
import time

def testPlanner(planner,numTrials,maxTime,filename,**params):
    id = 0
    if 'data_id' in params:
        id = params['data_id']
    print("Testing planner for %d trials, %f seconds"%(numTrials,maxTime))
    print("Saving to",filename)
    if id == 0:
        f = open(filename,'w')
        f.write("data_id,trial,plan iters,plan time,best cost\n")
    elif id > 0:
        f = open(filename,'a')
    for trial in range(numTrials):
        print()
        print("Trial",trial+1)
        planner.reset()
        curCost = float('inf')
        t0 = time.time()
        numupdates = 0
        iters = 0
        hadException = False
        while time.time()-t0 < maxTime:
            try:
                planner.planMore(10)
            except Exception as e:
                if hadException:
                    print("Warning, planner raise two exceptions in a row. Quitting")
                    break
                else:
                    import traceback
                    traceback.print_exc()
                    print("Warning, planner raised an exception... soldiering on")
                    print(e)
                    hadException = True
                    continue
            iters += 10
            if planner.bestPathCost != None and planner.bestPathCost != curCost:
                numupdates += 1
                curCost = planner.bestPathCost
                t1 = time.time()
                # f.write(str(id)+","+str(trial)+","+str(iters)+","+str(t1-t0)+","+str(curCost)+'\n')
        if hasattr(planner,'stats'):
            print
            temp = Profiler()
            temp.items["Stats:"] = planner.stats
            temp.pretty_print()
        print()
        print("Final cost:",curCost)
        print()

        f.write(str(id)+","+str(trial)+","+str(iters)+","+str(maxTime)+","+str(curCost)+'\n')
    f.close()
