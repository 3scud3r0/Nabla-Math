import math
import unittest

from nablamath.autodiff import Var
from nablamath.physics.fluids import solve_incompressible_periodic


class IncompressibleNavierStokesTests(unittest.TestCase):
    def test_uniform_velocity_is_exact_fixed_point(self):
        u=[[2.0]*8 for _ in range(6)]
        v=[[-0.5]*8 for _ in range(6)]
        result=solve_incompressible_periodic(
            u,v,2.0,1.5,0.01,0.02,steps=4,pressure_iterations=12
        )
        for row in result.u_m_s:
            for value in row:
                self.assertAlmostEqual(float(value),2.0,places=13)
        for row in result.v_m_s:
            for value in row:
                self.assertAlmostEqual(float(value),-0.5,places=13)
        self.assertLess(result.divergence_l2(),1e-13)

    def test_projection_reduces_divergence(self):
        nx=ny=12
        u=[[math.sin(2*math.pi*i/nx) for i in range(nx)] for _ in range(ny)]
        v=[[0.5*math.sin(2*math.pi*j/ny) for _ in range(nx)] for j in range(ny)]
        dx=dy=1.0/nx
        def divergence_l2(uu,vv):
            total=0.0
            for j in range(ny):
                jm,jp=(j-1)%ny,(j+1)%ny
                for i in range(nx):
                    im,ip=(i-1)%nx,(i+1)%nx
                    d=(uu[j][ip]-uu[j][im])/(2*dx)+(vv[jp][i]-vv[jm][i])/(2*dy)
                    total+=d*d
            return math.sqrt(total/(nx*ny))
        before=divergence_l2(u,v)
        result=solve_incompressible_periodic(
            u,v,1.0,1.0,0.002,0.01,steps=1,pressure_iterations=120
        )
        self.assertLess(result.divergence_l2(),0.35*before)

    def test_viscosity_path_is_differentiable(self):
        nx=ny=6
        u=[[0.15*math.sin(2*math.pi*j/ny) for _ in range(nx)] for j in range(ny)]
        v=[[0.15*math.sin(2*math.pi*i/nx) for i in range(nx)] for _ in range(ny)]
        viscosity=Var(0.03)
        result=solve_incompressible_periodic(
            u,v,1.0,1.0,0.002,viscosity,steps=1,pressure_iterations=16
        )
        energy=result.kinetic_energy()
        self.assertIsInstance(energy,Var)
        energy.backward()
        self.assertTrue(math.isfinite(viscosity.grad))
        self.assertLess(viscosity.grad,0.0)

    def test_stability_guard_rejects_excessive_step(self):
        u=[[10.0]*4 for _ in range(4)]
        v=[[0.0]*4 for _ in range(4)]
        with self.assertRaises(ValueError):
            solve_incompressible_periodic(
                u,v,1.0,1.0,1.0,0.1,steps=1,pressure_iterations=4
            )


if __name__=="__main__":
    unittest.main()
