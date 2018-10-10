//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ \.
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:		 BSD License
//					 Kratos default license: kratos/license.txt
//
//  Main authors:    Bodhinanda Chandra
//
//


#include "particle_mechanics_application_variables.h"

namespace Kratos
{

    // Element
    KRATOS_CREATE_VARIABLE( int, COUNTER )
    KRATOS_CREATE_VARIABLE( int, MP_NUMBER )
    KRATOS_CREATE_VARIABLE( int, MP_BOOL )
    KRATOS_CREATE_VARIABLE( int, MP_MATERIAL_ID )
    KRATOS_CREATE_VARIABLE( double, WEIGHT )
    KRATOS_CREATE_VARIABLE( double, MP_MASS )
    KRATOS_CREATE_VARIABLE( double, MP_DENSITY )
    KRATOS_CREATE_VARIABLE( double, MP_VOLUME )
    KRATOS_CREATE_VARIABLE( double, MP_KINETIC_ENERGY )
    KRATOS_CREATE_VARIABLE( double, MP_STRAIN_ENERGY )
    KRATOS_CREATE_VARIABLE( double, MP_TOTAL_ENERGY )
    KRATOS_CREATE_VARIABLE( double, MP_PRESSURE )
    KRATOS_CREATE_VARIABLE( double, MP_JACOBIAN )
    KRATOS_CREATE_VARIABLE( double, MP_DELTA_PLASTIC_STRAIN )
    KRATOS_CREATE_VARIABLE( double, MP_DELTA_PLASTIC_VOLUMETRIC_STRAIN )
    KRATOS_CREATE_VARIABLE( double, MP_DELTA_PLASTIC_DEVIATORIC_STRAIN )
    KRATOS_CREATE_VARIABLE( double, MP_EQUIVALENT_PLASTIC_STRAIN )
    KRATOS_CREATE_VARIABLE( double, MP_ACCUMULATED_PLASTIC_VOLUMETRIC_STRAIN )
    KRATOS_CREATE_VARIABLE( double, MP_ACCUMULATED_PLASTIC_DEVIATORIC_STRAIN )
    KRATOS_CREATE_VARIABLE( double, MP_CONSTITUTIVE_PRESSURE )
    KRATOS_CREATE_VARIABLE( double, NODAL_MPRESSURE )
    KRATOS_CREATE_VARIABLE( double, AUX_PRESSURE)
    KRATOS_CREATE_VARIABLE( double, AUX_MP_PRESSURE)

    // Constitutive Law
    KRATOS_CREATE_VARIABLE( ConstitutiveLaw::Pointer, CONSTITUTIVE_LAW_POINTER )
    // CL: Mohr Coulomb
    KRATOS_CREATE_VARIABLE( double, DILATANCY_COEFFICIENT )
    KRATOS_CREATE_VARIABLE( double, COHESION )
    KRATOS_CREATE_VARIABLE( double, INTERNAL_DILATANCY_ANGLE )
    // CL: Mohr Coulomb Strain Softening
    KRATOS_CREATE_VARIABLE( double, INTERNAL_FRICTION_ANGLE_RESIDUAL )
    KRATOS_CREATE_VARIABLE( double, COHESION_RESIDUAL )
    KRATOS_CREATE_VARIABLE( double, INTERNAL_DILATANCY_ANGLE_RESIDUAL )
    KRATOS_CREATE_VARIABLE( double, SHAPE_FUNCTION_BETA )
    // CL: Bounding Surface
    KRATOS_CREATE_VARIABLE( double, INITIAL_MEAN_STRESS )
    KRATOS_CREATE_VARIABLE( double, INITIAL_DEVIATORIC_STRESS )
    KRATOS_CREATE_VARIABLE( double, SPECIFIC_VOLUME_REFERENCE )
    KRATOS_CREATE_VARIABLE( bool  , IS_CSL_FIX )
    KRATOS_CREATE_VARIABLE( double, BOUNDING_SURFACE_CURVATURE )
    KRATOS_CREATE_VARIABLE( double, INITIAL_SCALING_HARDENING_PARAMETER )
    KRATOS_CREATE_VARIABLE( double, RELOAD_SCALING_HARDENING_PARAMETER  )
    KRATOS_CREATE_VARIABLE( double, MODEL_PARAMETER_R )
    KRATOS_CREATE_VARIABLE( double, MODEL_PARAMETER_A )
    KRATOS_CREATE_VARIABLE( double, MODEL_PARAMETER_K )
    
    // Nodal DOFs
    // Conditions
    //KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( IMPOSED_DISPLACEMENT )
    // Nodal load variables
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS(POINT_LOAD)
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS(LINE_LOAD)
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS(SURFACE_LOAD)

    // Condition load variables
    KRATOS_CREATE_VARIABLE(Vector, POINT_LOADS_VECTOR)
    KRATOS_CREATE_VARIABLE(Vector, LINE_LOADS_VECTOR)
    KRATOS_CREATE_VARIABLE(Vector, SURFACE_LOADS_VECTOR)
    
    // Others
    KRATOS_CREATE_VARIABLE( double, AUX_R)
    KRATOS_CREATE_VARIABLE( double, AUX_T)
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_R_VEL )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_T_VEL )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_R_ACC )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_T_ACC )
    KRATOS_CREATE_VARIABLE( double, NODAL_LUMPED_MASS)
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_VELOCITY )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_ACCELERATION )
    
    // MP element variable
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( GAUSS_COORD )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( MP_DISPLACEMENT )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( MP_VELOCITY )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( MP_ACCELERATION )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_MP_VELOCITY )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( AUX_MP_ACCELERATION )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( MP_VOLUME_ACCELERATION )
    KRATOS_CREATE_VARIABLE( Vector, MP_CAUCHY_STRESS_VECTOR )
    KRATOS_CREATE_VARIABLE( Vector, MP_ALMANSI_STRAIN_VECTOR )
    KRATOS_CREATE_VARIABLE( Vector, PREVIOUS_MP_CAUCHY_STRESS_VECTOR )
    KRATOS_CREATE_VARIABLE( Vector, PREVIOUS_MP_ALMANSI_STRAIN_VECTOR )
    KRATOS_CREATE_VARIABLE( Matrix, MP_CONSTITUTIVE_MATRIX )
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( DISPLACEMENT_AUX)
    
    // Grid node variable
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( NODAL_MOMENTUM)
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( NODAL_INERTIA)
    KRATOS_CREATE_3D_VARIABLE_WITH_COMPONENTS( NODAL_INTERNAL_FORCE )

}