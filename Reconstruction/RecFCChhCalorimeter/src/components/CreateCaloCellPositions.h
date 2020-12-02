#ifndef DETCOMPONENTS_CREATECELLPOSITIONS_H
#define DETCOMPONENTS_CREATECELLPOSITIONS_H

// FCCSW
#include "FWCore/DataHandle.h"
#include "RecInterface/ICellPositionsTool.h"

// Gaudi
#include "GaudiAlg/GaudiAlgorithm.h"
#include "GaudiKernel/ToolHandle.h"

#include "datamodel/CaloHit.h"
#include "datamodel/CaloHitCollection.h"
#include "datamodel/PositionedCaloHit.h"
#include "datamodel/PositionedCaloHitCollection.h"

class IGeoSvc;

namespace dd4hep {
  class Constant;
}

/** @class CreateCaloCellPositions Reconstruction/RecCalorimeter/src/components/CreateCaloCellPositions.h
 * CreateCaloCellPositions.h
 *
 *  Retrieve positions of the cells from cell ID.
 *  This algorithm saves the centre position of the volume. Defined for all Calo-Subsystems within tools.
 *
 *  @author Coralie Neubueser
 *
 */

class CreateCaloCellPositions : public GaudiAlgorithm {

public:
  CreateCaloCellPositions(const std::string& name, ISvcLocator* svcLoc);
  /**  Initialize.
   *   @return status code
   */
  StatusCode initialize();
  /**  Execute.
   *   @return status code
   */
  StatusCode execute();
  /**  Finalize.
   *   @return status code
   */
  StatusCode finalize();

  int get_system_id(std::string systemName);

private:
  /// Handle for tool to get positions in ECal Barrel
  ToolHandle<ICellPositionsTool> m_cellPositionsECalBarrelTool;
  /// Handle for tool to get positions in HCal Barrel and Ext Barrel, no Segmentation
  ToolHandle<ICellPositionsTool> m_cellPositionsHCalBarrelTool;
  /// Handle for tool to get positions in HCal Barrel and Ext Barrel, no Segmentation
  ToolHandle<ICellPositionsTool> m_cellPositionsHCalExtBarrelTool;
  /// Handle for tool to get positions in Calo Discs
  ToolHandle<ICellPositionsTool> m_cellPositionsEMECTool;
  /// Handle for tool to get positions in Calo Discs
  ToolHandle<ICellPositionsTool> m_cellPositionsHECTool;
  /// Handle for tool to get positions in Calo Discs
  ToolHandle<ICellPositionsTool> m_cellPositionsEMFwdTool;
  /// Handle for tool to get positions in Calo Discs
  ToolHandle<ICellPositionsTool> m_cellPositionsHFwdTool;
  /// Decoder for system ID
  dd4hep::DDSegmentation::BitFieldCoder* m_decoder = new dd4hep::DDSegmentation::BitFieldCoder("system:4");
  /// To check which system ID corresponds to which detector
  ServiceHandle<IGeoSvc> m_geoSvc;
  int m_detId_ECAL_Barrel, m_detId_HCAL_Barrel, m_detId_HCalExtBarrel, m_detId_EMEC, m_detId_HEC, m_detId_EMFwd, m_detId_HFwd;
  /// Input collection
  DataHandle<fcc::CaloHitCollection> m_hits{"hits/hits", Gaudi::DataHandle::Reader, this};
  /// Output collection
  DataHandle<fcc::PositionedCaloHitCollection> m_positionedHits{"hits/positionedHits", Gaudi::DataHandle::Writer, this};
};

#endif /* DETCOMPONENTS_CREATECELLPOSITIONS_H */
