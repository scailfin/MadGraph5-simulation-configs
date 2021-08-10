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
#include <iostream>

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

    std::string inputPath;  // required input
    std::string outputPath;  // required input
    std::string configPath {"drell-yan_example.lua"};  // default value
    std::string chainName {"event_selection/hftree"};  // default value
    std::vector <std::string> unusedCLIArguments;

    for (int idx = 1; idx < argc; ++idx) {
        // --input
        if (std::string(argv[idx]) == "--input") {
            if (idx + 1 < argc) { // Make sure not at the end of argv
                inputPath = argv[++idx]; // value is argv entry after flag
            } else {
                std::cerr << "--input option requires one argument." << std::endl;
                return 1;
            }
        }
        // --output
        else if (std::string(argv[idx]) == "--output") {
            if (idx + 1 < argc) {
                outputPath = argv[++idx];
            } else {
                std::cerr << "--output option requires one argument." << std::endl;
                return 1;
            }
        }
        // --chain
        else if (std::string(argv[idx]) == "--chain") {
            if (idx + 1 < argc) {
                chainName = argv[++idx];
            }
        }
        // --luaconfig
        else if (std::string(argv[idx]) == "--luaconfig") {
            if (idx + 1 < argc) {
                configPath = argv[++idx];
            }
        }
        else {
            unusedCLIArguments.push_back(argv[idx]);
        }
    }

    using std::swap;

    // Load events from input file, retrieve reconstructed particles and MET
    TChain chain(chainName.c_str());
    // Path needs to be findable inside of Docker container
    chain.Add(inputPath.c_str());
    TTreeReader myReader(&chain);

    // TODO: serialize the 4-momentum into the TTree over just using branches
    // TTreeReaderValue<LorentzVectorM> lep_plus_p4M(myReader, "lep1_p4");
    // TTreeReaderValue<LorentzVectorM> lep_minus_p4M(myReader, "lep2_p4");

    TTreeReaderValue<int> leading_lep_PID(myReader, "lep1_PID");

    TTreeReaderValue<float> lep_plus_Px(myReader, "lep1_Px");
    TTreeReaderValue<float> lep_plus_Py(myReader, "lep1_Py");
    TTreeReaderValue<float> lep_plus_Pz(myReader, "lep1_Pz");
    TTreeReaderValue<float> lep_plus_E(myReader, "lep1_E");

    TTreeReaderValue<float> lep_minus_Px(myReader, "lep2_Px");
    TTreeReaderValue<float> lep_minus_Py(myReader, "lep2_Py");
    TTreeReaderValue<float> lep_minus_Pz(myReader, "lep2_Pz");
    TTreeReaderValue<float> lep_minus_E(myReader, "lep2_E");

    TTreeReaderValue<float> bjet1_Px(myReader, "bjet1_Px");
    TTreeReaderValue<float> bjet1_Py(myReader, "bjet1_Py");
    TTreeReaderValue<float> bjet1_Pz(myReader, "bjet1_Pz");
    TTreeReaderValue<float> bjet1_E(myReader, "bjet1_E");

    TTreeReaderValue<float> bjet2_Px(myReader, "bjet2_Px");
    TTreeReaderValue<float> bjet2_Py(myReader, "bjet2_Py");
    TTreeReaderValue<float> bjet2_Pz(myReader, "bjet2_Pz");
    TTreeReaderValue<float> bjet2_E(myReader, "bjet2_E");

    // Define output TTree, which will contain the weights we're computing (including uncertainty and computation time)
    std::unique_ptr<TTree> out_tree = std::make_unique<TTree>("momemta", "momemta");
    double weight_DY, weight_DY_err, weight_DY_time;
    out_tree->Branch("weight_DY", &weight_DY);
    out_tree->Branch("weight_DY_err", &weight_DY_err);
    out_tree->Branch("weight_DY_time", &weight_DY_time);

    // Prepare MoMEMta to compute the weights

    logging::set_level(logging::level::debug);
    // logging::set_level(logging::level::error);

    // Construct the ConfigurationReader from the Lua file
    ConfigurationReader configuration(configPath);

    std::cout << "\n# Loaded MoMEMta Lua configuration\n" << std::endl;

    // Instantiate MoMEMta using a **frozen** configuration
    MoMEMta weight(configuration.freeze());

    int counter = 0;
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
        momemta::Particle lep_plus("lepton1",  LorentzVector { *lep_plus_Px, *lep_plus_Py, *lep_plus_Pz, *lep_plus_E });
        momemta::Particle lep_minus("lepton2", LorentzVector { *lep_minus_Px, *lep_minus_Py, *lep_minus_Pz, *lep_minus_E });
        momemta::Particle bjet1("bjet1", LorentzVector { *bjet1_Px, *bjet1_Py, *bjet1_Pz, *bjet1_E });
        momemta::Particle bjet2("bjet2", LorentzVector { *bjet2_Px, *bjet2_Py, *bjet2_Pz, *bjet2_E });

        // Due to numerical instability, the mass can sometimes be negative. If it's the case, change the energy in order to be mass-positive
        normalizeInput(lep_plus.p4);
        normalizeInput(lep_minus.p4);
        normalizeInput(bjet1.p4);
        normalizeInput(bjet2.p4);

        // Ensure the leptons are given in the correct order w.r.t their charge
        if (*leading_lep_PID < 0)
            swap(lep_plus, lep_minus);

        auto start_time = std::chrono::system_clock::now();
        // Compute the weights!
        // MoMEMta::computeWeights({vector of particles}, met)
        // The MET is an optional argument (defaults to a null vector)
        std::vector<std::pair<double, double>> weights = weight.computeWeights({lep_minus, lep_plus, bjet1, bjet2});
        auto end_time = std::chrono::system_clock::now();

        // Retrieve the weight and uncertainty
        weight_DY = weights.back().first;
        weight_DY_err = weights.back().second;
        weight_DY_time = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();

        LOG(debug) << "Event " << myReader.GetCurrentEntry() << " result: " << weight_DY << " +- " << weight_DY_err;
        LOG(info) << "Weight computed in " << weight_DY_time << "ms";

        out_tree->Fill();

        if (counter > 5) break;

        ++counter;
        if (counter % 1000 == 0)
            std::cout << "calculated weights for " << counter << " events\n";

    }
    std::cout << "calculated weights for " << counter << " events\n";

    // Save output to TTree
    out_tree->SaveAs(outputPath.c_str());

    return 0;
}
