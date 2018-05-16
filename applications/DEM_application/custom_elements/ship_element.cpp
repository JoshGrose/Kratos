// Last Modified by: Salva, latorre@cimne.upc.edu

// System includes
#include <string>
#include <iostream>
#include <stdlib.h>

// Project includes
#include "ship_element.h"
#include "custom_utilities/GeometryFunctions.h"
#include "DEM_application_variables.h"
#include "includes/variables.h"

namespace Kratos {

    ShipElement3D::ShipElement3D() : RigidBodyElement3D() {}

    ShipElement3D::ShipElement3D(IndexType NewId, GeometryType::Pointer pGeometry)
    : RigidBodyElement3D(NewId, pGeometry) {}

    ShipElement3D::ShipElement3D(IndexType NewId, GeometryType::Pointer pGeometry, PropertiesType::Pointer pProperties)
    : RigidBodyElement3D(NewId, pGeometry, pProperties) {}

    ShipElement3D::ShipElement3D(IndexType NewId, NodesArrayType const& ThisNodes)
    : RigidBodyElement3D(NewId, ThisNodes) {}

    Element::Pointer ShipElement3D::Create(IndexType NewId, NodesArrayType const& ThisNodes, PropertiesType::Pointer pProperties) const {
        return Element::Pointer(new ShipElement3D(NewId, GetGeometry().Create(ThisNodes), pProperties));
    }

    ShipElement3D::~ShipElement3D() {}

    void ShipElement3D::CustomInitialize(ModelPart& rigid_body_element_sub_model_part) {
        
        RigidBodyElement3D::CustomInitialize(rigid_body_element_sub_model_part);
        
        mEnginePower = rigid_body_element_sub_model_part[DEM_ENGINE_POWER];
        mMaxEngineForce = rigid_body_element_sub_model_part[DEM_MAX_ENGINE_FORCE];
        mThresholdVelocity = rigid_body_element_sub_model_part[DEM_THRESHOLD_VELOCITY];
        mEnginePerformance = rigid_body_element_sub_model_part[DEM_ENGINE_PERFORMANCE];
        
        mDragConstantVector = ZeroVector(3);
        mDragConstantVector[0] = rigid_body_element_sub_model_part[DEM_DRAG_CONSTANT_X];
        mDragConstantVector[1] = rigid_body_element_sub_model_part[DEM_DRAG_CONSTANT_Y];
        mDragConstantVector[2] = rigid_body_element_sub_model_part[DEM_DRAG_CONSTANT_Z];
    }
    
    void ShipElement3D::ComputeBuoyancyEffects() {

        KRATOS_TRY

        const double water_density = 1000;
        const double gravity = 9.81;
        const double water_level = 0.0;

        for (unsigned int i = 0; i != mListOfRigidFaces.size(); ++i) {
            double mean_pressure = 0.0;
            double rigid_face_area = 0.0;
            Point rigid_face_centroid;
            array_1d<double, 3> normal_to_rigid_face = ZeroVector(3);
            array_1d<double, 3> normal_rigid_face_force = ZeroVector(3);
            array_1d<double, 3> rigid_body_centroid_to_rigid_face_controid_vector = ZeroVector(3);
            array_1d<double, 3> buoyancy_moment = ZeroVector(3);
            unsigned int rigid_face_size = mListOfRigidFaces[i]->GetGeometry().size();

            for (unsigned int j = 0; j < rigid_face_size; j++) {
                double node_Z_coordinate = mListOfRigidFaces[i]->GetGeometry()[j].Coordinates()[2];
                mean_pressure += ((node_Z_coordinate >= water_level) ? 0.0 : -node_Z_coordinate * water_density * gravity);
            }

            rigid_face_centroid = mListOfRigidFaces[i]->GetGeometry().Center();
            if (rigid_face_size) mean_pressure /= rigid_face_size;
            else KRATOS_INFO("DEM") << "A rigid face with no nodes was found!";
            mListOfRigidFaces[i]->CalculateNormal(normal_to_rigid_face);
            rigid_face_area = mListOfRigidFaces[i]->GetGeometry().Area();
            normal_rigid_face_force[0] = mean_pressure * rigid_face_area * normal_to_rigid_face[0];
            normal_rigid_face_force[1] = mean_pressure * rigid_face_area * normal_to_rigid_face[1];
            normal_rigid_face_force[2] = mean_pressure * rigid_face_area * normal_to_rigid_face[2];

            for (unsigned int i = 0; i < rigid_face_size; i++) {
                rigid_body_centroid_to_rigid_face_controid_vector[0] = rigid_face_centroid.Coordinates()[0] - GetGeometry()[0].Coordinates()[0];
                rigid_body_centroid_to_rigid_face_controid_vector[1] = rigid_face_centroid.Coordinates()[1] - GetGeometry()[0].Coordinates()[1];
                rigid_body_centroid_to_rigid_face_controid_vector[2] = rigid_face_centroid.Coordinates()[2] - GetGeometry()[0].Coordinates()[2];
                if (GeometryFunctions::DotProduct(rigid_body_centroid_to_rigid_face_controid_vector, normal_to_rigid_face) > 0.0) {
                    DEM_MULTIPLY_BY_SCALAR_3(normal_rigid_face_force, -1.0)
                }
            }

            array_1d<double, 3>& total_forces = GetGeometry()[0].FastGetSolutionStepValue(TOTAL_FORCES);
            DEM_ADD_SECOND_TO_FIRST(total_forces, normal_rigid_face_force)
            array_1d<double, 3>& total_moments = GetGeometry()[0].FastGetSolutionStepValue(PARTICLE_MOMENT);
            GeometryFunctions::CrossProduct(rigid_body_centroid_to_rigid_face_controid_vector, normal_rigid_face_force, buoyancy_moment);
            DEM_ADD_SECOND_TO_FIRST(total_moments, buoyancy_moment)
        }

        KRATOS_CATCH("")
    }

    void ShipElement3D::ComputeEngineForce() {

        KRATOS_TRY
        
        array_1d<double, 3>& external_applied_force = GetGeometry()[0].FastGetSolutionStepValue(EXTERNAL_APPLIED_FORCE);
        const array_1d<double, 3> velocity = GetGeometry()[0].FastGetSolutionStepValue(VELOCITY);

        if ((GetGeometry()[0].FastGetSolutionStepValue(VELOCITY)[0]) < mThresholdVelocity) external_applied_force[0] = mEnginePerformance * mMaxEngineForce;
        else if (velocity[0]) external_applied_force[0] = mEnginePerformance * mEnginePower / velocity[0];
        
        noalias(GetGeometry()[0].FastGetSolutionStepValue(TOTAL_FORCES)) += external_applied_force;

        KRATOS_CATCH("")
    }

    void ShipElement3D::ComputeWaterDragForce() {

        KRATOS_TRY
        
        array_1d<double, 3>& external_applied_force  = GetGeometry()[0].FastGetSolutionStepValue(EXTERNAL_APPLIED_FORCE);
        const array_1d<double, 3> velocity = GetGeometry()[0].FastGetSolutionStepValue(VELOCITY);

        // Drag forces due to water. We are assuming the ship is moving in the X direction
        // Quadratic laws were chosen. They may be linear
        external_applied_force[0] += ((velocity[0] >= 0.0) ? -mDragConstantVector[0] * velocity[0] * velocity[0] : mDragConstantVector[0] * velocity[0] * velocity[0]);
        external_applied_force[1] += ((velocity[1] >= 0.0) ? -mDragConstantVector[1] * velocity[1] * velocity[1] : mDragConstantVector[1] * velocity[1] * velocity[1]);
        external_applied_force[2] += ((velocity[2] >= 0.0) ? -mDragConstantVector[2] * velocity[2] * velocity[2] : mDragConstantVector[2] * velocity[2] * velocity[2]);
        
        noalias(GetGeometry()[0].FastGetSolutionStepValue(TOTAL_FORCES)) += external_applied_force;

        KRATOS_CATCH("")
    }

    void ShipElement3D::ComputeExternalForces(const array_1d<double,3>& gravity) {

        KRATOS_TRY
        // Gravity
        noalias(GetGeometry()[0].FastGetSolutionStepValue(TOTAL_FORCES)) += RigidBodyElement3D::GetMass() * gravity;
        
        ComputeBuoyancyEffects();
        ComputeEngineForce();
        ComputeWaterDragForce();

        KRATOS_CATCH("")
    }

}  // namespace Kratos
