import KratosMultiphysics
import KratosMultiphysics.FluidTransportApplication as KratosFluidTransport

def Factory(settings, Model):
    if(type(settings) != KratosMultiphysics.Parameters):
        raise Exception("expected input shall be a Parameters object, encapsulating a json string")
    return ApplyScalarConstraintFunctionProcess(Model, settings["Parameters"])

## All the python processes should be derived from "python_process"

class ApplyScalarConstraintFunctionProcess(KratosMultiphysics.Process):
    def __init__(self, Model, settings ):
        KratosMultiphysics.Process.__init__(self)

        model_part = Model[settings["model_part_name"].GetString()]
        variable_name = settings["variable_name"].GetString()

        self.components_process_list = []

        # TODO temperature slope

        # for node in model_part.Nodes:
        #     temperature = -5.0 / 8.0 * node.X + 8.0
        #     node.SetSolutionStepValue(KratosMultiphysics.TEMPERATURE,temperature)

        for node in model_part.Nodes:
            if((node.X >= 0.1 and node.X <= 0.2) or (node.X >= 0.3 and node.X <= 0.4)):
                node.SetSolutionStepValue(KratosMultiphysics.TEMPERATURE,1.0)

            else:
                node.SetSolutionStepValue(KratosMultiphysics.TEMPERATURE,0.0)


    # def ExecuteInitialize(self):

    #     for component in self.components_process_list:
    #         component.ExecuteInitialize()

    # def ExecuteInitializeSolutionStep(self):

    #     for component in self.components_process_list:
    #         component.ExecuteInitializeSolutionStep()