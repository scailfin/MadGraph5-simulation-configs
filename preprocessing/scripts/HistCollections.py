# Code inspired by and based partially on https://gitlab.cern.ch/scipp/mario-mapyde
from array import array

import ROOT
from ROOT import TH1F


class DelphesEvent:
    def __init__(self, event, high_lumi=False, **kwargs):
        self.event = event
        # Only one event
        try:
            weight = event.Event[0].Weight
        except AttributeError:
            weight = 0
        self.weight = weight

        # reasonable values: 25 GeV, 2.5 eta
        electron_pt_cut = kwargs.pop("e_pt_cut", 0.0)  # GeV
        electron_eta_cut = kwargs.pop("e_eta_cut", 0.0)
        muon_pt_cut = kwargs.pop("mu_pt_cut", electron_pt_cut)  # GeV
        muon_eta_cut = kwargs.pop("mu_eta_cut", electron_eta_cut)
        # reasonable values: 25 GeV, 4.5 eta
        jet_pt_cut = kwargs.pop("jet_pt_cut", 0.0)  # GeV
        jet_eta_cut = kwargs.pop("jet_eta_cut", 0.0)
        # reasonable values: 4.0 eta
        bjet_eta_cut = kwargs.pop("bjet_eta_cut", jet_eta_cut)

        # self.met=TLorentzVector()
        # Only one MET
        try:
            met = event.MissingET[0].P4()
        except AttributeError:
            met = None
        self.met = met

        self.leptons = []
        self.elecs = []
        for electron in event.Electron:
            if electron.PT > electron_pt_cut and abs(electron.Eta) < electron_eta_cut:
                self.elecs.append(electron)
                self.leptons.append(electron)
        self.muons = []
        for muon in event.Muon:
            if muon.PT > muon_pt_cut and abs(muon.Eta) < muon_eta_cut:
                self.muons.append(muon)
                self.leptons.append(muon)

        self.sorted_leptons = sorted(self.leptons, key=lambda lep: lep.PT, reverse=True)

        self.jets = []
        self.excl_jets = []
        self.tau_tags = []
        self.btags = []

        self.btag_eta = bjet_eta_cut if not high_lumi else 4.0

        for jet in event.Jet:
            if jet.TauTag:
                self.tau_tags.append(jet)
            if jet.BTag and abs(jet.Eta) < self.btag_eta:
                self.btags.append(jet)
            if jet.PT > jet_pt_cut and abs(jet.Eta) < jet_eta_cut:
                self.jets.append(jet)
                if not (jet.TauTag or jet.BTag):
                    self.excl_jets.append(jet)

        self.sorted_jets = sorted(self.jets, key=lambda jet: jet.PT, reverse=True)


class Hists:
    def add_branch(self, branch_name, branch_type, branch_len=1, default=0):
        self.branches[branch_name] = array(branch_type, branch_len * [default])
        branch_name_mod = branch_name
        if branch_len > 1:
            branch_name_mod = f"{branch_name}[{branch_len}]"
        self.tree.Branch(
            branch_name,
            self.branches[branch_name],
            f"{branch_name_mod}/{branch_type.upper()}",
        )

    def __init__(self, tag, topdir, detaillevel=99):
        self.topdir = topdir
        self.hists = {}
        self.tag = tag

        self.newdir = topdir.mkdir(tag)
        self.newdir.cd()

        self.detaillevel = detaillevel
        self.collections = {}

        # Make all the histograms here (!)

        # Basics
        self.hists["nElec"] = TH1F(
            "h_" + tag + "_nElec", tag + "_nElec;Number of Electrons;Events", 10, 0, 10
        )
        self.hists["nMuon"] = TH1F(
            "h_" + tag + "_nMuon", tag + "_nMuon;Number of Muons;Events", 10, 0, 10
        )
        self.hists["nTau"] = TH1F(
            "h_" + tag + "_nTau", tag + "_nTau;Number of Taus;Events", 10, 0, 10
        )
        self.hists["nbjet"] = TH1F(
            "h_" + tag + "_nbjets", tag + "_nbjets;Number of b-jets;Events", 10, 0, 10
        )
        self.hists["njet"] = TH1F(
            "h_" + tag + "_njets", tag + "_njets;Number of jets;Events", 10, 0, 10
        )
        self.hists["nLep"] = TH1F(
            "h_" + tag + "_nLep",
            tag + "_nLep;Number of Leptons (e/#mu);Events",
            10,
            0,
            10,
        )

        # B-jets
        self.hists["bPT"] = TH1F(
            "h_" + tag + "_bPT", tag + "_bPT;p_{T,b-jets};Events/(10GeV)", 50, 0, 500
        )
        self.hists["bPhi"] = TH1F(
            "h_" + tag + "_bPhi", tag + "_bPhi;#phi(b-jets);Events/(0.4)", 20, -4, 4
        )
        self.hists["bEta"] = TH1F(
            "h_" + tag + "_bEta", tag + "_bEta;#eta(b-jets);Events/(0.5)", 20, -5, 5
        )

        # Jets
        self.hists["jPT"] = TH1F(
            "h_" + tag + "_jPT", tag + "_jPT;p_{T,jets};Events/(10GeV)", 50, 0, 500
        )
        self.hists["jPhi"] = TH1F(
            "h_" + tag + "_jPhi", tag + "_jPhi;#phi(jets);Events/(0.4)", 20, -4, 4
        )
        self.hists["jEta"] = TH1F(
            "h_" + tag + "_jEta", tag + "_jEta;#eta(jets);Events/(0.5)", 20, -5, 5
        )
        self.hists["mjj"] = TH1F(
            "h_" + tag + "_mjj", tag + "_mjj;m(jj);Events/(100 GeV)", 100, 0, 10000
        )

        # Electrons
        self.hists["ePT"] = TH1F(
            "h_" + tag + "_ePT", tag + "_ePT;p^{e}_{T};Events/(10GeV)", 50, 0, 500
        )
        self.hists["ePhi"] = TH1F(
            "h_" + tag + "_ePhi", tag + "_ePhi;#phi(elecs);Events/(0.4)", 20, -4, 4
        )
        self.hists["eEta"] = TH1F(
            "h_" + tag + "_eEta", tag + "_eEta;#eta(elecs);Events/(0.5)", 20, -5, 5
        )
        self.hists["lePT"] = TH1F(
            "h_" + tag + "_lePT",
            tag + "_lePT;p^{lead-e}_{T};Events/(10GeV)",
            50,
            0,
            500,
        )
        self.hists["lePhi"] = TH1F(
            "h_" + tag + "_lePhi",
            tag + "_lePhi;#phi(leading-e);Events/(0.4)",
            20,
            -4,
            4,
        )
        self.hists["leEta"] = TH1F(
            "h_" + tag + "_leEta",
            tag + "_leEta;#eta(leading-e);Events/(0.5)",
            20,
            -5,
            5,
        )

        # Muons
        self.hists["mPT"] = TH1F(
            "h_" + tag + "_mPT", tag + "_mPT;p^{#mu}_{T};Events/(10GeV)", 50, 0, 500
        )
        self.hists["mPhi"] = TH1F(
            "h_" + tag + "_mPhi", tag + "_mPhi;#phi(muons);Events/(0.4)", 20, -4, 4
        )
        self.hists["mEta"] = TH1F(
            "h_" + tag + "_mEta", tag + "_mEta;#eta(muons);Events/(0.5)", 20, -5, 5
        )
        self.hists["lmPT"] = TH1F(
            "h_" + tag + "_lmPT",
            tag + "_lmPT;p^{lead-#mu}_{T};Events/(10GeV)",
            50,
            0,
            500,
        )
        self.hists["lmPhi"] = TH1F(
            "h_" + tag + "_lmPhi",
            tag + "_lmPhi;#phi(leading-#mu);Events/(0.4)",
            20,
            -4,
            4,
        )
        self.hists["lmEta"] = TH1F(
            "h_" + tag + "_lmEta",
            tag + "_lmEta;#eta(leading-#mu);Events/(0.5)",
            20,
            -5,
            5,
        )

        # Taus
        self.hists["tPT"] = TH1F(
            "h_" + tag + "_tPT", tag + "_tPT;p^{#tau}_{T};Events/(10GeV)", 50, 0, 500
        )
        self.hists["tPhi"] = TH1F(
            "h_" + tag + "_tPhi", tag + "_tPhi;#phi(taus);Events/(0.4)", 20, -4, 4
        )
        self.hists["tEta"] = TH1F(
            "h_" + tag + "_tEta", tag + "_tEta;#eta(taus);Events/(0.5)", 20, -5, 5
        )
        self.hists["ltPT"] = TH1F(
            "h_" + tag + "_ltPT",
            tag + "_ltPT;p^{lead-#tau}_{T};Events/(10GeV)",
            50,
            0,
            500,
        )
        self.hists["ltPhi"] = TH1F(
            "h_" + tag + "_ltPhi",
            tag + "_ltPhi;#phi(leading-#tau);Events/(0.4)",
            20,
            -4,
            4,
        )
        self.hists["ltEta"] = TH1F(
            "h_" + tag + "_ltEta",
            tag + "_ltEta;#eta(leading-#tau);Events/(0.5)",
            20,
            -5,
            5,
        )

        # MET
        self.hists["MET"] = TH1F(
            "h_" + tag + "_MET",
            tag + "_MET;E_{T}^{miss} [GeV];Events/(10 GeV)",
            100,
            0,
            1000,
        )
        self.hists["MET_invismu"] = TH1F(
            "h_" + tag + "_MET_invismu",
            tag + "_MET;E_{T}^{miss} [GeV];Events/(10 GeV)",
            100,
            0,
            1000,
        )

        for i, j in self.hists.items():
            j.Sumw2()

        self.branches = {}
        self.tree = ROOT.TTree("hftree", "hftree")
        self.add_branch("MET", "f")
        self.add_branch("METPhi", "f")
        self.add_branch("MET_invismu", "f")
        self.add_branch("METPhi_invismu", "f")

        self.add_branch("nElec", "i")
        self.add_branch("nMuon", "i")
        self.add_branch("nTau", "i")
        self.add_branch("nbjet", "i")
        self.add_branch("njet", "i")
        self.add_branch("nLep", "i")

        # self.add_branch("lep1_p4", "TLorentzVector")
        self.add_branch("lep1_PID", "i")
        self.add_branch("lep1_Pt", "f")
        self.add_branch("lep1_Eta", "f")
        self.add_branch("lep1_Phi", "f")
        self.add_branch("lep1_M", "f")

        # Temporary hack to get 4-momentum components out
        self.add_branch("lep1_Px", "f")
        self.add_branch("lep1_Py", "f")
        self.add_branch("lep1_Pz", "f")
        self.add_branch("lep1_E", "f")

        # self.add_branch("lep2_p4", "TLorentzVector")
        self.add_branch("lep2_PID", "i")
        self.add_branch("lep2_Pt", "f")
        self.add_branch("lep2_Eta", "f")
        self.add_branch("lep2_Phi", "f")
        self.add_branch("lep2_M", "f")

        # Temporary hack to get 4-momentum components out
        self.add_branch("lep2_Px", "f")
        self.add_branch("lep2_Py", "f")
        self.add_branch("lep2_Pz", "f")
        self.add_branch("lep2_E", "f")

        self.add_branch("tau1PT", "f")
        self.add_branch("tau1Eta", "f")
        self.add_branch("tau1Phi", "f")

        self.add_branch("j1PT", "f")
        self.add_branch("j1Eta", "f")
        self.add_branch("j1Phi", "f")
        self.add_branch("j2PT", "f")
        self.add_branch("j2Eta", "f")
        self.add_branch("j2Phi", "f")
        self.add_branch("mjj", "f")

        self.add_branch("bj1PT", "f")
        self.add_branch("bj1Eta", "f")
        self.add_branch("bj1Phi", "f")
        self.add_branch("bj2PT", "f")
        self.add_branch("bj2Eta", "f")
        self.add_branch("bj2Phi", "f")

        self.add_branch("weight", "f")

    def write(self):
        self.newdir.cd()
        for i, k in self.hists.items():
            k.Write()
        for i, k in self.collections.items():
            k.write()
        self.tree.Write()
        self.topdir.cd()

    def add(self, coll):
        for i, k in self.hists.items():
            if i in coll.hists:
                k.Add(coll.hists[i])
        for i, k in self.collections.items():
            if i in coll.collections:
                k.add(coll.collections[i])

    def fill(self, event, weight=0):

        default_fill = -999

        for i, k in self.collections.items():
            k.fill(event, weight)

        self.branches["weight"][0] = weight

        # Do some characterizations
        # event.sorted_leptons are pT sorted in descending order
        leading_lepton = (
            event.sorted_leptons[0] if len(event.sorted_leptons) > 0 else None
        )
        subleading_lepton = (
            event.sorted_leptons[1] if len(event.sorted_leptons) > 1 else None
        )

        muons_momentum = ROOT.TLorentzVector()
        muons_momentum.SetPtEtaPhiM(0, 0, 0, 0)
        for muon in event.muons:
            muons_momentum += muon.P4()

        # Fill generic hists
        self.hists["nElec"].Fill(len(event.elecs), weight)
        self.hists["nMuon"].Fill(len(event.muons), weight)
        self.hists["nTau"].Fill(len(event.tau_tags), weight)
        self.hists["nbjet"].Fill(len(event.btags), weight)
        self.hists["njet"].Fill(len(event.jets), weight)
        self.hists["nLep"].Fill(len(event.elecs) + len(event.muons), weight)
        self.hists["MET"].Fill(event.met.Pt(), weight)
        self.hists["MET_invismu"].Fill((event.met + muons_momentum).Pt(), weight)

        self.branches["MET"][0] = event.met.Pt()
        self.branches["METPhi"][0] = event.met.Phi()
        self.branches["MET_invismu"][0] = (event.met + muons_momentum).Pt()
        self.branches["METPhi_invismu"][0] = (event.met + muons_momentum).Phi()
        self.branches["nElec"][0] = len(event.elecs)
        self.branches["nMuon"][0] = len(event.muons)
        self.branches["nTau"][0] = len(event.tau_tags)
        self.branches["nbjet"][0] = len(event.btags)
        self.branches["njet"][0] = len(event.jets)
        self.branches["nLep"][0] = len(event.elecs) + len(event.muons)

        # B-jets
        for aBJet in event.btags:
            self.hists["bPT"].Fill(aBJet.PT, weight)
            self.hists["bEta"].Fill(aBJet.Eta, weight)
            self.hists["bPhi"].Fill(aBJet.Phi, weight)

        # Jets
        for aJet in event.excl_jets:
            self.hists["jPT"].Fill(aJet.PT, weight)
            self.hists["jEta"].Fill(aJet.Eta, weight)
            self.hists["jPhi"].Fill(aJet.Phi, weight)
        if len(event.excl_jets) > 1:
            mjj = (event.excl_jets[0].P4() + event.excl_jets[1].P4()).M()
            self.hists["mjj"].Fill(mjj, weight)
            self.branches["mjj"][0] = mjj
        # Electrons
        for aElec in event.elecs:
            self.hists["ePT"].Fill(aElec.PT, weight)
            self.hists["eEta"].Fill(aElec.Eta, weight)
            self.hists["ePhi"].Fill(aElec.Phi, weight)
        if len(event.elecs) > 0:
            self.hists["lePT"].Fill(event.elecs[0].PT, weight)
            self.hists["leEta"].Fill(event.elecs[0].Eta, weight)
            self.hists["lePhi"].Fill(event.elecs[0].Phi, weight)

        # Muons
        for aMuon in event.muons:
            self.hists["mPT"].Fill(aMuon.PT, weight)
            self.hists["mEta"].Fill(aMuon.Eta, weight)
            self.hists["mPhi"].Fill(aMuon.Phi, weight)
        if len(event.muons) > 0:
            self.hists["lmPT"].Fill(event.muons[0].PT, weight)
            self.hists["lmEta"].Fill(event.muons[0].Eta, weight)
            self.hists["lmPhi"].Fill(event.muons[0].Phi, weight)

        # Taus
        for aTau in event.tau_tags:
            self.hists["tPT"].Fill(aTau.PT, weight)
            self.hists["tEta"].Fill(aTau.Eta, weight)
            self.hists["tPhi"].Fill(aTau.Phi, weight)
        if len(event.tau_tags) > 0:
            self.hists["ltPT"].Fill(event.tau_tags[0].PT, weight)
            self.hists["ltEta"].Fill(event.tau_tags[0].Eta, weight)
            self.hists["ltPhi"].Fill(event.tau_tags[0].Phi, weight)
            self.branches["tau1PT"][0] = event.tau_tags[0].PT
            self.branches["tau1Eta"][0] = event.tau_tags[0].Eta
            self.branches["tau1Phi"][0] = event.tau_tags[0].Phi
        else:
            self.branches["tau1PT"][0] = default_fill
            self.branches["tau1Eta"][0] = default_fill
            self.branches["tau1Phi"][0] = default_fill

        # b-jets
        if len(event.btags) > 0:
            self.branches["bj1PT"][0] = event.btags[0].P4().Pt()
            self.branches["bj1Eta"][0] = event.btags[0].P4().Eta()
            self.branches["bj1Phi"][0] = event.btags[0].P4().Phi()
        else:
            self.branches["bj1PT"][0] = default_fill
            self.branches["bj1Eta"][0] = default_fill
            self.branches["bj1Phi"][0] = default_fill
        if len(event.btags) > 1:
            self.branches["bj2PT"][0] = event.btags[1].P4().Pt()
            self.branches["bj2Eta"][0] = event.btags[1].P4().Eta()
            self.branches["bj2Phi"][0] = event.btags[1].P4().Phi()
        else:
            self.branches["bj2PT"][0] = default_fill
            self.branches["bj2Eta"][0] = default_fill
            self.branches["bj2Phi"][0] = default_fill

        # non-b/tau-jets
        if len(event.excl_jets) > 0:
            self.branches["j1PT"][0] = event.excl_jets[0].P4().Pt()
            self.branches["j1Eta"][0] = event.excl_jets[0].P4().Eta()
            self.branches["j1Phi"][0] = event.excl_jets[0].P4().Phi()
        else:
            self.branches["j1PT"][0] = default_fill
            self.branches["j1Eta"][0] = default_fill
            self.branches["j1Phi"][0] = default_fill
        if len(event.excl_jets) > 1:
            self.branches["j2PT"][0] = event.excl_jets[1].P4().Pt()
            self.branches["j2Eta"][0] = event.excl_jets[1].P4().Eta()
            self.branches["j2Phi"][0] = event.excl_jets[1].P4().Phi()
        else:
            self.branches["j2PT"][0] = default_fill
            self.branches["j2Eta"][0] = default_fill
            self.branches["j2Phi"][0] = default_fill

        # Leptons
        if leading_lepton:
            leading_lepton_p4 = leading_lepton.P4()
            # self.branches["lep1_p4"][0] = leading_lepton
            self.branches["lep1_PID"][0] = leading_lepton.Particle.GetObject().PID
            self.branches["lep1_Pt"][0] = leading_lepton_p4.Pt()
            self.branches["lep1_Eta"][0] = leading_lepton_p4.Eta()
            self.branches["lep1_Phi"][0] = leading_lepton_p4.Phi()
            self.branches["lep1_M"][0] = leading_lepton_p4.M()
            # Temporary hack to get 4-momentum components out
            self.branches["lep1_Px"][0] = leading_lepton_p4.Px()
            self.branches["lep1_Py"][0] = leading_lepton_p4.Py()
            self.branches["lep1_Pz"][0] = leading_lepton_p4.Pz()
            self.branches["lep1_E"][0] = leading_lepton_p4.E()
        else:
            for branch_name in [
                "lep1_PID",
                "lep1_Pt",
                "lep1_Eta",
                "lep1_Phi",
                "lep1_M",
                "lep1_Px",
                "lep1_Py",
                "lep1_Pz",
                "lep1_E",
            ]:
                self.branches[branch_name][0] = default_fill

        if subleading_lepton:
            subleading_lepton_p4 = subleading_lepton.P4()
            # self.branches["lep1_p4"][0] = subleading_lepton
            self.branches["lep2_PID"][0] = subleading_lepton.Particle.GetObject().PID
            self.branches["lep2_Pt"][0] = subleading_lepton_p4.Pt()
            self.branches["lep2_Eta"][0] = subleading_lepton_p4.Eta()
            self.branches["lep2_Phi"][0] = subleading_lepton_p4.Phi()
            self.branches["lep2_M"][0] = subleading_lepton_p4.M()
            # Temporary hack to get 4-momentum components out
            self.branches["lep2_Px"][0] = subleading_lepton_p4.Px()
            self.branches["lep2_Py"][0] = subleading_lepton_p4.Py()
            self.branches["lep2_Pz"][0] = subleading_lepton_p4.Pz()
            self.branches["lep2_E"][0] = subleading_lepton_p4.E()
        else:
            for branch_name in [
                "lep2_PID",
                "lep2_Pt",
                "lep2_Eta",
                "lep2_Phi",
                "lep2_M",
                "lep2_Px",
                "lep2_Py",
                "lep2_Pz",
                "lep2_E",
            ]:
                self.branches[branch_name][0] = default_fill

        self.tree.Fill()
