#############################
# bistable regulatory model #
# july 17, 2017
# David L Gibbs, dgibbs@systemsbiology.org

# variable names from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3098230/
# in the paper --- in the code
#   Kx+  ---  kxp
#   Ky+  ---  kyp
#   Kx-  ---  kxd
#   Ky-  ---  kyd
# the rest are pretty similar

import copy
import numpy as np
import random  # [Boris] for random walk


def nextStep(kxp, kyp, kxy, kyx, x, y, x0, y0, kxx, kyy, kxd, kyd):
    # here we are going to take the current values of x and y
    # along with the rate constants (k*)
    # and we're going to calculate the *change* in x and y
    # kxp: rate that X is produced (p for produced)
    # kyp: rate that Y is produced (p for produced)
    # kxd: rate that X is degraded (d for degrading)
    # kyd: rate that Y is degraded
    # kxx: rate that X binds to gene x (self activation)
    # kyy: rate that Y binds to self
    # kxy: rate of cross-binding, X to Y
    # kyx: rate of cross-binding, Y to X
    dxdt = (kxp * kxy * x0) * (x / ((kxx + x) * (kxy + y))) - kxd * x
    dydt = (kyp * kyx * y0) * (y / ((kyy + y) * (kyx + x))) - kyd * y
    return( (dxdt, dydt) )


def run_timecourse(kxp, kyp, kxy, kyx, x, y, x0, y0, kxx, kyy, kxd, kyd, maxsteps):
    # main loop
    dt = 0.01  # time step for simulation taken from the paper [Boris]
    std_rw = 0.1 # standard deviation of random walk ( sqrt( 2*D*dt )), obtained from the paper [Boris]
    timecourse = [(x,y)]
    curr_x = x
    curr_y = y
    for t in range(0,maxsteps):
        x_y_diff = nextStep(kxp,kyp,kxy,kyx,curr_x,curr_y,x0,y0,kxx,kyy,kxd,kyd)
        #curr_x += x_y_diff[0]
        #curr_y += x_y_diff[1]
        curr_x += x_y_diff[0]*dt + std_rw*np.random.normal() # [Boris] solution plus random motion
        curr_y += x_y_diff[1]*dt + std_rw*np.random.normal() # [Boris] equations 3.12 ans 3.13
        timecourse.append( (curr_x, curr_y) )
    return(timecourse)



def score_redef(idx):
    # if the score is empty it's in the first grid square
    # otherwise it's 1+index.
    if len(idx) == 0:
        return(0)
    else:
        return(1+np.max(idx))


def grid_score(x_y_pair):
    # here the "**" indicate the "grid squares"
    # ** 0.2 ** 0.4 ** 0.6 ** 0.8 ** #
    grid_dividers = np.array([0.2, 0.4, 0.6, 0.8]) # [Boris] here we can increase resolution
    x = x_y_pair[0]
    y = x_y_pair[1]
    i = score_redef( np.where(x > grid_dividers)[0] )
    j = score_redef( np.where(y > grid_dividers)[0] )
    return( (i,j) )


def norm_timecourse(xys):
    new_tuples = []
    max_x = -1.0
    max_y = -1.0
    for xyi in xys:
        if xyi[0] > max_x:
            max_x = xyi[0]
        if xyi[1] > max_y:
            max_y = xyi[1]
    for i in range(0,len(xys)):
        new_tuples.append(( (xys[i][0] / max_x), (xys[i][1] / max_y)))
    return( new_tuples )


def pxy(kxp, kyp, kxy, kyx, x, y, x0, y0, kxx, kyy, kxd, kyd, maxsteps):
    # first we need a grid of 25
    grid = np.zeros( (5,5) )  # [Boris] we can use a number of bins equal to a multiple of 5, to improve resolution. as a reference in the paper : they used 300 x 300 bins.
    # then we run the simulation
    xylevels = run_timecourse(kxp, kyp, kxy, kyx, x, y, x0, y0, kxx, kyy, kxd, kyd, maxsteps)
    # have to normalize the values of X and Y to the range of 0-1
    xynorm = norm_timecourse(xylevels)
    # then populate the grid
    for xy in xynorm:
        (i,j) = grid_score(xy) # where to put this time point
        grid[i,j] += 1.0
    return(grid)


def checkConverged(newgrid, oldgrid, eps):
    newgrid_norm = newgrid / np.sum(newgrid)
    oldgrid_norm = oldgrid / np.sum(oldgrid)
    diff = np.sum(np.abs(newgrid_norm - oldgrid_norm))
    # print(diff)
    return(abs(diff) < eps)


def converge(kxp, kyp, kxy, kyx, x, y, x0, y0, kxx, kyy, kxd, kyd, maxsteps, convsteps, eps):
    # run a little, check if we're converged, then run a little more.
    lastgrid = np.zeros( (5,5) )
    newgrid  = np.zeros( (5,5) )
    converged = 0
    lastgrid[0][0] = 1
    while converged == 0 and convsteps > 0:
        # add some new time series
        newgrid += pxy(kxp, kyp, kxy, kyx, x, y, x0, y0, kxx, kyy, kxd, kyd, maxsteps)
        if checkConverged(newgrid, lastgrid, eps):
            converged = 1 # and we're done
        else:
            lastgrid = copy.deepcopy(newgrid)
        convsteps -= 1
    newgrid_norm = (newgrid / np.max(newgrid)) * 12 - 6
    #newgrid_norm = newgrid
    return(newgrid_norm)


def get_Z_vals(params):
    x0 = 1     # "amount" of x promoter
    y0 = 1     # "amount" of y promoter
    x = 1      # starting level of X
    y = 1      # starting level of Y
    kxp = params[0]  # kxp: rate that X is produced (p for produced)
    kyp = params[1]  # kyp: rate that Y is produced (p for produced)
    kxy = params[2]  # kxy: rate of cross-binding, X to Y
    kyx = params[3]  # kyx: rate of cross-binding, Y to X
    kxx = params[4] # kxx: rate that X binds to Xs promoter
    kyy = params[5] # kyy: rate that Y binds to Ys promoter
    kxd = params[6]  # kxd: rate that X is degraded (d for degrading)
    kyd = params[7]  # kyd: rate that Y is degraded
    maxsteps = 1000 # [Boris] As reference in the paper they simulated 10^8 time steps
    convsteps = 1000
    eps = 0.005
    res0 = converge(kxp, kyp, kxy, kyx, x, y, x0, y0, kxx, kyy, kxd, kyd, maxsteps, convsteps, eps)
    res0 = np.fix(res0)
    res0 = res0.astype(int)
    res0 = res0.flatten()
    res0 = res0.tolist()
    return_order = [0,24,4,20,1,23,9,15,3,21,5,19,10,14,2,22,6,18,8,16,7,17,13,11,12]
    res0 = [ res0[i] for i in return_order]
    return (res0)
