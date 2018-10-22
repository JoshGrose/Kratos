from __future__ import absolute_import, division #makes KratosMultiphysics backward compatible with python 2.6 and 2.7

import KratosMultiphysics as Kratos
# KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING) # avoid printing of Kratos things
Kratos.Logger.GetDefaultOutput().SetSeverity(Kratos.Logger.Severity.WARNING)
import KratosMultiphysics.MyStochasticLaplacianApplication as Poisson    

from analysis_stage import AnalysisStage

import numpy as np
import time

from pycompss.api.task import task
from pycompss.api.api import compss_wait_on
from pycompss.api.parameter import *

class MultilevelMonteCarloLaplacianAnalysis(AnalysisStage):
    """Main script for MultilevelMonte Carlo Poisson simulations using the pure_diffusion solver"""

    
    def __init__(self,model,parameters,sample):
        self.sample = sample
        super(MultilevelMonteCarloLaplacianAnalysis,self).__init__(model,parameters)

            
    def _CreateSolver(self):
        import pure_diffusion_solver
        solver = pure_diffusion_solver.CreateSolver(self.model,self.project_parameters["solver_settings"])
        self.PureDiffusionSolver = solver
        return self.PureDiffusionSolver

    
    def _GetSimulationName(self):
        return "Multilevel Monte Carlo Poisson Analysis"

    
    def ApplyBoundaryConditions(self):
        super(MultilevelMonteCarloLaplacianAnalysis,self).ApplyBoundaryConditions()
        ## define the forcing function
        for node in self.model.GetModelPart("MLMCLaplacianModelPart").Nodes:
            coord_x = node.X
            coord_y = node.Y
            # forcing = -432.0 * coord_x * (coord_x - 1) * coord_y * (coord_y - 1)
            forcing = -432.0 * (coord_x**2 + coord_y**2 - coord_x - coord_y)
            node.SetSolutionStepValue(Poisson.FORCING,forcing*self.sample)            
        # print("SAMPLE = ",self.sample)
            ############################################################################################################################################################################################
            ## need to use SetSolutionStepValue and not SetValue (equivalent for GetSolutionStepValue and GetValue) because in custom_elements and custom_conditions I use this function              ##
            ## Set/GetValue uses less memory and is always used for element and conditions                                                                                                            ##
            ## Set/GetSolutionStepValue uses more memory, and allows to memorize values stored in the nodes in case of buffer > 1 (e.g. sol_{i-1}, sol_{i-2} remain stored there to evaluate sol_{i}) ##
            ## if I use SetValue, I need to use GetValue (the same for the other)                                                                                                                     ##
            # node.SetValue(Poisson.FORCING,node.GetSolutionStepValue(Poisson.FORCING)*sample)                                                                                                        ##
            ############################################################################################################################################################################################


    
###########################################################
######## END OF CLASS MONTECARLOLAPLACIANANALYSIS #########
###########################################################



def GenerateStochasticContribute(parameters):
    number_samples = 1 # i.e. generate one stochastic variable per time

    if (parameters["problem_data"].Has("stochastic_pdf")):
        stochastic_pdf = parameters["problem_data"]["stochastic_pdf"]
        print(stochastic_pdf)
    else:
        raise Exception('Please provide the "stochastic_pdf" parameter in the .json file')

    if stochastic_pdf.Has("normal_distribution"):
        if stochastic_pdf["normal_distribution"].Has("mean"):
            mu = stochastic_pdf["normal_distribution"]["mean"].GetDouble()
        else:
            raise Exception('Please define the "mean" for the normal distribution in the .json file')            
        if stochastic_pdf["normal_distribution"].Has("variance"):
            sigma = stochastic_pdf["normal_distribution"]["variance"].GetDouble()
        else:
            raise Exception('Please define the "variance" for the normal distribution in the .json file')
        sample = np.random.normal(mu,sigma,number_samples)

    elif stochastic_pdf.Has("beta_distribution"):
        if stochastic_pdf["beta_distribution"].Has("alpha"):
            alpha = stochastic_pdf["beta_distribution"]["alpha"].GetDouble()
        else:
            raise Exception('Please define the "alpha" for the beta distribution in the .json file')            
        if stochastic_pdf["beta_distribution"].Has("beta"):
            beta = stochastic_pdf["beta_distribution"]["beta"].GetDouble()
        else:
            raise Exception('Please define the "beta" for the beta distribution in the .json file')
        sample = np.random.beta(alpha,beta,number_samples)

    else:
        raise Exception('Please provide "normal_distribution" or "beta_distribution" in the .json file; at the moment only "normal_distribution" and "beta_distribution" are implemented')
    return sample

def GenerateBetaSample(alpha,beta):
    number_samples = 1
    sample = np.random.beta(alpha,beta,number_samples)
    return sample


def EvaluateQuantityOfInterest(simulation):
    """here we evaluate the QoI of the problem: int_{domain} SOLUTION(x,y) dx dy
    we use the midpoint rule to evaluate the integral"""
    Kratos.CalculateNodalAreaProcess(simulation._GetSolver().main_model_part,2).Execute()
    Q = 0.0
    SolArray = []
    for node in simulation._GetSolver().main_model_part.Nodes:
        Q = Q + (node.GetSolutionStepValue(Kratos.NODAL_AREA)*node.GetSolutionStepValue(Poisson.SOLUTION))
        #print("NODAL AREA = ",node.GetSolutionStepValue(Kratos.NODAL_AREA),"NODAL SOLUTION = ",node.GetSolutionStepValue(Poisson.SOLUTION),"CURRENT Q = ",Q)
    return Q


def Nf_law(lev):
        # refinement strategy:
        # uniform mesh on level lev with h_lev=(1/N0)*2^(-lev)
        # i.e. level = 0, h_{lev=0} = 0.25
        #      level = 1, h_{lev=1} = 0.2/2 = 0.125
        #      level = 2, h_{lev=2} = 0.2/4 = 0.0625
        #      ...
        # I wrote the following
        # N0 = 4.
        # M  = 2.
        # NFF = (N0*np.power(M,lev))
        # Nf2 = 2*NFF**2
        # Nobile wrote the following
        N0 = 5.
        M  = 2.
        NFF = (N0*np.power(M,lev))
        Nf2 = NFF**2
        # NFF is the number of elements on a boundary line
        # Nf2 is the number of triangular elements in the square domain (approximately, if mesh non uniform)
        return Nf2


def update_onepass_M(sample, old_mean, old_M2, nsam):
    # update mean and second moment values
    # M_{2,n} = sum_{i=1}^{n} (x_i - mean(x)_n)^2
    # M_{2,n} = M_{2,n-1} + (x_n - mean(x)_{n-1}) * (x_n - mean(x)_{n})
    # s_n^2 = M_{2,n} / (n-1)
    delta = np.subtract(sample, old_mean)
    if nsam == 1:
        new_mean = sample
        new_M2 = np.zeros(np.size(sample))
        new_M2 = np.asscalar(new_M2) # do so to have a list of scalars, and not a list of arrays of one element
    else:
        new_mean = old_mean + np.divide(delta,nsam)
        new_M2 = old_M2 + delta*np.subtract(sample,new_mean)

    return new_mean, new_M2


def compute_sample_variance_from_M2(M2,nsam):
    sample_variance = np.divide(M2,np.subtract(nsam,1))
    return sample_variance


def EstimateBayesianVariance(mean,variance,parameters,ratesLS,nDoF,nsam,level_local):
    k0 = parameters[0]
    k1 = parameters[1]
    Calfa = ratesLS[0]    
    alfa  = ratesLS[1]
    Cbeta = ratesLS[2]    
    beta  = ratesLS[3]

    # use local variables, in order to not modify the global variables
    mean_local = mean[:]
    variance_local = variance[:]
    nsam_local = nsam[:]
    if len(mean_local) < (level_local+1):
        count = (level_local+1)-len(mean_local)
        for i_count in range(0,count):
            mean_local.append(0.0)
    if len(variance_local) < (level_local+1):
        count = (level_local+1)-len(variance_local)
        for i_count in range(0,count):
            variance_local.append(0.0)
    if len(nsam_local) < (level_local+1):
        count = (level_local+1)-len(nsam_local)
        for i_count in range(0,count):
            nsam_local.append(0)

    BayesianVariance = []
    for level in range (0, (level_local+1)):
        mu = Calfa*nDoF[level]**(-alfa)
        lam = (1/Cbeta)*nDoF[level]**(beta)
        G1_l = 0.5 + np.multiply(k1,lam) + np.divide(nsam_local[level],2.0)
        G2_l = k1 + (nsam_local[level]-1)*0.5*variance_local[level] + k0*nsam_local[level]*((mean_local[level]-mu)**2)/(2.0*(k0+nsam_local[level]))
        BayesianVariance.append(np.divide(G2_l,G1_l-0.5))
    return BayesianVariance


def compute_tollerance_i(parameters,iE,iter_def):
    # compute tollerance for iteration i, using (24) of [PNL16]
    r1 = parameters[2]
    r2 = parameters[3]
    tolF = parameters[5]
    if iter_def <= iE:
        tol = (r1**(iE-iter) * r2**(-1))*tolF
    else:
        tol = (r2**(iE-iter) * r2**(-1))*tolF
    return tol


def compute_ratesLS(bias_ratesLS,variance_ratesLS,cost_ML_ratesLS,ndof_ratesLS):
    bias_ratesLS = np.abs(bias_ratesLS)

    ##################### MEAN - alpha ########################################
    ## NUMPY: linear fit   
    # why not considered also M_{L=0}?
    # considered only for gamma and cgamma
    pa = np.polyfit(np.log2(ndof_ratesLS[1::]),np.log2(bias_ratesLS[1::]),1) # Nobile does not use level = 0 but uses log2, I use log natural
    # pa = np.polyfit(np.log2(ndof_ratesLS),np.log2(bias_ratesLS),1)
    alpha   = -pa[0]
    C1      = 2**pa[1]

    ##################### VAR - beta ########################################## 
    ## NUMPY: linear fit   
    pb          = np.polyfit(np.log2(ndof_ratesLS[1::]),np.log2(variance_ratesLS[1::]),1) # Nobile does not use level = 0
    # pb          = np.polyfit(np.log2(ndof_ratesLS),np.log2(variance_ratesLS),1)  
    beta        = -pb[0]
    C2          = 2**pb[1] 

    ################# COST - gamma ############################################     
    ## NUMPY: linear fit       
    pg          = np.polyfit(np.log2(ndof_ratesLS),np.log2(cost_ML_ratesLS),1) 
    gamma       = pg[0]
    C3          = 2**pg[1]

    paramLS=[C1,alpha,C2,beta,C3,gamma]
    return paramLS

def theta_model(ratesLS,tollerance_i,nDoF):
    Calpha = ratesLS[0]
    alpha = ratesLS[1]
    theta_i = 1.0 - (Calpha * (nDoF)**(-alpha))/tollerance_i
    return theta_i


def compute_levels(tol,nsam,ratesLS,ndof_all,BayesianVariance,mean,variance,parameters,Lmax,Lmin):
    # consider theta_i = 1.0 - (calpha*(M_L**(-alpha)))/tol_i
    # observe I have already computed ndof_all for all the possible levels, i.e. up to Lmax
    Wmin   = 1e10
    Lopt_local = Lmin
    nsam_local = nsam
    Cgamma = ratesLS[4]
    gamma  = ratesLS[5]
    Calpha = ratesLS[0]
    alpha = ratesLS[1]
    Cphi = parameters[6]

    if len(BayesianVariance) < (Lmax+1):
        BayesianVariance = EstimateBayesianVariance(mean,variance,parameters,ratesLS,ndof_all,nsam_local,Lmax)
    # now both ndof_all and BayesianVariance have length = Lmax + 1
    model_cost = np.multiply(Cgamma,np.power(ndof_all,gamma)) # also model_cost has length = Lmax + 1
                                                              # here I obtain values bigger than Nobile, because my simulation times are bigger,
                                                              # and so from the computed values of gamma and Cgamma I get bigger model cost values
    
    for lev in range(Lmin, Lmax+1):
        # as we see in the deriverable, it is not mandatory to increase the number of levels,
        # and we may continue using the number of levels of the previous iteration, i.e. Lmin
        theta_i = 1.0 - (Calpha * (ndof_all[lev])**(-alpha))/tol # I do not call the def "theta_model",
                                                             # because I cannot use a task inside a task
        if (theta_i > 0.0) and (theta_i < 1.0):
            # update the cost in future: for the levels we know use cost_ML
            #                            for the levels we do not know use "cgamma*Ml**gamma"
            coeff2 = np.sum(np.sqrt(np.multiply(model_cost[0:lev+1],BayesianVariance[0:lev+1])))
            coeff2 = coeff2**2.0
            coeff1 = (Cphi/(theta_i*tol))**2.0 # formula in case QoI is scalar
            
        else:
            raise Exception ("The splitting parameter theta_i assumed a value outside the range (0,1)")

        Wtot = coeff1 * coeff2
        print("print level and correspondent cost",lev,Wtot)
        if Wtot < Wmin:
            Wmin = Wtot
            Lopt_local = lev
    
    if Lopt_local > Lmin:
        Lopt_local = Lmin + 1
            # i.e. I add one level per time!!!
            # note that the number of levels start from 0, not from 1,
            # so we have a difference of one between the number of levels
            # and the length of the arrays
            # (e.g. difference_value, ndof_all or number_sample)
    BayesianVariance = BayesianVariance[0:Lopt_local+1] # need to leave Lopt, and so the new BayesianVariance value,
                                                  # because I need this value in compute number of samples
    
    return Lopt_local, BayesianVariance, Lmin


def compute_number_samples(L_opt,BayesianVariance,ratesLS,theta,tol,nDoF,nsam,parameters):
    minNadd = np.multiply(np.ones(L_opt+1),6.)
    Cgamma = ratesLS[4]
    gamma  = ratesLS[5]
    Calpha = ratesLS[0]
    Cphi = parameters[6]
    ndof_local = nDoF[0:L_opt+1]

    coeff1 = (Cphi/(theta*tol))**2.0
    model_cost = np.multiply(Cgamma,np.power(ndof_local,gamma))

    coeff2 = np.sqrt(np.divide(BayesianVariance,model_cost))
    coeff3 = np.sum(np.sqrt(np.multiply(model_cost,BayesianVariance)))
       
    opt_number_samples = np.multiply(coeff1*coeff3,coeff2)
    
    for i in range (0,len(opt_number_samples)):
        opt_number_samples[i] = np.ceil(opt_number_samples[i])
        opt_number_samples[i] = opt_number_samples[i].astype(int)

    if len(nsam) < len(opt_number_samples):
        for i in range (0,len(opt_number_samples)-len(nsam)):
            nsam.append(0)
    previous_number_samples = nsam[:]

    dNsam = []
    for l in range(0,L_opt+1):
        dNsam.append(opt_number_samples[l] - nsam[l])
        if dNsam[l] <= 0.:
            dNsam[l] = 0.
            opt_number_samples[l] = nsam[l]
            # i.e. here I set that if NlOPT[l] is smaller than the previous
            # number of samples, I keep the previous number of samples
  
        if (dNsam[l] > 0.) and (dNsam[l] < minNadd[l]):
            dNsam[l] = minNadd[l]
            opt_number_samples[l] = nsam[l] + dNsam[l]
            # i.e. the minimum addition of samples is given by the array minNadd
            # so if the new number of samples would be smaller than the old
            # number of samples, I set to have an addition of minNadd[l] samples          
        
        nsam[l] = opt_number_samples[l]
    for i in range (0,len(dNsam)):
        dNsam[i] = int(dNsam[i])
        # dNsam[i] = dNsam[i].astype(int)
        nsam[i] = int(nsam[i])
        # nsam[i] = nsam[i].astype(int)

    print("New number of samples : ",nsam,"difference with previous iteration",dNsam,"old number samples",previous_number_samples)
    # note that I do not decrease the number of samples wrt previous MLMC iterations!!
    return nsam,dNsam,previous_number_samples


def compute_mean_mlmc_QoI(mean_array):
    mean_mlmc = np.sum(mean_array)
    return mean_mlmc


# def CalcMean(Qlist):
#     aux = 0.0
#     for i_instance in range(0,len(Qlist)):
#         aux = aux + Qlist[i_instance]
#     mean = aux / len(Qlist)
#     print("Mean value evaluated")
#     return mean


# def CalcVariance(Qlist,mean):
#     ## if we want to compute the population variance: mean of (QoI - mean)**2
#     ## we compute the the sample variance, instead of len(Qlist) we divide by (len(Qlist) - 1)
#     aux = 0.0
#     for i_instance in range(0,len(Qlist)):
#         aux = aux + (Qlist[i_instance] - mean) ** 2
#     variance = aux / (len(Qlist)-1)
#     print("Variance value evaluated")
#     return variance


@task(model_part_file_name=FILE_IN, parameter_file_name=FILE_IN, returns=2)
def execution_task(parameter_file_name, sample):
    with open(parameter_file_name,'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())
    local_parameters = parameters # in case there are more parameters file, we rename them
    model = Kratos.Model()      
    simulation = MultilevelMonteCarloLaplacianAnalysis(model,local_parameters, sample)
    simulation.Run() 
    QoI =  EvaluateQuantityOfInterest(simulation)
    return QoI

@task(returns=2)
def mean_task(*args):
    sum_val = 0
    amount_elems = 0
    for i in range(int(len(args) / 2)):
        sum_val = sum_val + (args[2 * i] * args[2 * i + 1])
        amount_elems = amount_elems + args[2 * i]
    return amount_elems, sum_val / amount_elems
    
@task(model_part_file_name=FILE_IN, parameter_file_name=FILE_IN,returns=1)
def exact_execution_task(model_part_file_name, parameter_file_name):
    with open(parameter_file_name,'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())
    local_parameters = parameters # in case there are more parameters file, we rename them
    model = Kratos.Model()      
    local_parameters["solver_settings"]["model_import_settings"]["input_filename"].SetString(model_part_file_name[:-5])
    sample = 1.0
    simulation = MultilevelMonteCarloLaplacianAnalysis(model,local_parameters, sample)
    simulation.Run() 
    QoI =  EvaluateQuantityOfInterest(simulation)
    ExactExpectedValueQoI = 0.25 * EvaluateQuantityOfInterest(simulation)
    return ExactExpectedValueQoI

@task(returns=1)
def compare_mean(AveragedMeanQoI,ExactExpectedValueQoI):
    relative_error = abs((AveragedMeanQoI - ExactExpectedValueQoI)/ExactExpectedValueQoI)
    return relative_error


if __name__ == '__main__':
    from sys import argv
    
    # if len(argv) > 2:
    #     err_msg = 'Too many input arguments!\n'
    #     err_msg += 'Use this script in the following way:\n'
    #     err_msg += '- With default parameter file (assumed to be called "ProjectParameters.json"):\n'
    #     err_msg += '    "python montecarlo_laplacian_analysis.py"\n'
    #     err_msg += '- With custom parameter file:\n'
    #     err_msg += '    "python montecarlo_laplacian_analysis.py <my-parameter-file>.json"\n'
    #     raise Exception(err_msg)

    # if len(argv) == 2: # ProjectParameters is being passed from outside
    #     parameter_file_name = argv[1]
    # else: # using default name
    #     parameter_file_name = "/home/kratos105b/Kratos/applications/MyMultilevelMonteCarloLaplacianApplication/tests/Level0/ProjectParameters.json"

    parameter_file_name =[]
    parameter_file_name.append("/home/kratos105b/Kratos/applications/MyMultilevelMonteCarloLaplacianApplication/tests/Level0/ProjectParameters.json")
    with open(parameter_file_name[0],'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())
    local_parameters_0 = parameters # in case there are more parameters file, we rename them
    parameter_file_name.append("/home/kratos105b/Kratos/applications/MyMultilevelMonteCarloLaplacianApplication/tests/Level1/ProjectParameters.json")
    with open(parameter_file_name[1],'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())
    local_parameters_1 = parameters # in case there are more parameters file, we rename them
    parameter_file_name.append("/home/kratos105b/Kratos/applications/MyMultilevelMonteCarloLaplacianApplication/tests/Level2/ProjectParameters.json")
    with open(parameter_file_name[2],'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())
    local_parameters_2 = parameters # in case there are more parameters file, we rename them
    parameter_file_name.append("/home/kratos105b/Kratos/applications/MyMultilevelMonteCarloLaplacianApplication/tests/Level3/ProjectParameters.json")
    with open(parameter_file_name[3],'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())
    local_parameters_3 = parameters # in case there are more parameters file, we rename them
    parameter_file_name.append("/home/kratos105b/Kratos/applications/MyMultilevelMonteCarloLaplacianApplication/tests/Level4/ProjectParameters.json")
    with open(parameter_file_name[4],'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())
    local_parameters_4 = parameters # in case there are more parameters file, we rename them
    L_max = len(parameter_file_name) - 1
    print("Lmax = ",L_max)

    ## evaluate now the exact expected value of Q (sample = 1.0)
    ExactExpectedValueQoI = exact_execution_task(local_parameters_1["solver_settings"]["model_import_settings"]["input_filename"].GetString() + ".mdpa", parameter_file_name[2])

    # compute parameters of the ML simulation
    parameters_ML_simulation = [0.1, 0.1, 1.25, 1.15, 0.25, 0.1, 1.0]
    k0     = 0.1        # Certainty Parameter 0 rates
    k1     = 0.1        # Certainty Parameter 1 rates
    r1     = 1.25       # Cost increase first iterations C-MLMC
    r2     = 1.15       # Cost increase final iterations C-MLMC
    tol0   = 0.25       # Tolerance iter 0
    tolF   = 0.1        # Tolerance final
    cphi   = 1.0        # confidence on tolerance
    # N0     = 25       # Number of samples for iter 0
    # L0     = 2        # Number of levels for iter 0

    ## Read the number of cycles of the Monte Carlo algorithm from the .json file
    instances = []
    instances.append(local_parameters_0["problem_data"]["number_samples"].GetInt())
    instances.append(local_parameters_1["problem_data"]["number_samples"].GetInt())
    instances.append(local_parameters_2["problem_data"]["number_samples"].GetInt())
    instances = [25,25,25] # set here to handle in a simple way

    difference_QoI = [] # list containing Y_{l}^{i} = Q_{m_l} - Q_{m_{l-1}}
    time_ML = []        # list containing the time to compute the level=l simulations
    number_samples = instances # list containing number of samples for each evel
    L_screening = len(number_samples) - 1 # i.e. L_screening = 3 - 1 = 2
                                          # recall the levels start from zero, so I need to add "-1"

    if len(number_samples) > len(difference_QoI):
        for i in range (0,len(number_samples)-len(difference_QoI)):
            difference_QoI.append([]) # append a list in Y_l for every level
            time_ML.append([])           
    for level in range (0,len(number_samples)):
        for instance in range (0,number_samples[level]):
            sample = GenerateBetaSample(2.0,6.0) # generate a random variable with beta pdf, alpha = 2.0 and beta = 6.0
            run_results = []
            start_time_ML = time.time()
            if level == 0: # evaluating QoI in the coarsest grid
                run_results.append(execution_task(parameter_file_name[level], sample)) # append to run_results QoI for the coarsest grid
                time_MLi = time.time() - start_time_ML
                # difference_QoI[level].append(run_results[-1]) # with list[-1] we read the last element of the list
                difference_QoI[level] = np.append(difference_QoI[level],run_results[-1])
                # time_ML[level].append(time_MLi)
                time_ML[level] = np.append(time_ML[level],time_MLi)
                # print("LEVEL",level,"run_results",run_results,"SAMPLE",sample)
                
            else:
                for cycle_level in range (0,level+1):
                    run_results.append(execution_task(parameter_file_name[cycle_level], sample))
                    # print("LEVEL",level,"CYCLE LEVEL",cycle_level,"run_results",run_results,"SAMPLE",sample)
                  
                time_MLi = time.time() - start_time_ML
                # difference_QoI[level].append(run_results[-1] - run_results[-2])
                difference_QoI[level] = np.append(difference_QoI[level],run_results[-1] - run_results[-2])
                # time_ML[level].append(time_MLi)
                time_ML[level] = np.append(time_ML[level],time_MLi)
    
    # to evaluate the cost {C_l} we should comoute time_MC and time_ML, where time_MC is the list containing
    # the time of every MC simulation, while tume_ML is the list containing the time of the ML simulation,
    # i.e. the sum of the MC times
    
    # compute {abs(E^(MC)[Y_l])} = 1/N * sum_{i=1}^{N} Y_l(sample(i))
    # compute {V^(MC)[Y_l]}    
    mean_difference_QoI = []
    if len(mean_difference_QoI) < (L_screening +1):
        for i in range (0,(L_screening+1)-len(mean_difference_QoI)):
            mean_difference_QoI.append([]) # append a list in E^(MC)[Y_l] for every level
    variance_difference_QoI = []
    if len(variance_difference_QoI) < (L_screening +1):
        for i in range (0,(L_screening+1)-len(variance_difference_QoI)):
            variance_difference_QoI.append([]) # append a list in Var^(MC)[Y_l] for every level
    second_moment_difference_QoI = []
    if len(second_moment_difference_QoI) < (L_screening +1):
        for i in range (0,(L_screening+1)-len(second_moment_difference_QoI)):
            second_moment_difference_QoI.append([]) # append a list in Var^(MC)[Y_l] for every level
    
    for level in range (0,L_screening+1):    
        for i in range(0,number_samples[level]):
            nsam = i+1
            mean_difference_QoI[level],second_moment_difference_QoI[level] = update_onepass_M(difference_QoI[level][i],mean_difference_QoI[level],second_moment_difference_QoI[level],nsam)
    # now from second moment compute sample variance
    for level in range(0,L_screening+1):
        variance_difference_QoI[level] = compute_sample_variance_from_M2(second_moment_difference_QoI[level],number_samples[level])
    # print("list Y_l",difference_QoI)
    print("mean Y_l",mean_difference_QoI)
    print("sample variance Y_l",variance_difference_QoI)


    # compute {abs(E^(MC)[time_ML_l])} = 1/N * sum_{i=1}^{N} time_ML_l(sample(i))
    # compute {V^(MC)[time_ML__l]}    
    mean_time_ML = []
    if len(mean_time_ML) < (L_screening +1):
        for i in range (0,(L_screening+1)-len(mean_time_ML)):
            mean_time_ML.append([]) # append a list in E^(MC)[Y_l] for every level
    variance_time_ML = []
    if len(variance_time_ML) < (L_screening +1):
        for i in range (0,(L_screening+1)-len(variance_time_ML)):
            variance_time_ML.append([]) # append a list in Var^(MC)[Y_l] for every level
    second_moment_time_ML = []
    if len(second_moment_time_ML) < (L_screening +1):
        for i in range (0,(L_screening+1)-len(second_moment_time_ML)):
            second_moment_time_ML.append([])

    for level in range (0,L_screening+1):    
        for i in range(0,number_samples[level]):
            nsam = i+1
            mean_time_ML[level],second_moment_time_ML[level] = update_onepass_M(time_ML[level][i],mean_time_ML[level],second_moment_time_ML[level],nsam)
    # now from second moment compute sample variance
    for level in range(0,L_screening+1):
        variance_time_ML[level] = compute_sample_variance_from_M2(second_moment_time_ML[level],number_samples[level])
    # print("list time ML",time_ML)
    print("mean time ML",mean_time_ML)
    print("sample variance time ML",variance_time_ML)

    # compute nDoF: number degrees of freedom for each mesh
    nDoF = []
    for level in range (0,L_max + 1):
        nDoF.append(Nf_law(level))
    
    # compute parameters by least square fit to estimate Bayesian VAR
    # for now just copy the values from "simulation_IO/reports/P1"
    # ratesLS  = [2.634451365003769, 0.771582753017592, 25.05611620318177, 1.6425568004190512, 0.000604705275900292, 0.2872856532560337]
    ratesLS = compute_ratesLS(mean_difference_QoI,variance_difference_QoI,mean_time_ML,nDoF[0:L_screening+1])
    print("rates LS",ratesLS)

    # compute Bayesian VAR V^c[Y_l]
    BayesianVariance = EstimateBayesianVariance(mean_difference_QoI,variance_difference_QoI,parameters_ML_simulation,ratesLS,nDoF,number_samples,L_screening)
    print("Bayesian Variance estimated = ", BayesianVariance)
    
    # compute i_E, number of iterations
    iE_cmlmc = np.floor((-np.log(tolF)+np.log(r2)+np.log(tol0))/(np.log(r1)))
    print("number of iterations = ",iE_cmlmc)

    convergence = False
    iter = 1
    L_old = L_screening

    while convergence is not True:

        # Compute Tolerance for the iteration i
        # eventually, we may still run the algorithm for a few more iterations wrt iE_cmlmc
        tol_i = compute_tollerance_i(parameters_ML_simulation,iE_cmlmc,iter)
        
        # Compute Optimal Number of Levels L_i
        print("Bayesian variance before computing optimal number of levels",BayesianVariance)
        L_opt, BayesianVariance, L_old = compute_levels(tol_i,number_samples,ratesLS,nDoF,BayesianVariance,
                                                        mean_difference_QoI,variance_difference_QoI,parameters_ML_simulation,L_max,L_old)
        print("Optimal number of levels = ",L_opt,"Previous number of levels = ",L_old)
        print("Bayesian variance after new optimal number of levels",BayesianVariance)
        
        ####################################################################
        # observation: levels start from level 0                           #
        #              length arrays starts from 1                         #
        # then we have a difference of 1 between length arrays and levels  #
        # current_level = len(number_samples) - 1                          #
        # or                                                               #
        # current_level = len(difference_value) - 1                        #
        ####################################################################

        # compute new theta splitting,
        # since we updated the number of levels we have a new M_l
        # theta_i is a scalar
        theta_i = theta_model(ratesLS,tol_i,nDoF[L_opt])
        if not((theta_i > 0.0) or (theta_i < 1.0)):
            raise Exception ("The splitting parameter theta_i assumed a value outside the range (0,1)")

        # compute number of samples according to bayesian variance and theta splitting parameters
        number_samples, difference_number_samples, previous_number_samples = compute_number_samples(L_opt,BayesianVariance,ratesLS,theta_i,tol_i,nDoF,number_samples,parameters_ML_simulation)        
        # difference_number_samples = [2,2,2,2]
        # number_samples = [4,4,4,2]
        
        

        # run hierarchy using optimal levels and optimal number of samples
        # I use the "old" difference_QoI, and append the new values for the added samples,
        # or append at the end for the new level
        if (L_opt+1) > len(difference_QoI):
            for i in range (0,(L_opt+1)-len(difference_QoI)):
                difference_QoI.append([]) # append a list in Y_l for the new level
        if (L_opt+1) > len(time_ML):
            for i in range (0,(L_opt+1)-len(time_ML)):
                time_ML.append([]) # append a list in time_ML for the new level
        for level in range (0,L_opt+1):
            for instance in range (0,difference_number_samples[level]):
                sample = GenerateBetaSample(2.0,6.0)
                run_results = []
                start_time_ML = time.time()
                if level == 0: # evaluating QoI in the coarsest grid
                    run_results.append(execution_task(parameter_file_name[level], sample)) # append to run_results QoI for the coarsest grid
                    time_MLi = time.time() - start_time_ML
                    # difference_QoI[level].append(run_results[-1]) # with list[-1] we read the last element of the list
                    # time_ML[level].append(time_MLi)
                    difference_QoI[level] = np.append(difference_QoI[level],run_results[-1])
                    time_ML[level] = np.append(time_ML[level],time_MLi)
                else:
                    for cycle_level in range (0,level+1):
                        run_results.append(execution_task(parameter_file_name[cycle_level], sample))
                    time_MLi = time.time() - start_time_ML
                    # difference_QoI[level].append(run_results[-1] - run_results[-2])
                    # time_ML[level].append(time_MLi)
                    difference_QoI[level] = np.append(difference_QoI[level],run_results[-1] - run_results[-2])
                    time_ML[level] = np.append(time_ML[level],time_MLi)

        # print("iteration",iter,"Y_l",difference_QoI)
        # print("iteration",iter,"time ML",time_ML)

        # to evaluate the cost {C_l} we should compute time_MC and time_ML, where time_MC is the list containing
        # the time of every MC simulation, while tume_ML is the list containing the time of the ML simulations,
    
        # now compute mean, second moment, sample variance for Y_l
        mean_difference_QoI = mean_difference_QoI[0:L_old+1]
        variance_difference_QoI = variance_difference_QoI[0:L_old+1]
        second_moment_difference_QoI = second_moment_difference_QoI[0:L_old+1]
        if len(mean_difference_QoI) < (L_opt+1):
            for i in range (0,(L_opt+1)-len(mean_difference_QoI)):
                mean_difference_QoI.append([]) # append a list in E^(MC)[Y_l] for every level
        if len(variance_difference_QoI) < (L_opt+1):
            for i in range (0,(L_opt+1)-len(variance_difference_QoI)):
                variance_difference_QoI.append([]) # append a list in Var^(MC)[Y_l] for every level
        if len(second_moment_difference_QoI) < (L_opt+1):
            for i in range (0,(L_opt+1)-len(second_moment_difference_QoI)):
                second_moment_difference_QoI.append([])

        print(previous_number_samples,difference_number_samples,number_samples)
        print("old mean Y_l",mean_difference_QoI)
        print("old second moment Y_l",second_moment_difference_QoI)
        print("old sample variance MC Y_l",variance_difference_QoI)

        for level in range (0,L_opt+1):
            for i in range(0,difference_number_samples[level]):
                nsam = previous_number_samples[level] + (i+1)
                mean_difference_QoI[level],second_moment_difference_QoI[level] = update_onepass_M(
                    difference_QoI[level][previous_number_samples[level]+i],mean_difference_QoI[level],second_moment_difference_QoI[level],nsam)
        # now from second moment compute sample variance
        for level in range(0,L_opt+1):
            variance_difference_QoI[level] = compute_sample_variance_from_M2(second_moment_difference_QoI[level],number_samples[level])
        
        print("new mean Y_l",mean_difference_QoI)
        print("new second moment Y_l",second_moment_difference_QoI)
        print("new sample variance Y_l",variance_difference_QoI)

        # now compute mean, second moment, sample variance for time ML
        mean_time_ML = mean_time_ML[0:L_old+1]
        variance_time_ML = variance_time_ML[0:L_old+1]
        second_moment_time_ML = second_moment_time_ML[0:L_old+1]
        if len(mean_time_ML) < (L_opt+1):
            for i in range (0,(L_opt+1)-len(mean_time_ML)):
                mean_time_ML.append([]) # append a list in E^(MC)[time_ML] for every level
        if len(variance_time_ML) < (L_opt+1):
            for i in range (0,(L_opt+1)-len(variance_time_ML)):
                variance_time_ML.append([]) # append a list in Var^(MC)[time_ML] for every level
        if len(second_moment_time_ML) < (L_opt+1):
            for i in range (0,(L_opt+1)-len(second_moment_time_ML)):
                second_moment_time_ML.append([])
        print("old mean time ML",mean_time_ML)
        print("old second moment time ML",second_moment_time_ML)
        print("old sample variance MC time ML",variance_time_ML)

        for level in range (0,L_opt+1):
            for i in range(0,difference_number_samples[level]):
                nsam = previous_number_samples[level] + (i+1)
                mean_time_ML[level],second_moment_time_ML[level] = update_onepass_M(
                    time_ML[level][previous_number_samples[level]+i],mean_time_ML[level],second_moment_time_ML[level],nsam)
        # now from second moment compute sample variance
        for level in range(0,L_opt+1):
            variance_time_ML[level] = compute_sample_variance_from_M2(second_moment_time_ML[level],number_samples[level])

        print("new mean time ML",mean_time_ML)
        print("new second moment time ML",second_moment_time_ML)
        print("new sample variance time ML",variance_time_ML)

        # compute E^MLMC [QoI]
        mean_mlmc_QoI = compute_mean_mlmc_QoI(mean_difference_QoI)
        print("iter = ",iter,"mean MLMC QoI = ",mean_mlmc_QoI)

        # estimation problem parameters for Bayesian updates
        
        # compute parameters by least square fit to estimate Bayesian VAR
        # for now just copy the values from "simulation_IO/reports/P1"
        # ratesLS  = [3.741711767348006, 0.9043135691528007, 51.888730513771954, 1.8898644660250465, 1.569803705252941e-05, 0.9664856168144955]
        ratesLS = compute_ratesLS(mean_difference_QoI,variance_difference_QoI,mean_time_ML,nDoF[0:L_opt+1])
        print("rates LS",ratesLS)

        # compute Bayesian VAR V^c[Y_l]
        # I compute from zero, since I have new ratesLS
        # also Nobile computes each time from zero the Bayesian variance in "var_estim"
        BayesianVariance = EstimateBayesianVariance(mean_difference_QoI,variance_difference_QoI,parameters_ML_simulation,ratesLS,nDoF,number_samples,L_opt)
        print("iter = ",iter,"Bayesian Variance estimated = ", BayesianVariance)

        # compute errors
        # bias contribution B ~= abs(E^MC[Q_{L}-Q_{L-1}])
        bias_error = np.abs(mean_difference_QoI[L_opt])
        # compute/approximate variance of the MLMC estimator Var^MLMC[E^MLMC[Q_M]] (34) of [PNL16]
        var_bayes = np.zeros(np.size(number_samples))
        calpha = ratesLS[0]
        for i in range(0,L_opt+1):
            var_bayes[i] = BayesianVariance[i]/number_samples[i]
        TErr = bias_error + parameters_ML_simulation[6]*np.sqrt(np.sum(var_bayes))
        print("iter",iter,"total error TErr",TErr)

        L_old = L_opt

        if iter >= iE_cmlmc:
            if (TErr < tol_i):
                convergence = True
        else:
            iter = iter + 1

    print("iter = ",iter,"total error = ",TErr,"mean MLMC QoI = ",mean_mlmc_QoI)    
    
    print("")
    relative_error = compare_mean(mean_mlmc_QoI,ExactExpectedValueQoI)
    mean_mlmc_QoI = compss_wait_on(mean_mlmc_QoI)
    ExactExpectedValueQoI = compss_wait_on(ExactExpectedValueQoI)
    relative_error = compss_wait_on(relative_error)
    print("stochastic mean = ",mean_mlmc_QoI,"exact mean = ",ExactExpectedValueQoI)
    print("relative error: ",relative_error)
    print("")


    ### OBSERVATION ###
    # between different tasks you don't need compss_wait_on, it's pycompss who handles everything automatically
    # if the output of a task is given directly to the input of an other, pycompss handles everything
