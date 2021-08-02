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
    TChain chain("event_selection/hftree");
    // chain.Add("figure out how to make this a configurable path.root");
    // Path needs to be findable inside of Docker container
    chain.Add("/home/feickert/workarea/MadGraph5-simulation-configs/preprocessing/preprocessing_output.root");
    TTreeReader myReader(&chain);

    std::cout << "chain " << &chain << "\n";

    // As these need to be branch names in the TTree this means that there
    // necessarily needs to have a preprcoessing stage outside of the
    // MoMEMta analysis stage
    // Example:
    //    $ root -l tt_20evt.root  # This is the example tutorial file
    //    root [0]
    //    Attaching file tt_20evt.root as _file0...
    //    (TFile *) 0x55f4f03130d0
    //    root [1] _file0->ls()
    //    TFile**		tt_20evt.root
    //    TFile*		tt_20evt.root
    //    KEY: TTree	t;1	t
    //    root [2] lepton1_branch = t->GetBranch("lep1_p4")
    //    (TBranch *) @0x7fff98b15890
    //    root [3] lepton1_branch->Print()
    //    *Branch  :lep1_p4                                                            *
    //    *Entries :       20 : BranchElement (see below)                              *
    //    *............................................................................*
    //    *Br   81 :fCoordinates :                                                     *
    //    *Entries :       20 : Total  Size=       3958 bytes  One basket in memory    *
    //    *Baskets :        0 : Basket Size=      32000 bytes  Compression=   1.00     *
    //    *............................................................................*
    //    *Br   82 :fCoordinates.fPt : Float_t                                         *
    //    *Entries :       20 : Total  Size=        789 bytes  All baskets in memory   *
    //    *Baskets :        1 : Basket Size=      32000 bytes  Compression=   1.00     *
    //    *............................................................................*
    //    *Br   83 :fCoordinates.fEta : Float_t                                        *
    //    *Entries :       20 : Total  Size=        795 bytes  All baskets in memory   *
    //    *Baskets :        1 : Basket Size=      32000 bytes  Compression=   1.00     *
    //    *............................................................................*
    //    *Br   84 :fCoordinates.fPhi : Float_t                                        *
    //    *Entries :       20 : Total  Size=        795 bytes  All baskets in memory   *
    //    *Baskets :        1 : Basket Size=      32000 bytes  Compression=   1.00     *
    //    *............................................................................*
    //    *Br   85 :fCoordinates.fM : Float_t                                          *
    //    *Entries :       20 : Total  Size=        783 bytes  All baskets in memory   *
    //    *Baskets :        1 : Basket Size=      32000 bytes  Compression=   1.00     *
    //    *............................................................................*
    //
    // and then with the DELPHES output
    //
    //    $ root -l delphes_output_nevent_10e4.root
    //    root [0]
    //    (TFile *) 0x5633fbd61b40
    //    root [1] _file0->ls()
    //    TFile**		delphes_output_nevent_10e4.root
    //    TFile*		delphes_output_nevent_10e4.root
    //    KEY: TProcessID	ProcessID0;1	9b0e9308-d561-11eb-9149-020011acbeef
    //    KEY: TTree	Delphes;1	Analysis tree
    //    root [2] particle_branch = Delphes->GetBranch("Particle")
    //    (TBranch *) @0x7ffcff7f21a0
    //    root [3] particle_branch->Print()
    //    *Br    0 :Particle  : Int_t Particle_                                        *
    //    *Entries :    10000 : Total  Size=     131038 bytes  File Size  =      39636 *
    //    *Baskets :       20 : Basket Size=      64000 bytes  Compression=   2.06     *
    //    *............................................................................*
    //    *Br    1 :Particle.fUniqueID : UInt_t fUniqueID[Particle_]                   *
    //    *Entries :    10000 : Total  Size=   49119923 bytes  File Size  =   15014630 *
    //    *Baskets :       78 : Basket Size=    1790976 bytes  Compression=   3.27     *
    //    *............................................................................*
    //    ...


    // TTreeReaderValue<LorentzVectorM> lep_plus_p4M(myReader, "lep1_p4");
    // TTreeReaderValue<LorentzVectorM> lep_minus_p4M(myReader, "lep2_p4");

    TTreeReaderValue<float> lep_plus_Pt(myReader, "lep1_Pt");

    /*
     * Define output TTree, which will contain the weights we're computing (including uncertainty and computation time)
     */
    std::unique_ptr<TTree> out_tree = std::make_unique<TTree>("momemta", "momemta");
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
        // momemta::Particle lep_plus("lepton1",  LorentzVector { lep_plus_p4M->Px(), lep_plus_p4M->Py(), lep_plus_p4M->Pz(), lep_plus_p4M->E() });
        // momemta::Particle lep_minus("lepton2", LorentzVector { lep_minus_p4M->Px(), lep_minus_p4M->Py(), lep_minus_p4M->Pz(), lep_minus_p4M->E() });

        std::cout << "lep_plus_Pt " << lep_plus_Pt << "\n";
    }

    // ...

    // Save our output TTree
    out_tree->SaveAs("drell-yan_weights_test.root");

    return 0;
}
