-- c.f. https://github.com/MoMEMta/Tutorials/blob/master/Paper_configs/MELA_ZZ_bkg.lua for example copied form from

-- Load the library containing the matrix element
-- FIXME: Requires manual configuration
load_modules('MatrixElements/pp_drell_yan/build/libme_pp_drell_yan.so')

-- Declare inputs required by this configuration file. Since it's Drell-Yan, we expect 2 inputs (output paticles)
-- the two leptons
-- P4 for each particle are passed when calling the C++ `computeWeights` function
local lepton1 = declare_input("lepton1")
local lepton2 = declare_input("lepton2")

-- Global parameters used by several modules
-- Changing these has NO impact on the value of the parameters used by the matrix element!
parameters = {
    energy = 13000.,
    Z_mass = 91.1876,
    Z_width = 2.49,

    -- You can export a graphviz representation of the computation graph using the
    -- `export_graph_as` parameter
    -- Use the `dot` command to convert the graph into a PDF
    -- dot -Tpdf drell-yan_computing_graph.dot -o drell-yan_computing_graph.pdf
    export_graph_as = "drell-yan_computing_graph.dot"
}

-- Configuration of Cuba
cuba = {
    relative_accuracy = 0.05,
    verbosity = 3
}

-- The transfer functions take as input the particles passed in the computeWeights() function,
-- and each add a dimension of integration
GaussianTransferFunctionOnEnergy.tf_p1 = {
    -- add_dimension() generates an input tag allowing the retrieve a new phase-space point component,
    -- and it notifies MoMEMta that a new integration dimension is requested
    ps_point = add_dimension(),
    -- We use the directly the inputs declared above. The `reco_p4` attribute returns the correct input tag
    reco_particle = lepton1.reco_p4,
    sigma = 0.10,
    sigma_range = 3.,
}

-- We can assign to each input a `gen` p4. By default, the gen p4 is the same as the reco one, which is useful when
-- no transfer function is applied. Here however, we applied a transfer function to the `lepton1` input, meaning that the
-- output of the `tf_p1` module correspond now to the `gen` p4 of `lepton1`. To reflect that, we explicitly set the gen p4
-- to be the output of the `tf_p1` module
lepton1.set_gen_p4("tf_p1::output");

GaussianTransferFunctionOnEnergy.tf_p2 = {
    ps_point = add_dimension(),
    reco_particle = lepton2.reco_p4,
    sigma = 0.10,
    sigma_range = 3.,
}
lepton2.set_gen_p4("tf_p2::output")

-- Compute the phase space density for observed particles not concerned by the change of variable : here lepton on which we evaluate the TF
-- The TF jacobian just account for dp/dE to go from |p| to E, not the phase space volume, the other blocks give the whole product of jacobian and phase space volume to go from one param to another
StandardPhaseSpace.phaseSpaceOut = {
	particles = {'tf_p1::output', 'tf_p2::output'}
}

BuildInitialState.boost = {
    do_transverse_boost = true,
    particles = {lepton1.reco_p4, lepton2.reco_p4}
}

jacobians = {'phaseSpaceOut::phase_space'}

genParticles = {
	lepton1.reco_p4,
	lepton2.reco_p4,
}

MatrixElement.drellyan = {
  pdf = 'CT10nlo',
  pdf_scale = parameter('Z_mass'),

  matrix_element = 'pp_drell_yan_sm_P1_Sigma_sm_uux_epem',
  matrix_element_parameters = {
      card = 'MatrixElements/pp_drell_yan/Cards/param_card.dat'
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
      }
    }
  },

  jacobians = jacobians
}


-- Define quantity to be returned to MoMEMta
integrand("drellyan::output")

-- inputs_before_perm = {
--     'tf_p1::output',
--     'tf_p2::output',
-- }

-- inputs = {
--   lepton1.gen_p4,
--   lepton2.gen_p4,
-- }

-- -- The main block defines the phase-space parametrisation,
-- -- converts our particles given by the transfer functions, and our propagator masses
-- -- into solutions for the missing particles in the event
-- BlockD.blockd = {
--     p3 = inputs[1],
--     p4 = inputs[2],
-- }
