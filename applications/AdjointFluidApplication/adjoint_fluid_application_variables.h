//  KratosAdjointFluidApplication
//
//  License:		 BSD License
//					 license: AdjointFluidApplication/license.txt
//
//  Main authors:    Michael Andre, https://github.com/msandre
//

#if !defined(KRATOS_ADJOINT_FLUID_APPLICATION_VARIABLES_H_INCLUDED)
#define  KRATOS_ADJOINT_FLUID_APPLICATION_VARIABLES_H_INCLUDED

// Project includes
#include "includes/define.h"
#include "includes/kratos_application.h"
#include "includes/variables.h"
#include "includes/dem_variables.h"

namespace Kratos
{

    KRATOS_DEFINE_VARIABLE(double, NUMERICAL_DIFFUSION )
    KRATOS_DEFINE_VARIABLE( Matrix, VMS_STEADY_TERM_PRIMAL_GRADIENT_MATRIX)

// Define variables
// Moved to Kratos Core for trilinos_application
//KRATOS_DEFINE_3D_VARIABLE_WITH_COMPONENTS( ADJOINT_FLUID_VECTOR_1 )
//KRATOS_DEFINE_VARIABLE(double, ADJOINT_FLUID_SCALAR_1 )
//KRATOS_DEFINE_3D_VARIABLE_WITH_COMPONENTS( PRIMAL_VELOCITY )
//KRATOS_DEFINE_VARIABLE(double, PRIMAL_PRESSURE )
//KRATOS_DEFINE_3D_VARIABLE_WITH_COMPONENTS( SHAPE_SENSITIVITY )
//KRATOS_DEFINE_VARIABLE(double, NORMAL_SENSITIVITY )
}

#endif	/* KRATOS_ADJOINT_FLUID_APPLICATION_VARIABLES_H_INCLUDED */
