#include "adjoint_fluid_application.h"

namespace Kratos
{
KratosAdjointFluidApplication::KratosAdjointFluidApplication() :
    KratosApplication("AdjointFluidApplication"),
    mVMSAdjointElement2D(0,Element::GeometryType::Pointer(new Triangle2D3<Node<3> >(Element::GeometryType::PointsArrayType(3)))),
    mVMSAdjointElement3D(0,Element::GeometryType::Pointer(new Tetrahedra3D4<Node<3> >(Element::GeometryType::PointsArrayType(4))))
{}

void KratosAdjointFluidApplication::Register()
{
  // calling base class register to register Kratos components
  KratosApplication::Register();
  std::cout << "Initializing KratosAdjointFluidApplication... " << std::endl;

  // Register elements
  KRATOS_REGISTER_ELEMENT( "VMSAdjointElement2D", mVMSAdjointElement2D );
  KRATOS_REGISTER_ELEMENT( "VMSAdjointElement3D", mVMSAdjointElement3D );

  KRATOS_REGISTER_VARIABLE(NUMERICAL_DIFFUSION)
  KRATOS_REGISTER_VARIABLE(VMS_STEADY_TERM_PRIMAL_GRADIENT_MATRIX)
      
  // Register variables
  // Moved to Kratos Core for trilinos_application
  //KRATOS_REGISTER_3D_VARIABLE_WITH_COMPONENTS( ADJOINT_FLUID_VECTOR_1 );
  //KRATOS_REGISTER_VARIABLE( ADJOINT_FLUID_SCALAR_1 );
  //KRATOS_REGISTER_3D_VARIABLE_WITH_COMPONENTS( PRIMAL_VELOCITY );
  //KRATOS_REGISTER_VARIABLE( PRIMAL_PRESSURE );
  //KRATOS_REGISTER_3D_VARIABLE_WITH_COMPONENTS( SHAPE_SENSITIVITY );
  //KRATOS_REGISTER_VARIABLE( NORMAL_SENSITIVITY );
}

} // namespace Kratos
