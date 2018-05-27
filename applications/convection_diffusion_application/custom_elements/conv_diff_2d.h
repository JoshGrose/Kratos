// KRATOS ___ ___  _  ___   __   ___ ___ ___ ___ 
//       / __/ _ \| \| \ \ / /__|   \_ _| __| __|
//      | (_| (_) | .` |\ V /___| |) | || _|| _| 
//       \___\___/|_|\_| \_/    |___/___|_| |_|  APPLICATION
//
//  License: BSD License
//   license: convection_diffusion_application/license.txt
//
//  Main authors:  Riccardo Rossi
//

#if !defined(KRATOS_TRIANGULAR_CONVDIFF_ELEM_H_INCLUDED )
#define  KRATOS_TRIANGULAR_CONVDIFF_ELEM_H_INCLUDED

// System includes

// External includes

// Project includes
#include "includes/define.h"
#include "includes/element.h"
#include "includes/ublas_interface.h"
#include "includes/variables.h"
#include "includes/serializer.h"

namespace Kratos
{

///@name Kratos Globals
///@{

///@}
///@name Type Definitions
///@{

///@}
///@name  Enum's
///@{

///@}
///@name  Functions
///@{

///@}
///@name Kratos Classes
///@{

/// A stabilized element for solving the convection diffusion equations in 2D.

/**
The problem can be written in matrix form as
  \f$ \rho C M \frac{\partial T}{\partial t} + \rho C S T  = - \kappa L T \f$


*/


class ConvDiff2D
    : public Element
{
public:
    ///@name Type Definitions
    ///@{

    /// Counted pointer of ConvDiff2D
    // typedef GeometryData::IntegrationMethod IntegrationMethod;
    KRATOS_CLASS_POINTER_DEFINITION(ConvDiff2D);

    ///@}
    ///@name Life Cycle
    ///@{

    /// Default constructor.
    ConvDiff2D(IndexType NewId, GeometryType::Pointer pGeometry);
    ConvDiff2D(IndexType NewId, GeometryType::Pointer pGeometry,  PropertiesType::Pointer pProperties);

    /// Destructor.
    virtual ~ConvDiff2D();


    ///@}
    ///@name Operators
    ///@{


    ///@}
    ///@name Operations
    ///@{
    //IntegrationMethod GetIntegrationMethod();
    Element::Pointer Create(IndexType NewId, NodesArrayType const& ThisNodes,  PropertiesType::Pointer pProperties) const override;

    ///Evaluates  \f$ L h s = \frac{\rho C}{\Delta t} (W, N) + (W, v. \nabla N) + \kappa (\nabla W, \nabla N)  \f$ and \f$R h s = \rho (W, Q) + \frac{\rho C}{\Delta t} (W, T^n) - L h s \ast T \f$



    void CalculateLocalSystem(MatrixType& rLeftHandSideMatrix, VectorType& rRightHandSideVector, ProcessInfo& rCurrentProcessInfo) override;

    void CalculateRightHandSide(VectorType& rRightHandSideVector, ProcessInfo& rCurrentProcessInfo) override;
    //virtual void CalculateLeftHandSide(MatrixType& rLeftHandSideMatrix, ProcessInfo& rCurrentProcessInfo);

    ///Provides the global indices for each one of this element's local rows. @see NoNewtonianASGS2D
    void EquationIdVector(EquationIdVectorType& rResult, ProcessInfo& rCurrentProcessInfo) override;

    ///Returns a list of the element's Dofs. @see NoNewtonianASGS2D
    void GetDofList(DofsVectorType& ElementalDofList,ProcessInfo& CurrentProcessInfo) override;
    /// Calculates the temperature convective projection
    void InitializeSolutionStep(ProcessInfo& CurrentProcessInfo) override;

   /* double ComputeSmagorinskyViscosity(const boost::numeric::ublas::bounded_matrix<double, 3, 2 > & DN_DX,const double& h,const double& C,const double nu);*/

    ///@}
    ///@name Access
    ///@{


    ///@}
    ///@name Inquiry
    ///@{


    ///@}
    ///@name Input and output
    ///@{

    /// Turn back information as a string.
//      virtual String Info() const;

    /// Print information about this object.
//      virtual void PrintInfo(std::ostream& rOStream) const;

    /// Print object's data.
//      virtual void PrintData(std::ostream& rOStream) const;


    ///@}
    ///@name Friends
    ///@{


    ///@}

protected:
    ///@name Protected static Member Variables
    ///@{


    ///@}
    ///@name Protected member Variables
    ///@{


    ///@}
    ///@name Protected Operators
    ///@{


    ///@}
    ///@name Protected Operations
    ///@{


    ///@}
    ///@name Protected  Access
    ///@{


    ///@}
    ///@name Protected Inquiry
    ///@{


    ///@}
    ///@name Protected LifeCycle
    ///@{


    ///@}

private:
    //IntegrationMethod mThisIntegrationMethod;
    //std::vector< Matrix > mInvJ0;
    //Vector mDetJ0;
    ///@name Static Member Variables
    ///@{

    ///@}
    ///@name Member Variables
    ///@{

    ///@}
    ///@name Serialization
    ///@{
    friend class Serializer;

    // A private default constructor necessary for serialization
    ConvDiff2D() : Element()
    {
    }

    void save(Serializer& rSerializer) const override
    {
        KRATOS_SERIALIZE_SAVE_BASE_CLASS(rSerializer, Element);
    }

    void load(Serializer& rSerializer) override
    {
        KRATOS_SERIALIZE_LOAD_BASE_CLASS(rSerializer, Element);
    }




    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{


    ///@}
    ///@name Private  Access
    ///@{


    ///@}
    ///@name Private Inquiry
    ///@{


    ///@}
    ///@name Un accessible methods
    ///@{

    /// Assignment operator.
    //ConvDiff2D& operator=(const ConvDiff2D& rOther);

    /// Copy constructor.
    //ConvDiff2D(const ConvDiff2D& rOther);


    ///@}

}; // Class ConvDiff2D

///@}

///@name Type Definitions
///@{


///@}
///@name Input and output
///@{


/// input stream function
/*  inline std::istream& operator >> (std::istream& rIStream,
				    ConvDiff2D& rThis);
*/
/// output stream function
/*  inline std::ostream& operator << (std::ostream& rOStream,
				    const ConvDiff2D& rThis)
    {
      rThis.PrintInfo(rOStream);
      rOStream << std::endl;
      rThis.PrintData(rOStream);

      return rOStream;
    }*/
///@}

}  // namespace Kratos.

#endif // KRATOS_TRIANGULAR_CONVDIFF_ELEM_H_INCLUDED  defined


