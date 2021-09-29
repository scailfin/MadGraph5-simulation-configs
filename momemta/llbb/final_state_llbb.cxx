#include <momemta/ConfigurationReader.h>
#include <momemta/Logging.h>
#include <momemta/MoMEMta.h>
#include <momemta/Unused.h>

#include <Math/LorentzVector.h>
#include <Math/PtEtaPhiM4D.h>
#include <TChain.h>
#include <TTree.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>

#include <chrono>
#include <iostream>
#include <memory>
#include <stdlib.h> // provide: exit, EXIT_FAILURE

using LorentzVectorM = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;

/*
 * Example executable file loading an input sample of events,
 * computing weights using MoMEMta in the Drell-Yan hypothesis,
 * and saving these weights along with a copy of the event content in an output file.
 */

void normalizeInput(LorentzVector& p4) {
    if(p4.M() > 0)
        return;

    // Increase the energy until M is positive
    p4.SetE(p4.P());
    while(p4.M2() < 0) {
        double delta = p4.E() * 1e-5;
        p4.SetE(p4.E() + delta);
    };
}

int main(int argc, char** argv) {
    std::string inputPath;                           // required input
    std::string outputPath;                          // required input
    std::string configPath{"drell-yan_example.lua"}; // default value
    std::string chainName{"event_selection/hftree"}; // default value
    int totalSteps{0};                               // default value
    int stepNumber{0};                               // default value
    std::vector<std::string> unusedCLIArguments;

    for(int idx = 1; idx < argc; ++idx) {
        // --input
        if(std::string(argv[idx]) == "--input") {
            if(idx + 1 < argc) {         // Make sure not at the end of argv
                inputPath = argv[++idx]; // value is argv entry after flag
            } else {
                std::cerr << "--input option requires one argument." << std::endl;
                return 1;
            }
        }
        // --output
        else if(std::string(argv[idx]) == "--output") {
            if(idx + 1 < argc) {
                outputPath = argv[++idx];
            } else {
                std::cerr << "--output option requires one argument." << std::endl;
                return 1;
            }
        }
        // --chain
        else if(std::string(argv[idx]) == "--chain") {
            if(idx + 1 < argc) {
                chainName = argv[++idx];
            }
        }
        // --luaconfig
        else if(std::string(argv[idx]) == "--luaconfig") {
            if(idx + 1 < argc) {
                configPath = argv[++idx];
            }
        }
        // --nsteps
        else if(std::string(argv[idx]) == "--nsteps") {
            if(idx + 1 < argc) {
                totalSteps = std::stoi(argv[++idx]);
            }
        }
        // --step
        else if(std::string(argv[idx]) == "--step") {
            if(idx + 1 < argc) {
                stepNumber = std::stoi(argv[++idx]);
            }
        } else {
            unusedCLIArguments.push_back(argv[idx]);
        }
    }

    if(totalSteps > 0 && (stepNumber == totalSteps)) {
        std::cerr << "\n# ERROR: CLI arguments --nsteps and --step are the same: "
                  << "--nsteps " << totalSteps << " --step " << stepNumber << "\n"
                  << "This would result in an error so exiting now.\n"
                  << std::endl;
        exit(EXIT_FAILURE);
    }

    using std::swap;

    // Load events from input file, retrieve reconstructed particles and MET
    TChain chain(chainName.c_str());
    // Path needs to be findable inside of Docker container
    chain.Add(inputPath.c_str());
    TTreeReader treeReader(&chain);

    // TODO: serialize the 4-momentum into the TTree over just using branches
    // TTreeReaderValue<LorentzVectorM> lep_plus_p4M(treeReader, "lep1_p4");
    // TTreeReaderValue<LorentzVectorM> lep_minus_p4M(treeReader, "lep2_p4");

    TTreeReaderValue<int> leading_lep_PID(treeReader, "lep1_PID");

    TTreeReaderValue<float> lep_plus_Px(treeReader, "lep1_Px");
    TTreeReaderValue<float> lep_plus_Py(treeReader, "lep1_Py");
    TTreeReaderValue<float> lep_plus_Pz(treeReader, "lep1_Pz");
    TTreeReaderValue<float> lep_plus_E(treeReader, "lep1_E");

    TTreeReaderValue<float> lep_minus_Px(treeReader, "lep2_Px");
    TTreeReaderValue<float> lep_minus_Py(treeReader, "lep2_Py");
    TTreeReaderValue<float> lep_minus_Pz(treeReader, "lep2_Pz");
    TTreeReaderValue<float> lep_minus_E(treeReader, "lep2_E");

    TTreeReaderValue<float> bjet1_Px(treeReader, "bjet1_Px");
    TTreeReaderValue<float> bjet1_Py(treeReader, "bjet1_Py");
    TTreeReaderValue<float> bjet1_Pz(treeReader, "bjet1_Pz");
    TTreeReaderValue<float> bjet1_E(treeReader, "bjet1_E");

    TTreeReaderValue<float> bjet2_Px(treeReader, "bjet2_Px");
    TTreeReaderValue<float> bjet2_Py(treeReader, "bjet2_Py");
    TTreeReaderValue<float> bjet2_Pz(treeReader, "bjet2_Pz");
    TTreeReaderValue<float> bjet2_E(treeReader, "bjet2_E");

    // Define output TTree, which will contain the weights we're computing (including
    // uncertainty and computation time)
    std::unique_ptr<TTree> out_tree = std::make_unique<TTree>("momemta", "momemta");
    double weight_DY, weight_DY_err, weight_DY_time;
    out_tree->Branch("weight_DY", &weight_DY);
    out_tree->Branch("weight_DY_err", &weight_DY_err);
    out_tree->Branch("weight_DY_time", &weight_DY_time);

    // Prepare MoMEMta to compute the weights

    // logging::set_level(logging::level::debug);
    logging::set_level(logging::level::error);

    // Construct the ConfigurationReader from the Lua file
    ConfigurationReader configuration(configPath);

    std::cout << "\n# Loaded MoMEMta Lua configuration\n" << std::endl;

    // Instantiate MoMEMta using a **frozen** configuration
    MoMEMta weight(configuration.freeze());

    // c.f.
    // https://root.cern.ch/doc/v624/classTTreeReader.html#abe0530cfddbf50d5266d3d9ebb68972b
    int totalNEvents     = treeReader.GetEntries(true);
    int fractionOfEvents = totalNEvents / 20;

    int counter = 0;

    if(totalSteps > 0) {
        std::vector<int> steps{};
        int stepSize{static_cast<int>(
            std::round(totalNEvents / static_cast<float>(totalSteps)))};

        for(int n = 0; n < totalSteps; ++n)
            steps.push_back(n * stepSize);
        // push_back outside of the loop instead of using `n <= totalSteps` as
        // there will probably be a non-integer unrounded step size, so make
        // the last step big enough to get the remainder
        steps.push_back(totalNEvents);

        std::cout << "\n# calculating weights for event range: ("
                  << steps.at(stepNumber) << ", " << steps.at(stepNumber + 1) - 1
                  << ")\n"
                  << std::endl;

        // This call is usually followed by an iteration of the range using
        // TTreeReader::Next(), which will visit the the entries from begiNEntry to
        // endEntry - 1.
        treeReader.SetEntriesRange(steps.at(stepNumber), steps.at(stepNumber + 1));

        counter = steps.at(stepNumber);
    }

    while(treeReader.Next()) {
        /*
         * Prepare the LorentzVectors passed to MoMEMta:
         * In the input file they are written in the PtEtaPhiM<float> basis,
         * while MoMEMta expects PxPyPzE<double>, so we have to perform this change of
         * basis:
         *
         * We define here Particles, allowing MoMEMta to correctly map the inputs to the
         * configuration file. The string identifier used here must be the same as used
         * to declare the inputs in the config file
         */
        // momemta::Particle lep_plus("lepton1",  LorentzVector { lep_plus_p4M->Px(),
        // lep_plus_p4M->Py(), lep_plus_p4M->Pz(), lep_plus_p4M->E() });
        // momemta::Particle lep_minus("lepton2", LorentzVector { lep_minus_p4M->Px(),
        // lep_minus_p4M->Py(), lep_minus_p4M->Pz(), lep_minus_p4M->E() });
        momemta::Particle lep_plus(
            "lepton1",
            LorentzVector{*lep_plus_Px, *lep_plus_Py, *lep_plus_Pz, *lep_plus_E});
        momemta::Particle lep_minus(
            "lepton2",
            LorentzVector{*lep_minus_Px, *lep_minus_Py, *lep_minus_Pz, *lep_minus_E});
        momemta::Particle bjet1(
            "bjet1", LorentzVector{*bjet1_Px, *bjet1_Py, *bjet1_Pz, *bjet1_E});
        momemta::Particle bjet2(
            "bjet2", LorentzVector{*bjet2_Px, *bjet2_Py, *bjet2_Pz, *bjet2_E});

        // Due to numerical instability, the mass can sometimes be negative. If it's the
        // case, change the energy in order to be mass-positive
        normalizeInput(lep_plus.p4);
        normalizeInput(lep_minus.p4);
        normalizeInput(bjet1.p4);
        normalizeInput(bjet2.p4);

        // Ensure the leptons are given in the correct order w.r.t their charge
        if(*leading_lep_PID < 0)
            swap(lep_plus, lep_minus);

        auto start_time = std::chrono::system_clock::now();
        // Compute the weights!
        // MoMEMta::computeWeights({vector of particles}, met)
        // The MET is an optional argument (defaults to a null vector)
        std::vector<std::pair<double, double>> weights
            = weight.computeWeights({lep_minus, lep_plus, bjet1, bjet2});
        auto end_time = std::chrono::system_clock::now();

        // Retrieve the weight and uncertainty
        weight_DY      = weights.back().first;
        weight_DY_err  = weights.back().second;
        weight_DY_time = std::chrono::duration_cast<std::chrono::milliseconds>(
                             end_time - start_time)
                             .count();

        LOG(debug) << "Event " << treeReader.GetCurrentEntry()
                   << " result: " << weight_DY << " +- " << weight_DY_err;
        LOG(info) << "Weight computed in " << weight_DY_time << "ms";

        out_tree->Fill();

        ++counter;
        if(counter % fractionOfEvents == 0) {
            std::cout << "calculated weights for " << counter << " events ("
                      << std::round(counter * 100. / totalNEvents) << "% of "
                      << totalNEvents << " events)\n";
        }
    }
    std::cout << "calculated weights for " << counter << " events ("
              << std::round(counter * 100. / totalNEvents) << "% of " << totalNEvents
              << " events)\n";

    // Save output to TTree
    out_tree->SaveAs(outputPath.c_str());

    return 0;
}
