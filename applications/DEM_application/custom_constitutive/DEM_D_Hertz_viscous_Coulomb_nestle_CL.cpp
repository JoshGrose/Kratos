
#include <iostream>
#include "DEM_D_Hertz_viscous_Coulomb_nestle_CL.h"
#include "custom_elements/spheric_particle.h"

namespace Kratos {

    DEMDiscontinuumConstitutiveLaw::Pointer DEM_D_Hertz_viscous_Coulomb_nestle::Clone() const {
        
        DEMDiscontinuumConstitutiveLaw::Pointer p_clone(new DEM_D_Hertz_viscous_Coulomb_nestle(*this));
        return p_clone;
    }

    void DEM_D_Hertz_viscous_Coulomb_nestle::SetConstitutiveLawInProperties(Properties::Pointer pProp, bool verbose) const {
        
        if (verbose) std::cout << "\nAssigning DEM_D_Hertz_viscous_Coulomb_nestle to Properties " << pProp->Id() << std::endl;
        pProp->SetValue(DEM_DISCONTINUUM_CONSTITUTIVE_LAW_POINTER, this->Clone());
    }
    
    void DEM_D_Hertz_viscous_Coulomb_nestle::CalculateViscoDampingForce(double LocalRelVel[3],
                                                                 double ViscoDampingLocalContactForce[3],
                                                                 SphericParticle* const element1,
                                                                 SphericParticle* const element2) {
        
        const double my_mass    = element1->GetMass();
        const double other_mass = element2->GetMass();
                
        const double equiv_mass = 1.0 / (1.0/my_mass + 1.0/other_mass);        
        
        const double my_gamma    = element1->GetProperties()[DAMPING_GAMMA];
        const double other_gamma = element2->GetProperties()[DAMPING_GAMMA];
        const double equiv_gamma = 0.5 * (my_gamma + other_gamma);

        const double equiv_visco_damp_coeff_normal     = 2.0 * equiv_gamma * sqrt(equiv_mass * mKn);
        const double equiv_visco_damp_coeff_tangential = equiv_visco_damp_coeff_normal / 0.55; 
    
        ViscoDampingLocalContactForce[0] = - equiv_visco_damp_coeff_tangential * LocalRelVel[0];
        ViscoDampingLocalContactForce[1] = - equiv_visco_damp_coeff_tangential * LocalRelVel[1];
        ViscoDampingLocalContactForce[2] = - equiv_visco_damp_coeff_normal     * LocalRelVel[2];
    }

    void DEM_D_Hertz_viscous_Coulomb_nestle::CalculateViscoDampingForceWithFEM(double LocalRelVel[3],
                                                                double ViscoDampingLocalContactForce[3],
                                                                SphericParticle* const element,
                                                                DEMWall* const wall) {
        
        const double my_mass    = element->GetMass();
        const double gamma = element->GetProperties()[DAMPING_GAMMA];
        const double normal_damping_coefficient     = 2.0 * gamma * sqrt(my_mass * mKn);
        const double tangential_damping_coefficient = normal_damping_coefficient / 0.55;
              
        ViscoDampingLocalContactForce[0] = - tangential_damping_coefficient * LocalRelVel[0];
        ViscoDampingLocalContactForce[1] = - tangential_damping_coefficient * LocalRelVel[1];
        ViscoDampingLocalContactForce[2] = - normal_damping_coefficient     * LocalRelVel[2];
    }
} //namespace Kratos
