import ROOT
import os 

ROOT.gROOT.SetBatch(ROOT.kTRUE)

max_evt = 2000
#rootfile_name = "fccee_idea_LAr_photongun10GeV_10kevt_nonoise.root"
rootfile_name = "fccee_idea_LAr_photongun10GeV_500evt_nonoise_withBothClustering.root"
plot_dir_name = "plot_"+rootfile_name.replace('.root','')
if not os.path.isdir(plot_dir_name):
  os.mkdir(plot_dir_name)
f = ROOT.TFile(rootfile_name)
events = f.Get("events")

th1_total_energy_barrelHits = ROOT.TH1F("th1_total_energy_barrelHits", "th1_total_energy_barrelHits", 100, 0, 5)
th1_total_energy_ecalBarrelCells = ROOT.TH1F("th1_total_energy_ecalBarrelCells", "th1_total_energy_ecalBarrelCells", 100, 0, 20)
th1_total_energy_ecalBarrelswCluster = ROOT.TH1F("th1_total_energy_ecalBarrelswCluster", "th1_total_energy_ecalBarrelswCluster", 100, 0, 20)
th1_total_energy_ecalBarreltopoCluster = ROOT.TH1F("th1_total_energy_ecalBarreltopoCluster", "th1_total_energy_ecalBarreltopoCluster", 100, 0, 20)
evt = 0
for event in events:
    if evt >= max_evt:
        break
    #barrelHits = event.ECalBarrelPositionedHits
    barrelCells = event.ECalBarrelCells
    topoClusters = event.caloClustersBarrelTopo
    swClusters = event.CaloClustersSW
    #total_energy_barrelHits = 0
    total_energy_barrelCells = 0
    total_energy_topoClusters = 0
    total_energy_swClusters = 0
    #for barrelHit in barrelHits:
    #    total_energy_barrelHits += barrelHit.core.energy
    for barrelCell in barrelCells:
        total_energy_barrelCells += barrelCell.core.energy
    for topoCluster in topoClusters:
        total_energy_topoClusters += topoCluster.core.energy
    for swCluster in swClusters:
        total_energy_swClusters += swCluster.core.energy
    #th1_total_energy_barrelHits.Fill(total_energy_barrelHits)
    th1_total_energy_ecalBarrelCells.Fill(total_energy_barrelCells)
    th1_total_energy_ecalBarrelswCluster.Fill(total_energy_swClusters)
    th1_total_energy_ecalBarreltopoCluster.Fill(total_energy_topoClusters)
    if evt % 100 == 0:
        print evt
    evt += 1

#canvas_total_energy_barrelHits = ROOT.TCanvas('canvas_total_energy_barrelHits', 'canvas_total_energy_barrelHits')
#th1_total_energy_barrelHits.Draw()
#canvas_total_energy_barrelHits.Print(plot_dir_name+'/total_energy_from_barrelPositionedHitSum.png')

canvas_total_energy_ecalBarrelCells = ROOT.TCanvas('canvas_total_energy_ecalBarrelCells', 'canvas_total_energy_ecalBarrelCells')
fit = th1_total_energy_ecalBarrelCells.Fit('gaus', 'SQ', '', 7, 13)
sigma = fit.Parameter(2)
mean = fit.Parameter(1)
legend = ROOT.TLegend(0.14, 0.60, 0.421, 0.89)
legend.AddEntry(th1_total_energy_ecalBarrelCells,  "Bare Cells", "")
legend.AddEntry(ROOT.nullptr,  '#mu = ' + str(round(mean, 2)), "")
legend.AddEntry(ROOT.nullptr,  '#sigma = ' + str(round(sigma, 2)), "")
th1_total_energy_ecalBarrelCells.Draw()
legend.Draw()
canvas_total_energy_ecalBarrelCells.Print(plot_dir_name+'/total_energy_from_ecalBarrelCells.png')

canvas_total_energy_ecalBarrelswCluster = ROOT.TCanvas('canvas_total_energy_ecalBarrelswCluster', 'canvas_total_energy_ecalBarrelswCluster')
fit = th1_total_energy_ecalBarrelswCluster.Fit('gaus', 'SQ', '', 7, 13)
sigma = fit.Parameter(2)
mean = fit.Parameter(1)
legend = ROOT.TLegend(0.14, 0.60, 0.421, 0.89)
legend.AddEntry(th1_total_energy_ecalBarrelCells,  "Sliding Window", "")
legend.AddEntry(ROOT.nullptr,  '#mu = ' + str(round(mean, 2)), "")
legend.AddEntry(ROOT.nullptr,  '#sigma = ' + str(round(sigma, 2)), "")
th1_total_energy_ecalBarrelswCluster.Draw()
legend.Draw()
canvas_total_energy_ecalBarrelswCluster.Print(plot_dir_name+'/total_energy_from_ecalBarrelswCluster.png')

canvas_total_energy_ecalBarreltopoCluster = ROOT.TCanvas('canvas_total_energy_ecalBarreltopoCluster', 'canvas_total_energy_ecalBarreltopoCluster')
fit = th1_total_energy_ecalBarreltopoCluster.Fit('gaus', 'SQ', '', 7, 13)
sigma = fit.Parameter(2)
mean = fit.Parameter(1)
legend = ROOT.TLegend(0.14, 0.60, 0.421, 0.89)
legend.AddEntry(th1_total_energy_ecalBarrelCells,  "Topo Clusters", "")
legend.AddEntry(ROOT.nullptr,  '#mu = ' + str(round(mean, 2)), "")
legend.AddEntry(ROOT.nullptr,  '#sigma = ' + str(round(sigma, 2)), "")
th1_total_energy_ecalBarreltopoCluster.Draw()
legend.Draw()
canvas_total_energy_ecalBarreltopoCluster.Print(plot_dir_name+'/total_energy_from_ecalBarreltopoCluster.png')

#c = ROOT.TCanvas("canvas1", "",600, 400)
#h = ROOT.TH1F("h_GenParticles_P", ";Primary particle Momentum P; Events", 100, 0 ,20)
#events.Draw("sqrt(pow(GenParticles.core.p4.px,2) + pow(GenParticles.core.p4.py,2) +pow(GenParticles.core.p4.pz,2))>>h_GenParticles_P")
#c.Print(plot_dir_name+'/h_GenParticles_P.png')


