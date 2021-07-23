#include <momemta/ConfigurationReader.h>
#include <momemta/Logging.h>
#include <momemta/MoMEMta.h>
#include <momemta/Unused.h>

#include <TTree.h>
#include <TChain.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <Math/PtEtaPhiM4D.h>
#include <Math/LorentzVector.h>

#include <chrono>
#include <memory>

#include <iostream>  // for printing tchain for sanity check

using namespace std::chrono;

using LorentzVectorM = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;

/*
 * Example executable file loading an input sample of events,
 * computing weights using MoMEMta in the Drell-Yan hypothesis,
 * and saving these weights along with a copy of the event content in an output file.
 */

void normalizeInput(LorentzVector& p4) {
    if (p4.M() > 0)
        return;

    // Increase the energy until M is positive
    p4.SetE(p4.P());
    while (p4.M2() < 0) {
        double delta = p4.E() * 1e-5;
        p4.SetE(p4.E() + delta);
    };
}

int main(int argc, char** argv) {

    UNUSED(argc);
    UNUSED(argv);

    using std::swap;

    /*
     * Load events from input file, retrieve reconstructed particles and MET
     */
    TChain chain("Delphes");
    // chain.Add("figure out how to make this a configurable path.root");
    // Path needs to be findable inside of Docker container
    chain.Add("/data/hepmc_output/delphes_output/delphes_output_nevent_10e4.root");
    TTreeReader myReader(&chain);

    std::cout << "chain " << &chain << "\n";

    TTreeReaderValue<LorentzVectorM> lep_plus_p4M(myReader, "lep1_p4");
    TTreeReaderValue<LorentzVectorM> lep_minus_p4M(myReader, "lep2_p4");

    /*
     * Define output TTree, which will contain the weights we're computing (including uncertainty and computation time)
     */
    std::unique_ptr<TTree> out_tree = std::make_unique<TTree>("Delphes", "Delphes");
    double weight_DY, weight_DY_err, weight_DY_time;
    out_tree->Branch("weight_DY", &weight_DY);
    out_tree->Branch("weight_DY_err", &weight_DY_err);
    out_tree->Branch("weight_DY_time", &weight_DY_time);

    /*
     * Prepare MoMEMta to compute the weights
     */
    // Set MoMEMta's logging level to `debug`
    logging::set_level(logging::level::debug);

    // Construct the ConfigurationReader from the Lua file
    ConfigurationReader configuration("drell-yan_example.lua");

    // Instantiate MoMEMta using a **frozen** configuration
    MoMEMta weight(configuration.freeze());

    while (myReader.Next()) {
        /*
         * Prepare the LorentzVectors passed to MoMEMta:
         * In the input file they are written in the PtEtaPhiM<float> basis,
         * while MoMEMta expects PxPyPzE<double>, so we have to perform this change of basis:
         *
         * We define here Particles, allowing MoMEMta to correctly map the inputs to the configuration file.
         * The string identifier used here must be the same as used to declare the inputs in the config file
         */
        momemta::Particle lep_plus("lepton1",  LorentzVector { lep_plus_p4M->Px(), lep_plus_p4M->Py(), lep_plus_p4M->Pz(), lep_plus_p4M->E() });
        momemta::Particle lep_minus("lepton2", LorentzVector { lep_minus_p4M->Px(), lep_minus_p4M->Py(), lep_minus_p4M->Pz(), lep_minus_p4M->E() });
    }

    // ...

    // Save our output TTree
    out_tree->SaveAs("drell-yan_weights_test.root");

    return 0;
}
