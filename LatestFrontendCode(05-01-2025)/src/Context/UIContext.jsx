import React, { createContext, useState, useMemo } from "react";

export const UIContext = createContext();

export const UIProvider = ({ children }) => {
  const [popupEnable, setPopupEnable] = useState(false);
  const [DialogBox, setDialogBox] = useState(false);
  const [folderlist, setfolderlist] = useState(false);
  const [onechecktable, setonechecktable] = useState(true);
  const [onecheckendpointlisttable, setonecheckendpointlisttable] = useState(false);
  const [showEndpointBackup, setShowEndpointBackup] = useState(false);
  const [showTreePopup, setShowTreePopup] = useState(false);
  const [showLivePopup, setShowLivePopup] = useState(false);
  const [showLocalLive, setshowLocalLive] = useState(true);
  const [showTableLive, setshowTableLive] = useState(true);
  const [showBackuplog, setShowBackuplog] = useState(false);
  const [localShowLocalLive, setlocalShowLocalLive] = useState(true);

  const value = useMemo(
    () => ({
      popupEnable, setPopupEnable,
      DialogBox, setDialogBox,
      folderlist, setfolderlist,
      onechecktable, setonechecktable,
      onecheckendpointlisttable, setonecheckendpointlisttable,
      showEndpointBackup, setShowEndpointBackup,
      showTreePopup, setShowTreePopup,
      showLivePopup, setShowLivePopup,
      showLocalLive, setshowLocalLive,
      showTableLive, setshowTableLive,
      showBackuplog, setShowBackuplog,
      localShowLocalLive, setlocalShowLocalLive
    }),
    [popupEnable, DialogBox, folderlist, onechecktable, onecheckendpointlisttable,
     showEndpointBackup, showTreePopup, showLivePopup, showLocalLive, 
     showTableLive, showBackuplog, localShowLocalLive]
  );

  return (
    <UIContext.Provider value={value}>
      {children}
    </UIContext.Provider>
  );
};
