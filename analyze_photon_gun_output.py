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
th1_total_energy_ecalBarrelCellsStep2 = ROOT.TH1F("th1_total_energy_ecalBarrelCellsStep2", "th1_total_energy_ecalBarrelCellsStep2", 100, 0, 20)
evt = 0
for event in events:
    if evt >= max_evt:
        break
    barrelHits = event.ECalBarrelPositionedHits
    barrelCells = event.ECalBarrelCellsStep2
    total_energy_barrelHits = 0
    total_energy_barrelCells = 0
    #for barrelHit in barrelHits:
    #    total_energy_barrelHits += barrelHit.core.energy
    for barrelCell in barrelCells:
        total_energy_barrelCells += barrelCell.core.energy
    th1_total_energy_barrelHits.Fill(total_energy_barrelHits)
    th1_total_energy_ecalBarrelCellsStep2.Fill(total_energy_barrelCells)
    if evt % 100 == 0:
        print evt
    evt += 1

canvas_total_energy_barrelHits = ROOT.TCanvas('canvas_total_energy_barrelHits', 'canvas_total_energy_barrelHits')
th1_total_energy_barrelHits.Draw()
canvas_total_energy_barrelHits.Print(plot_dir_name+'/total_energy_from_barrelPositionedHitSum.png')

canvas_total_energy_ecalBarrelCellsStep2 = ROOT.TCanvas('canvas_total_energy_ecalBarrelCellsStep2', 'canvas_total_energy_ecalBarrelCellsStep2')
th1_total_energy_ecalBarrelCellsStep2.Draw()
canvas_total_energy_ecalBarrelCellsStep2.Print(plot_dir_name+'/total_energy_from_ecalBarrelCellsStep2.png')



#c = ROOT.TCanvas("canvas1", "",600, 400)
#h = ROOT.TH1F("h_GenParticles_P", ";Primary particle Momentum P; Events", 100, 0 ,20)
#events.Draw("sqrt(pow(GenParticles.core.p4.px,2) + pow(GenParticles.core.p4.py,2) +pow(GenParticles.core.p4.pz,2))>>h_GenParticles_P")
#c.Print(plot_dir_name+'/h_GenParticles_P.png')


