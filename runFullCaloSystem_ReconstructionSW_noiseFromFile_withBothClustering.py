# Setup
# Names of cells collections
ecalBarrelCellsName = "ECalBarrelCells"
# Readouts
ecalBarrelReadoutName = "ECalBarrelPhiEta"
ecalEndcapReadoutName = "EMECPhiEtaReco" 
ecalFwdReadoutName = "EMFwdPhiEtaReco"
#HCAL readouts
hcalBarrelReadoutName = "HCalBarrelReadout" 
hcalExtBarrelReadoutName ="HCalExtBarrelReadout" 
#hcalExtBarrelReadoutName ="HCalBarrelReadout" 
hcalEndcapReadoutName = "HECPhiEtaReco" 
hcalFwdReadoutName = "HFwdPhiEtaReco"

# Number of events
num_events = 10

from Gaudi.Configuration import *
from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput
import sys

podioevent = FCCDataSvc("EventDataSvc")
#podioevent.input="/opt/fcc/repo/FCCeeLArStudy/ShowerDisplay/fccee_samplingFraction_inclinedEcal.root"
import glob
podioevent.inputs=glob.glob("output_fullCalo_SimAndDigi_*.root")
# reads HepMC text file and write the HepMC::GenEvent to the data service
from Configurables import PodioInput
podioinput = PodioInput("PodioReader",
                        collections = [ecalBarrelCellsName,
                                       # ecalEndcapCellsName, ecalFwdCellsName,
                                       #hcalBarrelCellsName, hcalExtBarrelCellsName, hcalEndcapCellsName, hcalFwdCellsName,
                                       "GenParticles",
                                       ])


from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc")
# if FCC_DETECTORS is empty, this should use relative path to working directory
path_to_detector = os.environ.get("FCC_DETECTORS", "")
detectors_to_use=[
                    'Detector/DetFCCeeIDEA-LAr/compact/FCCee_DectMaster.xml',
                    #'Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml'
                    #'Detector/DetFCCeeIDEA-LAr/compact/FCCee_DectEmptyMaster.xml',
                    'Detector/DetFCCeeECalInclined/compact/FCCee_ECalBarrel_withCryostat.xml',
                  ]
# prefix all xmls with path_to_detector
geoservice.detectors = [os.path.join(path_to_detector, _det) for _det in detectors_to_use]
geoservice.OutputLevel = WARNING


ecalBarrelNoisePath = "http://fccsw.web.cern.ch/fccsw/testsamples/elecNoise_ecalBarrelFCCee_50Ohm_traces1_4shieldWidth.root"
ecalBarrelNoiseHistName = "h_elecNoise_fcc_"

# add noise, create all existing cells in detector
from Configurables import NoiseCaloCellsFromFileTool, TubeLayerPhiEtaCaloTool,CreateCaloCells
#noiseBarrel = NoiseCaloCellsFromFileTool("NoiseBarrel",
#                                         readoutName = ecalBarrelReadoutName,
#                                         noiseFileName = ecalBarrelNoisePath,
#                                         elecNoiseHistoName = ecalBarrelNoiseHistName,
#                                         activeFieldName = "layer",
#                                         addPileup = False,
#                                         numRadialLayers = 8)
barrelGeometry = TubeLayerPhiEtaCaloTool("EcalBarrelGeo",
                                         readoutName = ecalBarrelReadoutName,
                                         activeVolumeName = "LAr_sensitive",
                                         activeFieldName = "layer",
                                         fieldNames = ["system"],
                                         fieldValues = [5],
                                         activeVolumesNumber = 8)
#createEcalBarrelCells = CreateCaloCells("CreateECalBarrelCells",
#                                        geometryTool = barrelGeometry,
#                                        doCellCalibration=False, # already calibrated
#                                        addCellNoise=True, filterCellNoise=False,
#                                        noiseTool = noiseBarrel,
#                                        hits=ecalBarrelCellsName,
#                                        cells=ecalBarrelCellsName+"Noise",
#                                        OutputLevel=INFO)

from Configurables import CreateEmptyCaloCellsCollection
createemptycells =CreateEmptyCaloCellsCollection("CreateEmptyCaloCells")
createemptycells.cells.Path = "emptyCaloCells"

#Create calo clusters with sliding window
from Configurables import CreateCaloClustersSlidingWindow
from GaudiKernel.PhysicalConstants import pi

from Configurables import CaloTowerTool
towers = CaloTowerTool("towers",
                               deltaEtaTower = 0.01, deltaPhiTower = 2*pi/704.,
                               ecalBarrelReadoutName = ecalBarrelReadoutName,
                               #ecalEndcapReadoutName = ecalEndcapReadoutName,
                               #ecalFwdReadoutName = ecalFwdReadoutName,
                               #hcalBarrelReadoutName = hcalBarrelReadoutPhiEtaName,
                               #hcalExtBarrelReadoutName = hcalExtBarrelReadoutPhiEtaName,
                               #hcalEndcapReadoutName = hcalEndcapReadoutName,
                               #hcalFwdReadoutName = hcalFwdReadoutName,
                               OutputLevel = INFO)

# Needed for the clustering algorithm otherwise it crashes
towers.ecalBarrelCells.Path = ecalBarrelCellsName
#towers.ecalBarrelCells.Path = ecalBarrelCellsName + "Noise"
towers.ecalEndcapCells.Path = "emptyCaloCells" #ecalEndcapCellsName + "Noise"
towers.ecalFwdCells.Path = "emptyCaloCells" #ecalFwdCellsName
towers.hcalBarrelCells.Path = "emptyCaloCells"
towers.hcalExtBarrelCells.Path = "emptyCaloCells" # "newHCalExtBarrelCells"
towers.hcalEndcapCells.Path = "emptyCaloCells" #hcalEndcapCellsName
towers.hcalFwdCells.Path = "emptyCaloCells" #hcalFwdCellsName

# Cluster variables
windE = 9
windP = 17
posE = 5
posP = 11
dupE = 7
dupP = 13
finE = 9
finP = 17
# approx in GeV: changed from default of 12 in FCC-hh
threshold = 2

createClusters = CreateCaloClustersSlidingWindow("CreateClusters",
                                                 towerTool = towers,
                                                 nEtaWindow = windE, nPhiWindow = windP,
                                                 nEtaPosition = posE, nPhiPosition = posP,
                                                 nEtaDuplicates = dupE, nPhiDuplicates = dupP,
                                                 nEtaFinal = finE, nPhiFinal = finP,
                                                 energyThreshold = threshold)
createClusters.clusters.Path = "CaloClusters"

#Configure tools for calo cell positions
from Configurables import CellPositionsECalBarrelTool,CellPositionsHCalBarrelNoSegTool, CellPositionsCaloDiscsTool
ECalBcells = CellPositionsECalBarrelTool(
    "CellPositionsECalBarrel", readoutName = ecalBarrelReadoutName, OutputLevel = INFO)
EMECcells = CellPositionsCaloDiscsTool(
    "CellPositionsEMEC", readoutName = ecalEndcapReadoutName, OutputLevel = INFO)
ECalFwdcells = CellPositionsCaloDiscsTool(
    "CellPositionsECalFwd", readoutName = ecalFwdReadoutName, OutputLevel = INFO)
HCalBcells = CellPositionsHCalBarrelNoSegTool("CellPositionsHCalBarrelVols",
                                              readoutName = hcalBarrelReadoutName,
                                              OutputLevel = INFO) 
HCalExtBcells =CellPositionsHCalBarrelNoSegTool("CellPositionsHCalExtBarrel",
                                                readoutName = hcalExtBarrelReadoutName,
                                                OutputLevel = INFO) 
HECcells =CellPositionsCaloDiscsTool("CellPositionsHEC",
                                     readoutName = hcalEndcapReadoutName,
                                     OutputLevel = INFO) 
HCalFwdcells =CellPositionsCaloDiscsTool("CellPositionsHCalFwd",
                                         readoutName = hcalFwdReadoutName,
                                         OutputLevel = INFO)

#Create calo clusters with topo clustering
from Configurables import CaloTopoClusterInputTool,CaloTopoCluster, TopoCaloNeighbours, TopoCaloNoisyCells
createTopoInput = CaloTopoClusterInputTool("CreateTopoInput",
                                           ecalBarrelReadoutName = ecalBarrelReadoutName,
                                           ecalEndcapReadoutName = "",
                                           ecalFwdReadoutName = "",
                                           hcalBarrelReadoutName = hcalBarrelReadoutName,
                                           hcalExtBarrelReadoutName = "",
                                           hcalEndcapReadoutName = "",
                                           hcalFwdReadoutName = "",
                                           OutputLevel = INFO)
createTopoInput.ecalBarrelCells.Path = ecalBarrelCellsName 
createTopoInput.ecalEndcapCells.Path ="emptyCaloCells" 
createTopoInput.ecalFwdCells.Path ="emptyCaloCells" 
createTopoInput.hcalBarrelCells.Path = "emptyCaloCells" 
createTopoInput.hcalExtBarrelCells.Path ="emptyCaloCells" 
createTopoInput.hcalEndcapCells.Path ="emptyCaloCells" 
createTopoInput.hcalFwdCells.Path = "emptyCaloCells"

readNeighboursMap =TopoCaloNeighbours("ReadNeighboursMap",
                                      fileName = "http://fccsw.web.cern.ch/fccsw/testsamples/calo/neighbours_map_segHcal.root",
                                      OutputLevel = INFO)

#Thresholds estimated from atlas, without noise !!!
readNoisyCellsMap = TopoCaloNoisyCells(
    "ReadNoisyCellsMap",
    fileName =
    "http://fccsw.web.cern.ch/fccsw/testsamples/calo/cellNoise_map_segHcal_constNoiseLevel.root",
    OutputLevel = INFO)

createTopoClusters = CaloTopoCluster("CreateTopoClusters",
                                     TopoClusterInput = createTopoInput,
                                     #expects neighbours map from cellid->vec < neighbourIds >
                                     neigboursTool = readNeighboursMap,
                                     #tool to get noise level per cellid
                                     noiseTool = readNoisyCellsMap,
                                     #cell positions tools for all sub - systems
                                     positionsECalBarrelTool = ECalBcells,
                                     positionsHCalBarrelTool = HCalBcells,
                                     positionsHCalExtBarrelTool = HCalExtBcells,
                                     positionsEMECTool = EMECcells,
                                     positionsHECTool = HECcells,
                                     positionsEMFwdTool = ECalFwdcells,
                                     positionsHFwdTool = HCalFwdcells,
                                     seedSigma = 4,
                                     neighbourSigma = 0,
                                     lastNeighbourSigma = 0,
                                     OutputLevel = DEBUG) 
createTopoClusters.clusters.Path ="caloClustersBarrel" 
createTopoClusters.clusterCells.Path = "caloClusterBarrelCells"

#Fill a collection of CaloHitPositions for detailed Cluster analysis
from Configurables import CreateCaloCellPositions 
positionsClusterBarrel = CreateCaloCellPositions("positionsClusterBarrel",
                                                 positionsECalBarrelTool = ECalBcells,
                                                 positionsHCalBarrelTool = HCalBcells,
                                                 positionsHCalExtBarrelTool = HCalExtBcells,
                                                 positionsEMECTool = EMECcells,
                                                 positionsHECTool = HECcells,
                                                 positionsEMFwdTool = ECalFwdcells,
                                                 positionsHFwdTool = HCalFwdcells,
                                                 hits = "caloClusterBarrelCells",
                                                 positionedHits = "caloClusterBarrelCellPositions",
                                                 OutputLevel = INFO)

import uuid
out = PodioOutput("out", filename="output_allCalo_reco_noise_new3" + uuid.uuid4().hex + ".root")
out.outputCommands = ["keep *"]

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
podioinput.AuditExecute = True
createClusters.AuditExecute = True
out.AuditExecute = True

ApplicationMgr(
    TopAlg = [podioinput,
              #rewriteECalEC,
              createemptycells,
              #createEcalBarrelCells,
              #createEcalEndcapCells,
              createClusters,
              createTopoClusters,
              positionsClusterBarrel,
              out
              ],
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [podioevent, geoservice])
