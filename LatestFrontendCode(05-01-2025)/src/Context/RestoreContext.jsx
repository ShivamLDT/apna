import React, { createContext, useState, useMemo } from "react";

export const RestoreContext = createContext();

export const RestoreProvider = ({ children }) => {
  const [restorePayload, setRestorePayload] = useState("");
  const [restoreTotalData, setRestoreTotalData] = useState(null);
  const [showRestoreReportTable, setShowRestoreReportTable] = useState(false);
  const [reStoreTableData, setReStoreTableData] = useState([]);
  const [storeMultipleRestoreName, setStoreMultipleRestoreName] = useState([]);
  const [useMultipleRestoreName, setUseMultipleRestoreName] = useState([]);
  const [ValdidateRestorePopup, setValdidateRestorePopup] = useState([]);
  const [openRestorePopup, setOpenRestorePopup] = useState(true);
  const [showRestoreReportEndPoint, setShowRestoreReportEndPoint] = useState("");
  const [openSuccessful, setOpenSuccessful] = useState(true);
  const [restoreNameTable, setRestoreNameTable] = useState([])

  const value = useMemo(
    () => ({
      restorePayload, setRestorePayload,
      restoreTotalData, setRestoreTotalData,
      showRestoreReportTable, setShowRestoreReportTable,
      reStoreTableData, setReStoreTableData,
      storeMultipleRestoreName, setStoreMultipleRestoreName,
      useMultipleRestoreName, setUseMultipleRestoreName,
      ValdidateRestorePopup, setValdidateRestorePopup,
      openRestorePopup, setOpenRestorePopup,
      showRestoreReportEndPoint, setShowRestoreReportEndPoint,
      openSuccessful, setOpenSuccessful,
      restoreNameTable, setRestoreNameTable
    }),
    [restorePayload, restoreTotalData, showRestoreReportTable, reStoreTableData,
      storeMultipleRestoreName, useMultipleRestoreName, ValdidateRestorePopup,
      openRestorePopup, showRestoreReportEndPoint, openSuccessful, setOpenSuccessful,
      restoreNameTable, setRestoreNameTable]
  );

  return (
    <RestoreContext.Provider value={value}>
      {children}
    </RestoreContext.Provider>
  );
};
