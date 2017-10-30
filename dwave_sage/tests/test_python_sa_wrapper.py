import unittest
import numpy as np

import dwave_sage_sampler

class TestSA(unittest.TestCase):
    def _sample_fm_problem(self, num_variables=10, num_samples=100, 
                           num_sweeps=1000):
        h = [-1]*num_variables
        (coupler_starts, 
            coupler_ends, 
            coupler_weights) = zip(*((u,v,-1) for u in range(num_variables) 
                    for v in range(u, num_variables)))
        
        beta_schedule = np.linspace(0.01, 3, num=num_sweeps)
        seed = 1

        return (num_samples, h, coupler_starts, coupler_ends, coupler_weights,
                beta_schedule, seed)

    def _random_pm1_problem(self, num_variables=10, num_samples=100,
                        num_sweeps=1000):
        h = np.random.choice((-1, 1), num_variables)
        coupler_starts, coupler_ends = zip(*((u,v) for u in range(num_variables) for v in range(u, num_variables)))
        coupler_weights = np.random.choice((-1,1), len(coupler_starts))

        beta_schedule = np.linspace(0.01, 3, num=num_sweeps)
        seed = 1

        return (num_samples, h, coupler_starts, coupler_ends, coupler_weights,
                beta_schedule, seed)

    def test_submit_problem(self):
        num_variables, num_samples = 10, 100
        problem = self._sample_fm_problem(num_variables=num_variables,
                                          num_samples=num_samples)

        result = dwave_sage_sampler.simulated_annealing(*problem)

        self.assertIsInstance(result, dict, "Sampler should return a dict")

        for key in ("samples", "energies", "intermediate_states"):
            self.assertTrue(key in result,
                    "Key `{}` not found in dict sampler returned")

        samples, energies = result["samples"], result["energies"]

        # ensure samples are all valid samples
        self.assertTrue(type(samples) is np.ndarray)
        # ensure correct number of samples and samples are have the correct
        # length
        self.assertTrue(samples.shape == (num_samples, num_variables), 
                "Sampler returned wrong shape for samples")
        # make sure samples contain only +-1
        self.assertTrue(set(np.unique(samples)) == {-1, 1},
                "Sampler returned spins with values not equal to +-1") 

        # ensure energies is valid
        self.assertTrue(type(energies) is np.ndarray)
        # one energy per sample
        self.assertTrue(energies.shape == (num_samples,),
                "Sampler returned wrong number of energies") 


    def test_good_results(self):
        num_variables = 5
        problem = self._sample_fm_problem(num_variables=num_variables)
        
        result = dwave_sage_sampler.simulated_annealing(*problem)
        samples, energies = result["samples"], result["energies"]

        ground_state = [1]*num_variables
        ground_energy = -(num_variables+3)*num_variables/2

        # we should definitely have gotten to the ground state
        self.assertTrue(ground_state in samples,
                "Ground state not found in samples from easy problem")

        mean_energy = np.mean(energies)
        self.assertAlmostEqual(ground_energy, mean_energy, delta=2,
                msg="Sampler returned poor mean energy for easy problem")

    def test_seed(self):
        # no need to do a bunch of sweeps, in fact the less we do the more
        # sure we can be that the same seed is returning the same result
        problem = self._sample_fm_problem(num_variables=40, num_samples=1000,
                num_sweeps=10)

        # no need to do a bunch of sweeps, in fact the less we do the more
        # sure we can be that the same seed is returning the same result

        previous_samples = []
        for seed in (1, 40, 235, 152436, 3462354, 92352355):
            seeded_problem = problem[:-1] + (seed,)
            result0 = dwave_sage_sampler.simulated_annealing(*seeded_problem)
            result1 = dwave_sage_sampler.simulated_annealing(*seeded_problem)
            samples0 = result0["samples"]
            samples1 = result1["samples"]

            self.assertTrue(np.array_equal(samples0, samples1),
                    "Same seed returned different results")

            for previous_sample in previous_samples:
                self.assertFalse(np.array_equal(samples0, previous_sample),
                    "Different seed returned same results")

            previous_samples.append(samples0)

    def test_intermediate_states(self):
        problem = self._random_pm1_problem()

        result = dwave_sage_sampler.simulated_annealing(*problem,
                n_intermediate_states=10)

if __name__ == "__main__":
    unittest.main()
