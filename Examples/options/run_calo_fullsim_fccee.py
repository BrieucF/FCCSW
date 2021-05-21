import os

from GaudiKernel.SystemOfUnits import MeV, GeV, tesla

use_pythia = False

# Parameters for the particle gun simulations, dummy if use_pythia is set to True
momentum = 10 # in GeV
thetaMin = 90.25 # degrees
thetaMax = 90.25 # degrees
pdgCode = 13 # 11 electron, 13 muon, 22 photon, 111 pi0, 211 pi+
magneticField = False

from Gaudi.Configuration import *

from Configurables import FCCDataSvc
podioevent  = FCCDataSvc("EventDataSvc")

################## Particle gun setup
_pi = 3.14159

from Configurables import GenAlg
genAlg = GenAlg()
if use_pythia:
    from Configurables import PythiaInterface
    pythia8gentool = PythiaInterface()
    pythia8gentool.Filename = "MCGeneration/ee_Z_ee.cmd"
    genAlg.SignalProvider = pythia8gentool
else:
    from Configurables import  MomentumRangeParticleGun
    pgun = MomentumRangeParticleGun("ParticleGun_Electron")
    pgun.PdgCodes = [pdgCode]
    pgun.MomentumMin = momentum * GeV
    pgun.MomentumMax = momentum * GeV
    pgun.PhiMin = 0
    pgun.PhiMax = 2 * _pi
    pgun.ThetaMin = thetaMin * _pi / 180.
    pgun.ThetaMax = thetaMax * _pi / 180.
    genAlg.SignalProvider = pgun

genAlg.hepmc.Path = "hepmc"

from Configurables import HepMCToEDMConverter
hepmc_converter = HepMCToEDMConverter()
hepmc_converter.hepmc.Path="hepmc"
genParticlesOutputName = "genParticles"
hepmc_converter.GenParticles.Path = genParticlesOutputName
hepmc_converter.hepmcStatusList = []

################## Simulation setup
# Detector geometry
from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc")
# if FCC_DETECTORS is empty, this should use relative path to working directory
path_to_detector = os.environ.get("FCCDETECTORS", "")
print(path_to_detector)
detectors_to_use=[
                    'Detector/DetFCCeeIDEA-LAr/compact/FCCee_DectMaster.xml',
                    #'Detector/DetFCCeeIDEA/compact/FCCee_DectMaster.xml',
                    #'Detector/DetFCCeeIDEA-LAr/compact/FCCee_DectMaster_original.xml',
                  ]
# prefix all xmls with path_to_detector
geoservice.detectors = [os.path.join(path_to_detector, _det) for _det in detectors_to_use]
geoservice.OutputLevel = INFO
#geoservice.OutputLevel = DEBUG

# Geant4 service
# Configures the Geant simulation: geometry, physics list and user actions
from Configurables import SimG4FullSimActions, SimG4Alg, SimG4PrimariesFromEdmTool, SimG4SaveParticleHistory
actions = SimG4FullSimActions()
actions.enableHistory=True
actions.energyCut = 0.2 * GeV 
saveHistTool = SimG4SaveParticleHistory("saveHistory")


from Configurables import SimG4Svc
#geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist="SimG4FtfpBert", actions="SimG4FullSimActions")
geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist="SimG4FtfpBert", actions=actions)
# To be re-implemented in k4hep, see https://github.com/HEP-FCC/FCCSW/commit/bc8ab83c982ba55a72870b30d96c3726a2098c6d
#geantservice.randomNumbersFromGaudi = False
#geantservice.seedValue = 4242

# Range cut
geantservice.g4PreInitCommands += ["/run/setCut 0.1 mm"]

# Magnetic field
from Configurables import SimG4ConstantMagneticFieldTool
if magneticField == 1:
    field = SimG4ConstantMagneticFieldTool("SimG4ConstantMagneticFieldTool", FieldComponentZ=-2*tesla, FieldOn=True,IntegratorStepper="ClassicalRK4")
else:
    field = SimG4ConstantMagneticFieldTool("SimG4ConstantMagneticFieldTool",FieldOn=False)

# Geant4 algorithm
# Translates EDM to G4Event, passes the event to G4, writes out outputs via tools
# and a tool that saves the calorimeter hits

# Detector readouts
# ECAL
#ecalBarrelReadoutName = "ECalBarrelTheta"
#ecalBarrelReadoutNamePhiTheta = "ECalBarrelPhiTheta"
ecalBarrelReadoutName = "ECalBarrelEta"
ecalBarrelReadoutNamePhiTheta = "ECalBarrelPhiEta"
# HCAL
hcalReadoutName = "HCalBarrelReadout"
extHcalReadoutName = "HCalExtBarrelReadout"

# Configure saving of calorimeter hits
ecalBarrelHitsName = "ECalBarrelPositionedHits"
from Configurables import SimG4SaveCalHits
saveECalBarrelTool = SimG4SaveCalHits("saveECalBarrelHits", readoutNames = [ecalBarrelReadoutName])
saveECalBarrelTool.CaloHits.Path = ecalBarrelHitsName

saveHCalTool = SimG4SaveCalHits("saveHCalBarrelHits", readoutNames = [hcalReadoutName])
saveHCalTool.CaloHits.Path = "HCalBarrelPositionedHits"

# next, create the G4 algorithm, giving the list of names of tools ("XX/YY")
from Configurables import SimG4PrimariesFromEdmTool
particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
particle_converter.GenParticles.Path = genParticlesOutputName

from Configurables import SimG4Alg
geantsim = SimG4Alg("SimG4Alg",
                       outputs= [saveECalBarrelTool,
                                 saveHCalTool,
                                 saveHistTool
                       ],
                       eventProvider=particle_converter,
                       OutputLevel=DEBUG)

############## Digitization (Merging hits into cells, EM scale calibration)
# EM scale calibration (sampling fraction)
from Configurables import CalibrateInLayersTool
calibEcalBarrel = CalibrateInLayersTool("CalibrateECalBarrel",
                                   # sampling fraction obtained using SamplingFractionInLayers from DetStudies package
                                   samplingFraction = [0.303451138049] * 1 + [0.111872504159] * 1 + [0.135806495306] * 1 + [0.151772636618] * 1 + [0.163397436122] * 1 + [0.172566977313] * 1 + [0.179855253903] * 1 + [0.186838417657] * 1 + [0.192865946689] * 1 + [0.197420241611] * 1 + [0.202066552306] * 1 + [0.22646764465] * 1,
                                   readoutName = ecalBarrelReadoutName,
                                   layerFieldName = "layer")

from Configurables import CalibrateCaloHitsTool
calibHcells = CalibrateCaloHitsTool("CalibrateHCal", invSamplingFraction="41.66")

# Create cells in ECal barrel
# 1. step - merge hits into cells with default Theta segmentation
# 2. step - rewrite the cellId using the Phi-Theta segmentation
from Configurables import CreateCaloCells
createEcalBarrelCellsStep1 = CreateCaloCells("CreateECalBarrelCellsStep1",
                               doCellCalibration=True,
                               calibTool = calibEcalBarrel,
                               addCellNoise=False, filterCellNoise=False,
                               OutputLevel=INFO,
                               hits=ecalBarrelHitsName,
                               cells="ECalBarrelCellsStep1")


## Ecal barrel cell positions
##from Configurables import CreateVolumeCaloPositions
##positionsEcalBarrel = CreateVolumeCaloPositions("positionsBarrelEcal", OutputLevel = INFO)
##positionsEcalBarrel.hits.Path = "ECalBarrelCellsStep1"
##positionsEcalBarrel.positionedHits.Path = "ECalBarrelPositions"
## Use Phi-Theta segmentation in ECal barrel
#from Configurables import RedoSegmentation
#resegmentEcalBarrel = RedoSegmentation("ReSegmentationEcal",
#                             # old bitfield (readout)
#                             oldReadoutName = ecalBarrelReadoutName,
#                             # specify which fields are going to be altered (deleted/rewritten)
#                             oldSegmentationIds = ["module"],
#                             # new bitfield (readout), with new segmentation
#                             newReadoutName = ecalBarrelReadoutNamePhiTheta,
#                             OutputLevel = INFO,
#                             inhits = "ECalBarrelPositions",
#                             outhits = "ECalBarrelCellsStep2")
#
#EcalBarrelCellsName = "ECalBarrelCells"
#createEcalBarrelCells = CreateCaloCells("CreateECalBarrelCells",
#                               doCellCalibration=False,
#                               addCellNoise=False, filterCellNoise=False,
#                               OutputLevel=INFO,
#                               hits="ECalBarrelCellsStep2",
#                               cells=EcalBarrelCellsName)
#
## Ecal barrel cell positions (good for physics, all coordinates set properly)
#from Configurables import CellPositionsECalBarrelTool
#cellPositionEcalBarrelTool = CellPositionsECalBarrelTool("CellPositionsECalBarrel", readoutName = ecalBarrelReadoutNamePhiTheta, OutputLevel = INFO)
#
#from Configurables import CreateCaloCellPositionsFCCee
#createEcalBarrelPositionedCells = CreateCaloCellPositionsFCCee("ECalBarrelPositionedCells", OutputLevel = INFO)
#createEcalBarrelPositionedCells.positionsECalBarrelTool = cellPositionEcalBarrelTool
#createEcalBarrelPositionedCells.hits.Path = "ECalBarrelCells"
#createEcalBarrelPositionedCells.positionedHits.Path = "ECalBarrelPositionedCells"
#
## Create cells in HCal
## 1. step - merge hits into cells with the default readout
#createHcalBarrelCells = CreateCaloCells("CreateHCaloCells",
#                               doCellCalibration=True,
#                               calibTool=calibHcells,
#                               addCellNoise = False, filterCellNoise = False,
#                               OutputLevel = INFO,
#                               hits="HCalBarrelHits",
#                               cells="HCalBarrelCells")
#
## sliding window clustering
##Empty cells for parts of calorimeter not implemented yet
#from Configurables import CreateEmptyCaloCellsCollection
#createemptycells = CreateEmptyCaloCellsCollection("CreateEmptyCaloCells")
#createemptycells.cells.Path = "emptyCaloCells"
#
#from Configurables import CaloTowerTool
#towers = CaloTowerTool("towers",
#                               deltaEtaTower = 0.01, deltaPhiTower = 2*_pi/768.,
#                               ecalBarrelReadoutName = ecalBarrelReadoutNamePhiTheta,
#                               ecalEndcapReadoutName = "",
#                               ecalFwdReadoutName = "",
#                               hcalBarrelReadoutName = "",
#                               hcalExtBarrelReadoutName = "",
#                               hcalEndcapReadoutName = "",
#                               hcalFwdReadoutName = "",
#                               OutputLevel = INFO)
#towers.ecalBarrelCells.Path = EcalBarrelCellsName
#towers.ecalEndcapCells.Path = "emptyCaloCells"
#towers.ecalFwdCells.Path = "emptyCaloCells"
#towers.hcalBarrelCells.Path = "emptyCaloCells"
#towers.hcalExtBarrelCells.Path = "emptyCaloCells"
#towers.hcalEndcapCells.Path = "emptyCaloCells"
#towers.hcalFwdCells.Path = "emptyCaloCells"
#
## Cluster variables
#windE = 9
#windP = 17
#posE = 5
#posP = 11
#dupE = 7
#dupP = 13
#finE = 9
#finP = 17
## approx in GeV: changed from default of 12 in FCC-hh
#threshold = 0.1
#
#from Configurables import CreateCaloClustersSlidingWindow
#createClusters = CreateCaloClustersSlidingWindow("CreateClusters",
#                                                 towerTool = towers,
#                                                 nEtaWindow = windE, nPhiWindow = windP,
#                                                 nEtaPosition = posE, nPhiPosition = posP,
#                                                 nEtaDuplicates = dupE, nPhiDuplicates = dupP,
#                                                 nEtaFinal = finE, nPhiFinal = finP,
#                                                 energyThreshold = threshold,
#                                                 #attachCells = True,
#                                                 OutputLevel = INFO
#                                                 )
#createClusters.clusters.Path = "CaloClusters"
##createClusters.clusterCells.Path = "CaloClusterCells"
#
#createEcalBarrelPositionedCaloClusterCells = CreateCaloCellPositionsFCCee("ECalBarrelPositionedCaloClusterCells", OutputLevel = INFO)
#createEcalBarrelPositionedCaloClusterCells.positionsECalBarrelTool = cellPositionEcalBarrelTool
#createEcalBarrelPositionedCaloClusterCells.hits.Path = "CaloClusterCells"
#createEcalBarrelPositionedCaloClusterCells.positionedHits.Path = "PositionedCaloClusterCells"
################ Output
from Configurables import PodioOutput
out = PodioOutput("out",
                  OutputLevel=INFO)

#out.outputCommands = ["keep *", "drop ECalBarrelHits", "drop HCal*", "drop ECalBarrelCellsStep*", "drop emptyCaloCells"]
out.outputCommands = ["keep *"]
#out.outputCommands = ["keep *", "drop ECalBarrelHits", "drop HCal*", "drop ECalBarrelCellsStep*", "drop ECalBarrelPositionedHits", "drop ECalBarrelPositions", "drop emptyCaloCells", "drop CaloClusterCells"]

import uuid
out.filename = "output_fullCalo_SimAndDigi_withCluster_MagneticField_"+str(magneticField)+"_pMin_"+str(momentum*1000)+"_MeV"+"_ThetaMinMax_"+str(thetaMin)+"_"+str(thetaMax)+"_pdgId_"+str(pdgCode)+"_pythia"+str(use_pythia)+".root"

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
genAlg.AuditExecute = True
hepmc_converter.AuditExecute = True
geantsim.AuditExecute = True
createEcalBarrelCellsStep1.AuditExecute = True
##positionsEcalBarrel.AuditExecute = True
#resegmentEcalBarrel.AuditExecute = True
#createEcalBarrelCells.AuditExecute = True
#createHcalBarrelCells.AuditExecute = True
out.AuditExecute = True

from Configurables import EventCounter
event_counter = EventCounter('event_counter')
event_counter.Frequency = 10

from Configurables import ApplicationMgr
ApplicationMgr(
    TopAlg = [
              event_counter,
              genAlg,
              hepmc_converter,
              geantsim,
              createEcalBarrelCellsStep1,
              #positionsEcalBarrel,
              #resegmentEcalBarrel,
              #createEcalBarrelCells,
              #createEcalBarrelPositionedCells,
              ##createHcalBarrelCells,
              #createemptycells,
              #createClusters,
              #createEcalBarrelPositionedCaloClusterCells,
              out
              ],
    EvtSel = 'NONE',
    EvtMax   = 10000,
    ExtSvc = [geoservice, podioevent, geantservice, audsvc],
    StopOnSignal = True,
 )
