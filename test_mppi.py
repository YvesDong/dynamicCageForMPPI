import sys
sys.path.append('/home/yif/Documents/KTH/git/dynamicCageForMPPI/mppi')
import numpy as np
import torch
import logging
import math
from pomp.mppi.mppi import *
import random
import csv

if __name__ == "__main__":
    problem_name = 'PlanePush'
    if problem_name == 'PlanePush':
        fake_data = [5.0, 4.3, 0.0, 0.0, 0.0, 0.0, 
                    5.3, 4.0, 0.0, 0.0, 1.0, 0.0]
        dynamics_sim = forwardSimulationPlanePushPlanner(gui=0)
        cage = PlanePush(fake_data, dynamics_sim)
        goal_threshold = 0.22 # half of the width of the box
    elif problem_name == 'BalanceGrasp':
        pass

    N_EPISODE = 1
    N_ITER = 30 # max no. of iterations
    N_SAMPLE = 300 # 1000  # K
    N_HORIZON = 15  # T, MPPI horizon
    nx = len(fake_data)
    nu = cage.nu - 1 # expect time as the first element of action
    dt = .3 # 0.15 # fixed time step
    num_vis_samples = 2
    lambda_ = 1.
    gravity = 9.81
    d = "cuda"
    dtype = torch.double
    u_init = torch.tensor([0.0,]*3, device=d, dtype=dtype) # in OpenGL frame
    noise_mu = torch.zeros_like(u_init, device=d, dtype=dtype)
    noise_sigma = 1 * torch.eye(nu, device=d, dtype=dtype)
    # noise_sigma[2,2] = 0.5

    # For reproducibility
    # randseed = 5
    # if randseed is None:
    #     randseed = random.randint(0, 1000000)
    # random.seed(randseed)
    # np.random.seed(randseed)
    # torch.manual_seed(randseed)
    # print("random seed %d", randseed)

    def running_cost(state, action,):
        '''state and state_goal: torch.tensor()'''
        # weight = 1.
        # cost = (state_goal[0]-state[0])**2 + (state_goal[1]-state[1])**2
        cost = abs(state[1]-cage.y_obstacle)
        # cost = angle_normalize(theta) ** 2 + 0.1 * theta_dt ** 2 + 0.001 * action ** 2
        return cost

    def terminal_state_cost(state, weight=3.):
        '''state and state_goal: torch.tensor()'''
        cost_goal = weight * abs(state[1]-cage.y_obstacle)
        # cost_goal = weight * (state_goal[0]-state[0])**2 + (state_goal[1]-state[1])**2
        # stability_cage = predict(mppi.model, state.reshape(-1, mppi.nx), mppi.scaler_scale, mppi.scaler_min)[0,0]
        # cost_cage = 2.*weight / (.01 + 2*torch.max(stability_cage, torch.tensor(1e-3))) # torch.Size([self.nx,1]), gpu
        # print('TERM cost_goal',cost_goal)
        # print('TERM cost_cage',cost_cage)
        # return cost_goal + cost_cage
        return cost_goal
    
    mppi_gym = MPPI(nx, 
                    nu, 
                    cage, 
                    K=N_SAMPLE, 
                    T=N_HORIZON, 
                    running_cost=running_cost, 
                    terminal_state_cost=terminal_state_cost, 
                    lambda_=lambda_, 
                    goal_thres=goal_threshold,
                    num_vis_samples=num_vis_samples, 
                    noise_mu=noise_mu, 
                    noise_sigma=noise_sigma, 
                    u_init=u_init, 
                    dt=dt, 
                    device=d)

    # Save data to a CSV file with headers
    filename = "states_from_mppi.csv"
    headers = ['n_episode', 'n_iteration', 'n_sample', 'n_horizon', 'xo', 'yo',  'thetao', 'vxo', 'vyo',  'omegao',
               'xg', 'yg', 'thetag', 'vxg', 'vyg', 'omegag']
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
    # Randomize start and goal
    randomize = 0
    for e in range(N_EPISODE):
        data = []
        if randomize:
            params = [
                (cage.x_range-2)*random.random() + 1, # xo_init
                (cage.y_range-2)*random.random() + 1, # yo_init
                0.8*math.pi*random.random() - 0.4*math.pi, # thetao_init
                (cage.x_range-2)*random.random() + 1, # xg_init
                (cage.y_range-2)*random.random() + 1, # yg_init
                ]
        else:
            params = [3,6,0,3,5.5,]
        mppi_gym._reset_start_goal(params)

        rollouts_hist, cutdown_hist, cutdown_iter = run_mppi(mppi_gym, iter=N_ITER, episode=e)
        # rollouts_hist = torch.tensor((iter, mppi.num_vis_samples, mppi.T+1, mppi.nx))
        # cutdown_hist = torch.tensor((iter, mppi.num_vis_samples))

        # Process data to save
        for i in range(cutdown_iter):
            for s in range(mppi_gym.num_vis_samples):
                cutoff = int(cutdown_hist[i, s].item()) # cutoff in the horizon
                # print('cutoff',cutoff)
                selected_data = rollouts_hist[i, s, 1:cutoff, :]
                
                for h in range(cutoff-1):
                    selected_data_list = selected_data[h, :].tolist()
                    data.append([e, i, s, h,] + selected_data_list)
        
        # Save data to a CSV file
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)