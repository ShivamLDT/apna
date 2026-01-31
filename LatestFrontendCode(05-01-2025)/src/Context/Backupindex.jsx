import React, { createContext, useState } from "react";
// Create and export the context
export const Backupindex = createContext();
export const BackupProvider = ({ children }) => {
  const [backupIndex, setBackupIndex] = useState({ step: 0 });
  const [sourceData, setSourceData] = useState('');
  const [popupEnable, setPopupEnable] = useState(false);
  const [DialogBox, setDialogBox] = useState(false);
  const [folderlist, setfolderlist] = useState(false);
  const [onechecktable, setonechecktable] = useState(true);
  const [onecheckendpointlisttable, setonecheckendpointlisttable] = useState(false);
  const [showEndpointBackup, setShowEndpointBackup] = useState(false);
  const [endpointagentname, setEndpointagentname] = useState("");
  const [CollectFormData, setCollectFormData] = useState();
  const [nextruntimeCheckList, setnextruntimeCheckList] = useState('');
  const [endPointAgentName, setEndPointAgentName] = useState('');
  const [agentNameTable, setAgentNameTable] = useState('');
  const [fileExtensionData, setfileExtensionData] = useState([]);
  const [getRestoreData, setGetRestoreData] = useState('');
  const [showTreePopup, setShowTreePopup] = useState(false);
  const [showLivePopup, setShowLivePopup] = useState(false);
  const [restorePayload, setRestorePayload] = useState('');
  const [restoreTotalData, setRestoreTotalData] = useState(null);
  const [checkBoxData, setCheckBoxData] = useState(true);
  const [errorPopupStoreData, setErrorPopupStoreData] = useState(false);
  const [selectedEndpointName, setSelectedEndpointName] = useState('');
  const [destinationNamePayload, setDestinationNamePayload] = useState('LAN');
  const [itemToDeleteFileExtension, setItemToDeleteFileExtension] = useState('');
  const [reStoreTableData, setReStoreTableData] = useState([])
  const [showRestoreReportTable, setShowRestoreReportTable] = useState(false);
  const [storeMultipleRestoreName, setStoreMultipleRestoreName] = useState([]);
  const [useMultipleRestoreName, setUseMultipleRestoreName] = useState([]);
  const [showLocalLive, setshowLocalLive] = useState(true);
  const [ValdidateRestorePopup, setValdidateRestorePopup] = useState([]);
  const [showTableLive, setshowTableLive] = useState(true);
  const [isBackup, setIsBackup] = useState(false);
  const [isSechduler, setIsSechduler] = useState(false);
  const [checkApi, setCheckApi] = useState(false);
  // const [resultCount, setResultCount] = useState(0);.
  const [resultCount, setResultCount] = useState(0);
  const [openRestorePopup, setOpenRestorePopup] = useState(true);
  const [notificationData, setNotificationData] = useState([]);
  const [showRestoreReportEndPoint, setShowRestoreReportEndPoint] = useState('');
  const [showBackuplog, setShowBackuplog] = useState(false)
  const [jobNotificationName, setJobNotificationName] = useState('')
  const [localShowLocalLive, setlocalShowLocalLive] = useState(true);
  return (
    <Backupindex.Provider value={{ localShowLocalLive, setlocalShowLocalLive, showBackuplog, setShowBackuplog, jobNotificationName, setJobNotificationName, showRestoreReportEndPoint, setShowRestoreReportEndPoint, notificationData, setNotificationData, openRestorePopup, setOpenRestorePopup, resultCount, setResultCount, checkApi, setCheckApi, isSechduler, setIsSechduler, isBackup, setIsBackup, showTableLive, setshowTableLive, ValdidateRestorePopup, setValdidateRestorePopup, showLocalLive, setshowLocalLive, useMultipleRestoreName, setUseMultipleRestoreName, storeMultipleRestoreName, setStoreMultipleRestoreName, showRestoreReportTable, setShowRestoreReportTable, reStoreTableData, setReStoreTableData, itemToDeleteFileExtension, setItemToDeleteFileExtension, destinationNamePayload, setDestinationNamePayload, selectedEndpointName, setSelectedEndpointName, errorPopupStoreData, setErrorPopupStoreData, checkBoxData, setCheckBoxData, restoreTotalData, setRestoreTotalData, restorePayload, setRestorePayload, showLivePopup, setShowLivePopup, showTreePopup, setShowTreePopup, getRestoreData, setGetRestoreData, backupIndex, setBackupIndex, sourceData, setSourceData, popupEnable, setPopupEnable, DialogBox, setDialogBox, folderlist, setfolderlist, onechecktable, setonechecktable, onecheckendpointlisttable, setonecheckendpointlisttable, showEndpointBackup, setShowEndpointBackup, endpointagentname, setEndpointagentname, CollectFormData, setCollectFormData, nextruntimeCheckList, setnextruntimeCheckList, endPointAgentName, setEndPointAgentName, agentNameTable, setAgentNameTable, fileExtensionData, setfileExtensionData }}>
      {children}
    </Backupindex.Provider>
  );
};
