# Dynamic Cage as Stability Measure
MPPI manipulation planning with a cage-based instability cost.

Requirements:
- Python 2.X or 3.X
- Numpy/Scipy
- PyOpenGL
- Matplotlib (optional)

Usage:

1.
Run test_mppi.py first to generate sample features in a dataset by rolling out MPPI given random starts and goals. 

Then run cagelabeler.py to label each sample by running AO-RRT. Set vis to 0, your desired runtime (sec).


2.
  "python main.py [-v] [PROBLEM] [PLANNER]"

where -v is an optional flag to show the planner in a GUI.  If not specified,
the planner is run 10 times on the given problem and stats are saved to
disk.  You can also name multiple planners.

[PROBLEM] can be any of:
 - "Bugtrap"
 - "Kink"
 - "Pendulum" 
 - "Dubins" 
 - "Dubins2"
 - "DoubleIntegrator"
 - "Flappy"
 - "CageMovingObstacle"

[PLANNER] can be any of
 - "r-rrt"
 - "r-est"
 - "r-rrt-prune"
 - "r-est-prune"
 - "ao-rrt"
 - "ao-est"
 - "stable-sparse-rrt" 
 - "sst*" 
 - "all": run all planners
You may also add keyword arguments to change parameters of the planner, e.g.
"r-rrt(numControlSamples=1)".

Visualization controls:

- 'p' will do 1000 iterations of planning
- ' ' will do a single iteration.
- 'm' will start saving frames to disk every 100 iterations of planning, which
  can be later turned into a movie.

Once data has been saved to disk, you can run:

   "python processresults.py [folder]"

to generate a csv file summarizing all of the results for a single
problem.  If you have matplotlib, you can then view the results using

   "python viewsummary [file]"


