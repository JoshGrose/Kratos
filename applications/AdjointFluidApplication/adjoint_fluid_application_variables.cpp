#include "adjoint_fluid_application_variables.h"

namespace Kratos
{

    KRATOS_CREATE_VARIABLE(double, NUMERICAL_DIFFUSION )
    KRATOS_CREATE_VARIABLE( Matrix, VMS_STEADY_TERM_PRIMAL_GRADIENT_MATRIX)

    // KRATOS_REGISTER_IN_PYTHON_VARIABLE(m, NUMERICAL_DIFFUSION )
// Create variables
// Moved to Kratos Core for trilinos_application
//KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( ADJOINT_FLUID_VECTOR_1 )
//KRATOS_CREATE_VARIABLE(double, ADJOINT_FLUID_SCALAR_1 )
//KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( PRIMAL_VELOCITY )
//KRATOS_CREATE_VARIABLE(double, PRIMAL_PRESSURE )
//KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( SHAPE_SENSITIVITY )
//KRATOS_CREATE_VARIABLE(double, NORMAL_SENSITIVITY )
}
