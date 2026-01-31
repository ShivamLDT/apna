import "./RestoreBackupModel.css";
import { useEffect, useState, useContext } from "react";
import { Backupindex } from "../../../Context/Backupindex";
import config from "../../../config";
import useSaveLogs from "../../../Hooks/useSaveLogs";
import axios from "axios";
import { sendNotification } from '../../../Hooks/useNotification';
import axiosInstance from "../../../axiosinstance";
import { NotificationContext } from "../../../Context/NotificationContext";
import { RestoreContext } from "../../../Context/RestoreContext";
import { UIContext } from "../../../Context/UIContext";
import { useNavigate } from "react-router-dom";
import LoadingComponent from "../../../LoadingComponent";
const RestoreData = ({ progressPopupData, setShowProgress, setShowRestorePopup, reStoreName }) => {
  const [storeData, setStoreData] = useState({});
  const [expandedPaths, setExpandedPaths] = useState({});
  const [selectedPaths, setSelectedPaths] = useState([]);
  const [loadingBar, setLoadingBar] = useState(true);
  const { setSourceData, } = useContext(Backupindex);
  const [restoreDataCollect, setRestoreDataCollect] = useState(null);
  const { setNotificationData, resultCount, setResultCount } = useContext(NotificationContext)
  const { userName, profilePic, userRole, handleLogsSubmit } = useSaveLogs();
  const { restorePayload, restoreTotalData, reStoreTableData, setReStoreTableData, setStoreMultipleRestoreName, ValdidateRestorePopup, setValdidateRestorePopup, openRestorePopup, setOpenRestorePopup } = useContext(RestoreContext);
  const { showLivePopup, setShowLivePopup, setshowLocalLive, setlocalShowLocalLive, localShowLocalLive, } = useContext(UIContext)
  const [searchTerm, setSearchTerm] = useState("");
  const [autoExpandedPaths, setAutoExpandedPaths] = useState({});
  const [filteredTree, setFilteredTree] = useState(storeData);
  const [showConfirmPopup, setShowConfirmPopup] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (reStoreTableData.length > 0 && openRestorePopup) {
      if (resultCount == reStoreTableData.length) {
        setShowLivePopup(false);
        setShowProgress(false);
        setOpenRestorePopup(false);
      }
    }
  }, [reStoreTableData]);

  useEffect(() => {
    setStoreData(progressPopupData);
    if (progressPopupData) {
      setLoadingBar(false);
    }

  }, [progressPopupData]);

  const toggleExpand = (path) => {
    setExpandedPaths((prev) => ({
      ...prev,
      [path]: !prev[path],
    }));
  };

  const isFolderPath = (path) => {
    const node = findNodeByPath(storeData, path);
    return node?.type === "folder";
  };

  const getSelectedItemsOnly = () => {
    return selectedPaths.filter((path) => {
      // Check if this path has a selected ancestor
      return !hasSelectedAncestor(path);
    });
  };

  function HandleRestore() {
    setShowLivePopup(false);
    setResultCount(resultCount + 1);
    setlocalShowLocalLive(false);
    setStoreMultipleRestoreName((prev) => [...prev, restoreTotalData?.name]);

    const { RestoreLocation, action, agentName, id, selectedExtensions, storageType, targetAgentName, targetLocation } = restorePayload;
    setValdidateRestorePopup((prev) => [...prev, [reStoreName, RestoreLocation, targetAgentName, id]]);

    const selectedItems = getSelectedItemsOnly();
    const selectedFolders = selectedItems.filter((path) => isFolderPath(path));
    const selectedFiles = selectedItems.filter((path) => !isFolderPath(path));

    const obj = {
      RestoreLocation,
      action,
      agentName,
      id,
      selectedExtensions,
      // selectedFiles: selectedPaths.filter((p) => !isFolderPath(p)),
      // selectedFiles: selectedPaths,
      sourceLocation: null,
      storageType,
      targetAgentName,
      targetLocation
    };

    // if (selectedFolders.length > 0) {
    //   if (selectedFolders === 'C{{DRIVE}}') {
    //     obj.selectedFolder = null;
    //   };
    //   obj.selectedFolder = null;
    // }

    if (selectedFolders.length > 0) {
      const isOnlyRootDrive = selectedFolders.length === 1 && /^[A-Z]\{\{DRIVE\}\}$/.test(selectedFolders[0]);
      obj.selectedFolder = isOnlyRootDrive ? null : selectedFolders;
    }


    if (selectedFiles.length > 0) {
      obj.selectedFiles = selectedFiles;
    }


    const Notification_local_Data = {
      id: Date.now(),
      message: `⏳ Restore started: ${reStoreName} on ${targetAgentName} at ${RestoreLocation}`,
      timestamp: new Date(),
      isRead: false,
    };
    sendNotification(`⏳ Restore started: ${reStoreName} on ${targetAgentName} at ${RestoreLocation}`)
    setNotificationData((prev) => [...prev, Notification_local_Data]);

    const restoreRequest = async () => {
      try {
        const accessToken = localStorage.getItem("accessToken");

        const response = await axiosInstance.post(`${config.API.Server_URL}/restore`, obj, {
          headers: {
            "Content-Type": "application/json",
            token: accessToken,
          },
        });

        const data = response?.data;
        setRestoreDataCollect(data);
        setReStoreTableData((prev) => [data, ...prev]);

        // API contract: 200 = request processed. Check result for per-file outcome (restore: "success" | "failed").
        const resultList = data?.result;
        const failedItem = Array.isArray(resultList) ? resultList.find((r) => r?.restore === "failed") : null;
        if (failedItem?.reason) {
          // 200 but restore failed (e.g. client error) – show actual reason
          const msg = failedItem.reason;
          sendNotification(`❌ Restore Failed: ${reStoreName} - ${msg}`);
          setNotificationData((prev) => [...prev, { id: Date.now(), message: `❌ Restore Failed: ${reStoreName} - ${msg}`, timestamp: new Date(), isRead: false }]);
        } else {
          const downloadEvent = `✅ Backup:${restoreTotalData?.name} is restored on ${targetAgentName} at ${RestoreLocation}`;
          handleLogsSubmit(downloadEvent);
          sendNotification(downloadEvent);
        }
      } catch (error) {
        console.error("Error:", error);

        // ✅ Create error object – prefer reason from API (client restore failure) over generic message
        const apiReason = error.response?.data?.result?.[0]?.reason || error.response?.data?.reason;
        const errorData = {
          error: true,
          message: apiReason || error.response?.data?.message || error.message || "Restore request failed",
          jobName: reStoreName,
          statusCode: error.response?.status || 500
        };

        // ✅ Add error to reStoreTableData
        setReStoreTableData((prev) => [{
          result: [],
          error: true,
          message: errorData.message,
          jobName: reStoreName,
          id: id
        }, ...prev]);

        // ✅ Send error notification
        const errorNotification = {
          id: Date.now(),
          message: `❌ Restore Failed: ${reStoreName} - ${errorData.message}`,
          timestamp: new Date(),
          isRead: false,
        };
        sendNotification(`❌ Restore Failed: ${reStoreName} - ${errorData.message}`);
        setNotificationData((prev) => [...prev, errorNotification]);
      }
    };

    restoreRequest();

    setShowProgress(false);
    setOpenRestorePopup(false);

    navigate("/progress", { state: { tab: "Restore" } })

  }

  const getAllChildrenPaths = (node) => {
    let paths = [];

    if (!node || !node.children) return paths;

    Object.values(node.children).forEach((child) => {
      paths.push(child.path);

      if (child.type === "folder") {
        paths = [...paths, ...getAllChildrenPaths(child)];
      }
    });

    return paths;
  };

  const findNodeByPath = (node, targetPath) => {
    if (!node || !node.children) return null;

    for (const child of Object.values(node.children)) {
      if (child.path === targetPath) return child;
      if (child.type === "folder") {
        const found = findNodeByPath(child, targetPath);
        if (found) return found;
      }
    }

    return null;
  };

  const findAncestorPaths = (node, targetPath, parents = []) => {
    if (!node || !node.children) return null;

    for (const child of Object.values(node.children)) {
      if (child.path === targetPath) {
        return parents.slice();
      }
      if (child.type === "folder") {
        parents.push(child.path);
        const res = findAncestorPaths(child, targetPath, parents);
        if (res) return res;
        parents.pop();
      }
    }
    return null;
  };

  const hasSelectedAncestor = (path) => {
    const ancestors = findAncestorPaths(storeData, path) || [];
    return ancestors.some((ancestorPath) => selectedPaths.includes(ancestorPath));
  };



  const handleCheckboxChange = (path, checked) => {
    const node = findNodeByPath(storeData, path);

    let allChildPaths = [];
    if (node?.type === "folder") {
      allChildPaths = getAllChildrenPaths(node);
    }

    setSelectedPaths((prev) => {
      if (checked) {
        return [...new Set([...prev, path, ...allChildPaths])];
      } else {
        return prev.filter(
          (p) => p !== path && !allChildPaths.includes(p)
        );
      }
    });
  };


  const filterTree = (node, query, parentPath = "", expanded = {}) => {
    if (!node || !node.children) return { node: null, expanded };

    if (!query.trim()) {
      return { node, expanded: {} }; // reset expand when search empty
    }

    const filteredChildren = {};

    for (const [name, item] of Object.entries(node.children)) {
      const isMatch = name.toLowerCase().includes(query.toLowerCase());
      const fullPath = item.path;

      if (item.type === "folder") {
        const { node: subTree, expanded: subExpanded } =
          filterTree(item, query, fullPath, expanded);

        Object.assign(expanded, subExpanded);

        if (isMatch || (subTree && subTree.children && Object.keys(subTree.children).length > 0)) {
          filteredChildren[name] = subTree || item;
          expanded[fullPath] = true; // expand matching folder
        }
      } else if (isMatch) {
        filteredChildren[name] = item;
        expanded[parentPath] = true; // expand parent
      }
    }

    return { node: { ...node, children: filteredChildren }, expanded };
  };

  const renderTree = (node, depth = 0) => {
    if (!node || !node.children) return null;

    return Object.entries(node.children).map(([name, item]) => {
      const isFolder = item.type === "folder";

      // 🔹 If searching, force expand matched branches
      const isForcedExpanded = autoExpandedPaths[item.path];
      const isExpanded = searchTerm ? isForcedExpanded : expandedPaths[item.path];

      const isChecked = selectedPaths.includes(item.path);

      const highlight = searchTerm && name.toLowerCase().includes(searchTerm.toLowerCase());

      return (
        <div key={item.path}>
          <div className="tree-item" style={{ paddingLeft: `${depth * 20}px` }}>
            <input
              type="checkbox"
              checked={isChecked}
              disabled={hasSelectedAncestor(item.path)}
              onChange={(e) => handleCheckboxChange(item.path, e.target.checked)}
            />

            {isFolder && (
              <span
                className={`expand-icon ${isExpanded ? "expanded" : "collapsed"}`}
                onClick={() => {
                  if (!searchTerm) toggleExpand(item.path);
                }}
                style={{ cursor: "pointer", marginRight: "5px" }}
              ></span>
            )}

            <span className="item-icon">{isFolder ? "📁" : "📄"}</span>

            {/* 🔹 Highlight matched text */}
            <span
              className="item-name"
              style={{
                background: highlight ? "yellow" : "transparent",
                borderRadius: "4px",
              }}
            >
              {name}
            </span>
          </div>

          {isFolder && isExpanded && renderTree(item, depth + 1)}
        </div>
      );
    });
  };


  function handlecross() {
    setShowProgress(false);
    setShowRestorePopup(true);
  }

  const noDataAvailable = storeData && storeData.children && Object.keys(storeData.children).length === 0;
  const disableRestore = loadingBar || noDataAvailable;

  // const filteredTree = filterTree(storeData, searchTerm);

  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredTree(storeData);
      setAutoExpandedPaths({});
      return;
    }

    const { node, expanded } = filterTree(storeData, searchTerm);
    setFilteredTree(node);
    setAutoExpandedPaths(expanded);

  }, [searchTerm, storeData]);

  return (
    <div className="dialog-container">
      <div className="dialog">
        <div className="dialog-header">
          <h2 className="dialog-title">Select Data For Restore</h2>
          <button className="close-btn" onClick={handlecross}>&times;</button>
        </div>
        <div className="search-container">
          <div className="search-box">
            <input
              type="text"
              className="search-input"
              placeholder="Search folders and files..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

            <div className="search-icon2">🔍</div>
          </div>
        </div>

        {!loadingBar ? <>
          <div
            className="folder-tree"
            style={{ maxHeight: "350px", overflowY: "auto", padding: "10px" }}
          >
            {/* {storeData && storeData.children && Object.keys(storeData.children).length > 0 ? (
              renderTree(storeData)
            ) : (
              <div style={{ textAlign: "center", color: "#888" }}>No results found</div>
            )} */}


            {filteredTree && filteredTree.children && Object.keys(filteredTree.children).length > 0 ? (
              renderTree(filteredTree)
            ) : (
              <div style={{ textAlign: "center", color: "#888" }}>No results found</div>
            )}


          </div>

          <div className="dialog-footer">
            <div className="selected-info" id="selectedInfo">
              {selectedPaths.length} item(s) selected
            </div>
            <div className="footer-buttons">
              <button
                className="save-btn2"
                // onClick={HandleRestore}
                onClick={() => setShowConfirmPopup(true)}
                disabled={disableRestore}
                style={{
                  opacity: disableRestore ? 0.5 : 1,
                  cursor: disableRestore ? "not-allowed" : "pointer",
                }}
              >
                Restore
              </button>
            </div>
          </div>
        </> :
          // <div className="flex items-center justify-center h-full">
          //   <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
          //     <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
          //       style={{ animation: 'oceanSlide 3s infinite' }} />
          //     <style>{`
          //           @keyframes oceanSlide {
          //             0% { transform: translateX(-150%); }
          //             66% { transform: translateX(0%); }
          //             100% { transform: translateX(150%); }
          //           }
          //         `}</style>
          //   </div>
          // </div>

          <LoadingComponent />
        }
      </div>
      {showConfirmPopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-96">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              Are you sure?
            </h3>

            <p className="text-gray-600 mb-4 text-justify">
              During data restoration, if the same file name or folder name already exists at the restore location, it will be overwritten. <br />
              Type <span className="font-bold text-red-600">Proceed</span> to continue restore operation.
            </p>

            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              placeholder="Type Proceed here..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <div className="flex justify-end space-x-3 mt-6">
              <button
                className="px-4 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400"
                onClick={() => {
                  setShowConfirmPopup(false);
                  setConfirmText("");
                }}
              >
                Cancel
              </button>

              <button
                className={`
            px-4 py-2 rounded-md text-white 
            ${confirmText === "Proceed" ? "bg-blue-600 hover:bg-blue-700" : "bg-blue-300 cursor-not-allowed"}
          `}
                disabled={confirmText !== "Proceed"}
                onClick={() => {
                  setShowConfirmPopup(false);
                  setConfirmText("");
                  HandleRestore();
                }}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default RestoreData;
