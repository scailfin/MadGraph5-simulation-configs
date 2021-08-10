function append(t1, t2)
    for i = 1, #t2 do
        t1[#t1 + 1] = t2[i]
    end

    return t1
end

-- Order convention : e+ e- b bbar
-- Reco particles : input::particles/1
-- Gen particles, depends on what you do

-- Available parameters : https://github.com/MoMEMta/MoMEMta/blob/master/core/src/MoMEMta.cc#L141
-- If "relative accuracy" is reached stop launching points unless "min_eval" point have been launched,
-- if after "max_eval" points have been launched stop launching even if we do not have reahced accuracy.
-- "n_start" : Vegas works by iterations will launch n_start point by n_start point and refine the grid at each step
-- n_increase allow to launch more points at each iteration
-- NB : all the point that have been launched are used to compute the intergal
cuba = {
    seed = random,
    relative_accuracy = 0.01,
    verbosity = 3,
    max_eval = max_eval,
    n_start = n_start
}

-- NB: to be defined in the .cxx is matrix_element_prefix

--inputs as will be feed to the blocks and ME
local neg_lepton = declare_input("lepton1")
local pos_lepton = declare_input("lepton2")
local bjet1 = declare_input("bjet1")
local bjet2 = declare_input("bjet2")


USE_TF = true
USE_PERM = true -- carefull if you use TF binned in eta and the permutations, jet1 tf is applied to jet2

parameters = {
    energy = 13000.,
    Z_mass = 91.1876,
    Z_width = 2.49,
    lep1_me_index = 1,
    lep2_me_index = 2,
    matrix_element = 'pp_drell_yan_llbb_sm_P1_Sigma_sm_gg_epembbx',
    matrix_element_parameters = {
      card = 'MatrixElements/pp_drell_yan_llbb/Cards/param_card.dat'
    },
    export_graph_as = "drell-yan_example_computing_graph.dot"
}
load_modules('MatrixElements/pp_drell_yan_llbb/build/libme_pp_drell_yan_llbb.so')

if USE_PERM then
    add_reco_permutations(bjet1, bjet2)
end

if USE_TF then
    -- Fix gen energy of the two leptons according to their transfer function
    GaussianTransferFunctionOnEnergy.tf_neg_lepton = {
        ps_point = add_dimension(),
        reco_particle = neg_lepton.reco_p4,
        sigma = 0.10,
        sigma_range = 3.,
    }
    neg_lepton.set_gen_p4("tf_neg_lepton::output")

    GaussianTransferFunctionOnEnergy.tf_pos_lepton = {
        ps_point = add_dimension(),
        reco_particle = pos_lepton.reco_p4,
        sigma = 0.10,
        sigma_range = 3.,
    }
    pos_lepton.set_gen_p4("tf_pos_lepton::output")

    -- Compute the phase space density for observed particles not concerned by the change of variable:
    -- here lepton on which we evaluate the TF
    -- The TF jacobian just account for dp/dE to go from |p| to E, not the phase space volume, the
    -- other blocks give the whole product of jacobian and phase space volume to go from one param to another
    StandardPhaseSpace.phaseSpaceOut = {
        particles = {'tf_neg_lepton::output', 'tf_pos_lepton::output'}
    }
    -- Obtain the energy of the b's from momentum conservation (first two input are RECO b's, other inputs are
    -- used to fix PT to be balanced, all at gen level)
    BlockA.blocka = {
        p1 = bjet1.reco_p4,
        p2 = bjet2.reco_p4,
        branches = {'tf_neg_lepton::output', 'tf_pos_lepton::output'},
    }
    Looper.looper = {
        solutions = "blocka::solutions",
        path = Path("tfEval_bjet1", "tfEval_bjet2", "boost", "drellyan", "integrand") -- everything that will depend on the different solutions
    }
    bjet1.set_gen_p4("looper::particles/1")
    bjet2.set_gen_p4("looper::particles/2")

    GaussianTransferFunctionOnEnergyEvaluator.tfEval_bjet1 = {
        ps_point = add_dimension(),
        reco_particle = bjet1.reco_p4,
        sigma = 0.30,
        sigma_range = 3.,
    }
    GaussianTransferFunctionOnEnergyEvaluator.tfEval_bjet2 = {
        ps_point = add_dimension(),
        reco_particle = bjet2.reco_p4,
        sigma = 0.30,
        sigma_range = 3.,
    }

    genParticles = {
        pos_lepton.gen_p4,
        neg_lepton.gen_p4,
        bjet1.gen_p4,
        bjet2.gen_p4,
        }

else
    genParticles = {
        pos_lepton.reco_p4,
        neg_lepton.reco_p4,
        bjet1.reco_p4,
        bjet2.reco_p4,
        }
    -- Compute the phase space density for observed particles not concerned by the change of variable:
    -- here lepton on which we evaluate the TF
    -- The TF jacobian just account for dp/dE to go from |p| to E, not the phase space volume,
    -- the other blocks give the whole product of jacobian and phase space volume to go from one param to another
    StandardPhaseSpace.phaseSpaceOut = {
        particles = genParticles
    }
end


BuildInitialState.boost = {
    do_transverse_boost = true,
    particles = genParticles
}

jacobians = {'phaseSpaceOut::phase_space'}

if USE_TF then
    append(jacobians, {'tf_neg_lepton::TF_times_jacobian', 'looper::jacobian', 'tf_pos_lepton::TF_times_jacobian', 'tfEval_bjet1::TF', 'tfEval_bjet2::TF'})
end

MatrixElement.drellyan = {
  pdf = 'CT10nlo',
  pdf_scale = parameter('Z_mass'),

  matrix_element = parameter('matrix_element'),
  matrix_element_parameters = {
      card = parameter('matrix_element_parameters'),
  },

  initialState = 'boost::partons',

  particles = {
    inputs = genParticles,
    ids = {
      {
        pdg_id =  -11,
        me_index = 1,
      },
      {
        pdg_id = 11,
        me_index = 2,
      },
      {
        pdg_id = 5,
        me_index = 3,
      },
      {
        pdg_id = -5,
        me_index = 4,
      }
    }
  },

  jacobians = jacobians
}

DoubleLooperSummer.integrand = {
    input = "drellyan::output"
}

integrand("integrand::sum")
