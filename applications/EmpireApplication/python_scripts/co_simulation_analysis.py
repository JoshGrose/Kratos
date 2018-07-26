from __future__ import print_function, absolute_import, division  # makes KratosMultiphysics backward compatible with python 2.6 and 2.7

import co_simulation_tools as cs_tools
from co_simulation_tools import csprint, bold

class CoSimulationAnalysis(object):
    """The base class for the CoSimulation-AnalysisStage
    It mimicks the AnalysisStage of Kratos but does NOT derive from it
    The reason is that it also needs to work without Kratos
    """
    def __init__(self, cosim_settings):
        if (type(cosim_settings) != dict):
            raise Exception("Input is expected to be provided as a python dictionary")

        self.cosim_settings = cosim_settings
        if "print_colors" in self.cosim_settings["problem_data"]:
            cs_tools.PRINT_COLORS = self.cosim_settings["problem_data"]["print_colors"]

        self.echo_level = 0
        if "echo_level" in self.cosim_settings["problem_data"]:
            self.echo_level = self.cosim_settings["problem_data"]["echo_level"]

    def Run(self):
        self.Initialize()
        self.RunSolutionLoop()
        self.Finalize()

    def RunSolutionLoop(self):
        print("")
        while self.time < self.end_time:
            print("")
            self.step += 1
            self.time = self._GetSolver().AdvanceInTime(self.time)
            self.InitializeSolutionStep()
            self._GetSolver().Predict()
            self._GetSolver().SolveSolutionStep()
            self.FinalizeSolutionStep()
            self.OutputSolutionStep()

    def Initialize(self):
        self._GetSolver().Initialize()
        self._GetSolver().Check()

        if self.echo_level > 0:
            self._GetSolver().PrintInfo()

        ## Stepping and time settings
        self.end_time = self.cosim_settings["problem_data"]["end_time"]
        self.time = self.cosim_settings["problem_data"]["start_time"]
        self.step = 0

    def Finalize(self):
        self._GetSolver().Finalize()

    def InitializeSolutionStep(self):
        csprint(0, bold("time={0:.12g}".format(self.time)+ " | step="+ str(self.step)))

        self._GetSolver().InitializeSolutionStep()

    def FinalizeSolutionStep(self):
        self._GetSolver().FinalizeSolutionStep()

    def OutputSolutionStep(self):
        self._GetSolver().OutputSolutionStep()

    def _GetSolver(self):
        if not hasattr(self, '_solver'):
            self._solver = self._CreateSolver()
        return self._solver

    def _CreateSolver(self):
        """Create the solver
        """
        import co_simulation_solvers.python_solvers_wrapper_co_simulation as solvers_wrapper
        return solvers_wrapper.CreateSolver(self.cosim_settings["solver_settings"], level=0)

## TODO add the if name==main stuff like in fluid and structure