#include "CreateCaloCellPositions.h"

// FCCSW
#include "DetCommon/DetUtils.h"
#include "DetInterface/IGeoSvc.h"

// DD4hep
#include "DD4hep/Detector.h"

// EDM
#include "datamodel/CaloHitCollection.h"
#include "datamodel/PositionedCaloHitCollection.h"
#include "datamodel/PositionedTrackHitCollection.h"
#include "datamodel/TrackHitCollection.h"

DECLARE_COMPONENT(CreateCaloCellPositions)

CreateCaloCellPositions::CreateCaloCellPositions(const std::string& name, ISvcLocator* svcLoc)
    : GaudiAlgorithm(name, svcLoc), m_geoSvc("GeoSvc", name) {
  declareProperty("hits", m_hits, "Hit collection (input)");
  declareProperty("positionsECalBarrelTool", m_cellPositionsECalBarrelTool,
                  "Handle for tool to retrieve cell positions in ECal Barrel");
  declareProperty("positionsHCalBarrelTool", m_cellPositionsHCalBarrelTool,
                  "Handle for tool to retrieve cell positions in HCal Barrel and ext Barrel");
  declareProperty("positionsHCalExtBarrelTool", m_cellPositionsHCalExtBarrelTool,
                  "Handle for tool to retrieve cell positions in HCal Barrel and ext Barrel");
  declareProperty("positionsEMECTool", m_cellPositionsEMECTool, "Handle for tool to retrieve cell positions in EMEC");
  declareProperty("positionsHECTool", m_cellPositionsHECTool, "Handle for tool to retrieve cell positions in HEC");
  declareProperty("positionsEMFwdTool", m_cellPositionsEMFwdTool, "Handle for tool to retrieve cell positions EM Fwd");
  declareProperty("positionsHFwdTool", m_cellPositionsHFwdTool, "Handle for tool to retrieve cell positions Had Fwd");
  declareProperty("positionedHits", m_positionedHits, "Output cell positions collection");
}

int CreateCaloCellPositions::get_system_id(std::string systemName) {
  int detId;
  try { // e.g. FCCee does not have HCalExtBarrel but this tool is used both for FCCee and FCChh
    std::string detId_string = m_geoSvc->lcdd()->constant(systemName).toString(); // I did not find any member of dd4hep::Constant returning the value in a simple way...
    detId = std::stoi(detId_string.substr(detId_string.find(":") + 1, detId_string.length()));
  }
  catch (std::exception) {
      detId = 0;
      debug() << "Could not find " << systemName << " in the DectDimensions.xml. Setting it to 0 (unused)." << endmsg;
  }
  debug() << "System Id for " << systemName << ": " << detId << endmsg;
  return detId;
}

StatusCode CreateCaloCellPositions::initialize() {
  StatusCode sc = GaudiAlgorithm::initialize();
  if (sc.isFailure()) return sc;

  if (!m_geoSvc) {
    error() << "Unable to locate Geometry Service. "
            << "Make sure you have GeoSvc and SimSvc in the right order in the configuration." << endmsg;
    return StatusCode::FAILURE;
  }

  // Retrieve the ID of each detector type to know which cellPositionTool to use when
  //std::string detId_ECAL_Barrel_string = m_geoSvc->lcdd()->constant("DetID_ECAL_Barrel").toString(); // I did not find any member of dd4hep::Constant returning the value in a simple way...
  //m_detId_ECAL_Barrel = std::stoi(detId_ECAL_Barrel_string.substr(detId_ECAL_Barrel_string.find(":") + 1, detId_ECAL_Barrel_string.length()));
  m_detId_ECAL_Barrel = get_system_id("DetID_ECAL_Barrel");
  m_detId_HCalExtBarrel = get_system_id("HCalExtBarrel");

  //std::string detId_HCalBarrel_string = m_geoSvc->lcdd()->constant("").toString(); // I did not find any member of dd4hep::Constant returning the value in a simple way...
  //m_detId_HCalBarrel = std::stoi(detId_HCalBarrel_string.substr(detId_HCalBarrel_string.find(":") + 1, detId_HCalBarrel_string.length()));


  //m_detId_HCalBarrel;
  //m_detId_HCalExtBarrel;
  //m_detId_EMEC;
  //m_detId_HEC;
  //m_detId_EMFwd;
  //m_detId_HFwd;
  return StatusCode::SUCCESS;
}

StatusCode CreateCaloCellPositions::execute() {
  // Get the input hit collection
  const auto* hits = m_hits.get();
  debug() << "Input hit collection size: " << hits->size() << endmsg;
  // Initialize output collection
  auto edmPositionedHitCollection = m_positionedHits.createAndPut();

  for (const auto& hit : *hits) {
    dd4hep::DDSegmentation::CellID cellId = hit.core().cellId;
    // identify calo system
    //auto systemId = std::string(m_decoder->get(cellId, "system"));
    auto systemId = m_decoder->get(cellId, "system");
    dd4hep::Position posCell;

    //if (systemId == m_detId_ECalBarrel.GetTitle())  // ECAL BARREL system id
    if (systemId == m_detId_ECAL_Barrel)  // ECAL BARREL system id
      posCell = m_cellPositionsECalBarrelTool->xyzPosition(cellId);
    else if (systemId == 8)  // HCAL BARREL system id
      posCell = m_cellPositionsHCalBarrelTool->xyzPosition(cellId);
    else if (systemId == 9)  // HCAL EXT BARREL system id
      posCell = m_cellPositionsHCalExtBarrelTool->xyzPosition(cellId);
    else if (systemId == 6)  // EMEC system id
      posCell = m_cellPositionsEMECTool->xyzPosition(cellId);
    else if (systemId == 7)  // HEC system id
      posCell = m_cellPositionsHECTool->xyzPosition(cellId);
    else if (systemId == 10)  // EMFWD system id
      posCell = m_cellPositionsEMFwdTool->xyzPosition(cellId);
    else if (systemId == 11)  // HFWD system id
      posCell = m_cellPositionsHFwdTool->xyzPosition(cellId);

    auto edmPos = fcc::Point();
    edmPos.x = posCell.x() / dd4hep::mm;
    edmPos.y = posCell.y() / dd4hep::mm;
    edmPos.z = posCell.z() / dd4hep::mm;

    auto positionedHit = edmPositionedHitCollection->create(edmPos, hit.core());

    // Debug information about cell position
    debug() << "Cell energy (GeV) : " << hit.core().energy << "\tcellID " << hit.core().cellId << endmsg;
    debug() << "Position of cell (mm) : \t" << posCell.x() / dd4hep::mm << "\t" << posCell.y() / dd4hep::mm << "\t"
            << posCell.z() / dd4hep::mm << endmsg;
  }

  debug() << "Output positions collection size: " << edmPositionedHitCollection->size() << endmsg;
  return StatusCode::SUCCESS;
}

StatusCode CreateCaloCellPositions::finalize() { return GaudiAlgorithm::finalize(); }
