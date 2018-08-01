//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:         BSD License
//                   Kratos default license: kratos/license.txt
//
//  Main authors:    Thomas Oberbichler
//

#if !defined(KRATOS_NODE_CURVE_GEOMETRY_3D_H_INCLUDED)
#define KRATOS_NODE_CURVE_GEOMETRY_3D_H_INCLUDED

// System includes

// External includes
#include <ANurbs/Core>

// Project includes
#include "includes/define.h"
#include "includes/Node.h"
#include "includes/variables.h"

namespace Kratos {

/// Spatial NURBS curve geometry with Kratos Nodes as control points.
/** Unlike the ANurbs::CurveGeometry, this class does not use static Points as
 *  control points but Finite Element Nodes. That means that the Geometry
 *  changes whenever the Nodes are moving.
 */
class NodeCurveGeometry3D
    : public ANurbs::CurveGeometryBase<double, Kratos::array_1d<double, 3>>
{
protected:
    using NodePointer = typename Node<3>::Pointer;

public:
    using CurveGeometryBaseType = ANurbs::CurveGeometryBase<double,
        Kratos::array_1d<double, 3>>;
    using typename CurveGeometryBaseType::KnotsType;
    using typename CurveGeometryBaseType::ScalarType;
    using typename CurveGeometryBaseType::VectorType;
 
protected:
    std::vector<NodePointer> mNodes;

public:
    /** Creates a new NodeCurveGeometry3D.
     *
     *  \param Degree Degree of the curve
     *  \param NumberOfNodes Number of nodes
     */
    NodeCurveGeometry3D(
        const int Degree,
        const int NumberOfNodes)
        : CurveGeometryBaseType(Degree, NumberOfNodes)
        , mNodes(NumberOfNodes)
    {
    }

    /** Gets the Kratos node at a given index.
     * 
     * \param Index Index of the node
     * 
     * @return Kratos node at the given index.
     */
    NodePointer
    Node(
        const int Index
    ) const
    {
        KRATOS_DEBUG_ERROR_IF(Index < 0 || NbPoles() <= Index) <<
            "Index out of range" << std::endl;

        return mNodes[Index];
    }

    /** Sets the Kratos node at a given index.
     * 
     * \param Index Index of the node
     */
    void
    SetNode(
        const int Index,
        NodePointer Value
    )
    {
        KRATOS_DEBUG_ERROR_IF(Index < 0 || NbPoles() <= Index) <<
            "Index out of range" << std::endl;

        mNodes[Index] = Value;
    }

    /** Gets the location of the Kratos node at a given index.
     * 
     * \param Index Index of the node
     * 
     * @return Location of the Kratos node at the given index.
     */
    VectorType
    Pole(
        const int Index) const override
    {
        const auto& node = *Node(Index);
 
        VectorType pole;
        pole[0] = node[0];
        pole[1] = node[1];
        pole[2] = node[2];
 
        return pole;
    }

    /** Sets the location of the Kratos node at a given index.
     * 
     * \param Index Index of the node
     * \param Value New location of the Kratos node
     */
    void
    SetPole(
        const int Index,
        const VectorType& Value) override
    {
        auto& node = *Node(Index);
 
        node[0] = Value[0];
        node[1] = Value[1];
        node[2] = Value[2];
    }

    /** Gets a value indicating whether or not the NURBS curve is rational.
     * 
     * @return True whether the curve is rational, otherwise false.
     */
    bool
    IsRational() const override
    {
        return true;
    }

    /** Gets the weight of the Kratos node at a given index.
     * 
     * \param Index Index of the node
     * 
     * @return Weight of the Kratos node at the given index.
     */
    ScalarType
    Weight(
        const int Index) const override
    {
        auto& node = *Node(Index);
 
        return node.GetValue(Kratos::NURBS_CONTROLPOINT_WEIGHT);
    }

    /** Sets the weight of the Kratos node at a given index.
     * 
     * \param Index Index of the node
     * \param Value New weight of the Kratos node
     */
    void
    SetWeight(
        const int Index,
        const ScalarType Value) override
    {
        auto& node = *Node(Index);

        node.SetValue(Kratos::NURBS_CONTROLPOINT_WEIGHT, Value);
    }

    /** Gets the value of a nodal Kratos variable on a point at the curve.
     * 
     * \param Variable Kratos variable
     * \param T Curve parameter
     * 
     * @return The value of the variable at the given curve point.
     */
    template <typename TDataType, typename TVariableType = Variable<TDataType>>
    TDataType
    ValueAt(
        const TVariableType& Variable,
        const double T) const
    {
        return EvaluateAt<TDataType>([&](int i) -> TDataType {
            return Node(i)->GetValue(Variable);
        }, T);
    }

    /** Gets the derivatives of a nodal Kratos variable on a point at the curve.
     * 
     * \param Variable Kratos variable
     * \param T Curve parameter
     * \param Order Order of the highest derivative to compute
     * 
     * @return The value and the derivatives of the variable at the given
     * curve point.
     */
    template <typename TDataType, typename TVariableType = Variable<TDataType>>
    std::vector<TDataType>
    ValueAt(
        const TVariableType& Variable,
        const double T,
        const int Order) const
    {
        return EvaluateAt<TDataType>([&](int i) -> TDataType {
            return Node(i)->GetValue(Variable);
        }, T, Order);
    }
};
 
} // namespace Kratos

#endif // !defined(KRATOS_NODE_CURVE_GEOMETRY_3D_H_INCLUDED)