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
    TChain chain("t");
    // chain.Add("figure out how to make this a configurable path.root");
    chain.Add("/data/hepmc_output/delphes_output/delphes_output_nevent_10e4.root");
    TTreeReader myReader(&chain);

    std::cout << "chain " << &chain << "\n";

    TTreeReaderValue<LorentzVectorM> lep_plus_p4M(myReader, "lep1_p4");
    TTreeReaderValue<LorentzVectorM> lep_minus_p4M(myReader, "lep2_p4");

    /*
     * Define output TTree, which will contain the weights we're computing (including uncertainty and computation time)
     */
    std::unique_ptr<TTree> out_tree = std::make_unique<TTree>("t", "t");
    double weight_DY, weight_DY_err, weight_DY_time;
    out_tree->Branch("weight_DY", &weight_DY);
    out_tree->Branch("weight_DY_err", &weight_DY_err);
    out_tree->Branch("weight_DY_time", &weight_DY_time);

    /*
     * Prepare MoMEMta to compute the weights
     */
    // Set MoMEMta's logging level to `debug`
    logging::set_level(logging::level::debug);

    // ...

    // Save our output TTree
    out_tree->SaveAs("drell-yan_weights_test.root");

    return 0;
}
