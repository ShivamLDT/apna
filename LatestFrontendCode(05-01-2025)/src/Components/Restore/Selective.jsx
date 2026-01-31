/**19/03 */
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from "react-router-dom";
// import { FaFile, FaAngleDown, FaAngleRight } from 'react-icons/fa';
import './Restore.css'; // Import CSS file
import PROLOAD from "../../Image/RSP.gif";
// import * as XLSX from 'xlsx';
import XLSD from "../../Image/XLSD.png";
import io from 'socket.io-client';
import config from '../../config';
// import { HiMiniInformationCircle } from "react-icons/hi2";
import CryptoJS from "crypto-js";
import axios from "axios";
import axiosInstance from '../../axiosinstance';

function encryptData(data) {
  const encryptedData = CryptoJS.AES.encrypt(data, "1234567890").toString();

  return encryptedData;
}
function decryptData(encryptedData) {
  const decryptedData = CryptoJS.AES.decrypt(
    encryptedData,
    "1234567890"
  ).toString(CryptoJS.enc.Utf8);
  return decryptedData;
}

function Selective(props) {
  const [data, setData] = useState(null);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [showNumforPopup, setShowNumforPopup] = useState(false);
  const [selectedPaths, setSelectedPaths] = useState([]);
  const [loading, setLoading] = useState(true); // Loading state
  const [loadingRestore, setLoadingRestore] = useState(false); // Loading state for restore action
  const fileBrowserRef = useRef(null);
  const [responseData, setResponseData] = useState(null);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const accessToken = localStorage.getItem('AccessToken');

  const handleSearchClick = () => {
    localStorage.removeItem("SelectedExtension");
    localStorage.removeItem("SelectedExtensionss");
    localStorage.removeItem('selectedFiles');
    props.onSearchClick();
  };

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  const filterData = (data, searchQuery) => {
    if (!searchQuery) {
      return data; //If no search query, return the original data
    }

    const filteredData = { ...data };

    // Recursively filter folders and files
    const searchInChildren = (children) => {
      if (!children) return {}; // Ensure we don't call Object.entries on undefined or null

      return Object.fromEntries(
        Object.entries(children).filter(([name, item]) => {
          // Check if the name includes the search query
          const matchesName = name.toLowerCase().includes(searchQuery.toLowerCase());
          if (item.type === 'folder') {
            item.children = searchInChildren(item.children); // Recurse into the children of the folder
          }

          // Return true if the name matches or if it's a folder with matching children
          const hasMatchingChildren = item.type === 'folder' && Object.keys(item.children).length > 0;
          // Set the item as expanded if it or its children match the search query
          item.shouldExpand = matchesName || hasMatchingChildren;

          return matchesName || hasMatchingChildren;
        })
      );
    };

    filteredData.children = searchInChildren(filteredData.children) || {}; // Ensure children is not null or undefined
    return filteredData;
  };

  useEffect(() => {
    if (searchQuery === '') {
      setData(responseData); // Reset data to full response data when the search query is cleared
    }
  }, [searchQuery, responseData]);

  useEffect(() => {
    const storedSelectedFiles = JSON.parse(localStorage.getItem('selectedFiles'));
    if (storedSelectedFiles) {
      setSelectedItems(new Set(storedSelectedFiles));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('selectedFiles', JSON.stringify(Array.from(selectedItems)));
  }, [selectedItems]);

  const handleRestore = async (item) => {
    try {
      const storedSelectedFiles = JSON.parse(localStorage.getItem('selectedFiles'));
      if (!storedSelectedFiles) {
        return;
      }

      let storeSelectedValue = JSON.parse(localStorage.getItem("SelectedExtension") || "[]");
      storeSelectedValue = storeSelectedValue.filter(item => item.fileExtensions.trim() !== "").map(item => item.fileExtensions);
      localStorage.removeItem("SelectedExtension");

      const id = localStorage.getItem('id');
      const targetAgentName = localStorage.getItem('targetAgentName');
      const agentName = decryptData(localStorage.getItem('agentName'));
      const target_location = decryptData(localStorage.getItem('target_location'));
      const name = localStorage.getItem('sourceLocation');
      let selectedPathss = localStorage.getItem('selectedPathss');
      // let storageType = localStorage.getItem('storageType');
      const storageType = decryptData(localStorage.getItem('storageType'));
      let selectedIP = localStorage.getItem('selectedIP');

      localStorage.removeItem('selectedPathss');
      localStorage.removeItem('selectedFiles');
      localStorage.removeItem('target_location');
      localStorage.removeItem('agentName');
      localStorage.removeItem('id');
      localStorage.removeItem('targetAgentName');
      localStorage.removeItem('jobName');

      if (!selectedPathss) {
        const renameTargetLocation = '';
        const selectedPathss = renameTargetLocation || item.selectedPathss;
        localStorage.setItem('target_location', encryptData(selectedPathss));
      }

      setLoadingRestore(true); // Show loading indicator

      const response = await axiosInstance.post(`${config.API.Server_URL}/restore`, {
        id: id,
        agentName: agentName,
        targetAgentName: targetAgentName || selectedIP,
        action: "restore",
        targetLocation: target_location,
        RestoreLocation: selectedPathss,
        selectedFiles: storedSelectedFiles,
        sourceLocation: name,
        selectedExtensions: storeSelectedValue,
        storageType: storageType,
      }, {
        headers: {
          'Content-Type': 'application/json',
          token: accessToken
        },
      });

      const responseData = response.data;
      setResponseData(responseData);
      setShowAlert(true); // Show alert message

    } catch (error) {
      console.error('Error restoring data:', error);

      // Handle HTTP errors with server response
      if (error.response) {
        const errorResponse = error.response.data;
        console.error('Failed to restore data:', errorResponse);
        const reason = errorResponse.result?.reason || 'Unknown reason';
        setAlertMessage(`Failed: Internal Server Error occurred. Reason: ${reason}`);
      } else {
        // Handle network or other errors
        setAlertMessage('Error restoring data: ' + error.message);
      }

      setShowAlert(true);
      setShowNumforPopup(false);
    } finally {
      setLoadingRestore(false); // Hide loading indicator
    }
  };

  useEffect(() => {
    if (!loading) {
      // Call postId only if loading is false
      postId();
    }
  }, [loading]); // Run this effect whenever loading state changes

  const postId = async (selectedExtension) => {
    try {
      const id = localStorage.getItem('id');
      const agentName = decryptData(localStorage.getItem('agentName'));
      if (!id || !agentName) {
        console.error('ID or agentName not found in local storage');
        return;
      }

      let storeSelectedValue = JSON.parse(localStorage.getItem("SelectedExtensionss") || "[]");
      storeSelectedValue = storeSelectedValue
        .filter(item => item.fileExtensions.trim() !== "")
        .map(item => item.fileExtensions);

      if (storeSelectedValue.length === 0) {
        storeSelectedValue = selectedExtension; // Use selectedExtension if storeSelectedValue is empty
      }

      let storageType = decryptData(localStorage.getItem('storageType'));

      const response = await axiosInstance.post(`${config.API.Server_URL}/restore`, {
        id: id,
        agentName: agentName,
        selectedExtensions: storeSelectedValue,
        action: "browse",
        storageType: storageType,
      }, {
        headers: {
          'Content-Type': 'application/json',
          token: accessToken
        },
      });

      const responseData = response.data;

      setResponseData(responseData);
      setData(responseData);
      setLoading(false);
    } catch (error) {
      console.error('Error posting data:', error);
      setAlertMessage('An error occurred while fetching data. Please try again.');
      setShowAlert(true);
    }
  };


  // Initial data fetching logic on component mount
  useEffect(() => {
    setLoading(false); // Set loading to false to prevent initial request
  }, []);


  const handleToggleFolder = (folderPath) => {
    setSelectedPaths((prevPaths) =>
      prevPaths.includes(folderPath)
        ? prevPaths.filter((path) => path !== folderPath)
        : [...prevPaths, folderPath]
    );
  };

  const toggleItemSelection = (item, isFolder = false) => {
    setSelectedItems((prevSelectedItems) => {
      const updatedSelectedItems = new Set(prevSelectedItems);

      if (isFolder) {
        if (updatedSelectedItems.has(item.path)) {
          removeFolderItems(item, updatedSelectedItems);
        } else {
          addFolderItems(item, updatedSelectedItems);
        }
      } else {
        if (updatedSelectedItems.has(item.path)) {
          updatedSelectedItems.delete(item.path);
        } else {
          updatedSelectedItems.add(item.path);
        }
        selectParentFolders(item, updatedSelectedItems);
      }

      return updatedSelectedItems;
    });
  };

  const removeFolderItems = (folder, selectedItems) => {
    if (!folder.children) return;

    selectedItems.delete(folder.path);
    Object.values(folder.children).forEach((child) => {
      removeFolderItems(child, selectedItems);
    });
  };

  const addFolderItems = (folder, selectedItems) => {
    selectedItems.add(folder.path);
    if (folder.children) {
      Object.values(folder.children).forEach((child) => {
        addFolderItems(child, selectedItems);
      });
    }
  };

  const selectParentFolders = (item, selectedItems) => {
    let parentPath = item.path;
    while (parentPath !== '') {
      parentPath = parentPath.substring(0, parentPath.lastIndexOf('/'));
      selectedItems.add(parentPath);
    }
  };

  const exportToExcel = () => {
    try {
      if (!responseData || !responseData.result) {
        console.error('No data available to export');
        return;
      }

      const dataToExport = responseData.result.map((file) => ({
        "Storage Type": file.selectedStorageType,
        "Backup Name": file.backup_name,
        'File Name': file.file,
        "Backup Endpoint": file.frombackup_computer_name,
        "Backup Location": file.RestoreLocation,
        "Restore Endpoint": file.torestore_computer_name,
        "Restore Location": file.targetLocation,
        "Restore Start": file.file_start_time,
        "Restore End": file.file_start_end,
        "Restoration Duration": file.file_restore_timetaken,
        'Reason': file.reason,
        'Restore Status': file.restore
      }));

      const ws = XLSX.utils.json_to_sheet(dataToExport);


      /*change by ankita*/
      const headerStyle = { font: { bold: true }, alignment: { horizontal: "center" } };

      // Apply style to the header row
      for (let col = 0; col < dataToExport[0].length; col++) {
        const cell = ws[XLSX.utils.encode_cell({ r: 0, c: col })];
        if (cell) {
          cell.s = headerStyle;
        }
      }

      // Set column widths (example: for 4 columns)
      ws["!cols"] = [
        { wpx: 100 }, // Job Name column width
        { wpx: 100 }, // Created Time column width
        { wpx: 200 }, // Executed Time column width
        { wpx: 100 }, // Endpoint column width
        { wpx: 180 }, // Job Name column width
        { wpx: 150 }, // Created Time column width
        { wpx: 100 }, // Job Name column width
        { wpx: 200 }, // Created Time column width
        { wpx: 200 }, // Executed Time column width
        { wpx: 200 }, // Endpoint column width
        { wpx: 90 }, // Job Name column width
        { wpx: 90 }, // Created Time column width


      ];

      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Restored Files');
      XLSX.writeFile(wb, 'Restored_logs.xlsx');/*change by ankita*/
    } catch (error) {
      console.error('Error exporting to Excel:', error);
    }
  };

  const [progressValue, setProgressValue] = useState(0);
  const [jobname, setJobname] = useState(0);
  const [destination, setDestination] = useState(0);

  const socket = useRef(null);

  useEffect(() => {
    // Fetch the jobName from localStorage
    const storedJobName = decryptData(localStorage.getItem('jobName'));
    setJobname(storedJobName);  // Update the state to hold the jobName from localStorage

    const storedDestination = localStorage.getItem('selectedPathss');
    setDestination(storedDestination);

    socket.current = io(`${config.API.WEB_SOCKET}`);
    if (socket.current) {
      socket.current.on('backup_data', (data) => {
        try {
          const fetchedData = data.backup_jobs || [];

          // Check each job in the response
          fetchedData.forEach(job => {
            // Compare job name with the jobName from localStorage
            if (job.name === storedJobName) {
              if (job.restore_flag !== true && job.restore_flag !== 'true') return;

              const progress = parseFloat(job.progress_number);  // Extract progress number
              // Calculate the progress as 100 - progress_number
              // const adjustedProgress = 100 - progress;
              const adjustedProgress = (100 - progress) < 0 ? 100 : (100 - progress);
              // Update the progress value
              setProgressValue(adjustedProgress);
            }
          });
        } catch (error) {
          console.error('Error processing WebSocket data:', error);
        }
      });

      return () => {
        if (socket.current) {
          socket.current.disconnect();
        }
      };
    }
  }, []); // Empty dependency array to run this effect only once when component mounts


  const handleKeyUp = (event) => {
    // Check if the key pressed is either a character or backspace
    if (event.key === 'Backspace' || event.key.length === 1) {
      const selectedExtension = JSON.parse(localStorage.getItem("SelectedExtensionss") || "[]")
        .map(item => item.fileExtensions)
        .filter(ext => ext.trim() !== ""); // Get non-empty extensions

      postId(selectedExtension); // Pass selectedExtension to postId
    }
  };
  const renderFolders = (folders, path = '') => {
    if (!folders) return null;

    return (
      <ul className='ul'>
        {Object.entries(folders).map(([name, folder]) => {
          const fullPath = folder.path || path;
          const isFolderOpen = selectedPaths.includes(fullPath) || folder.shouldExpand; // Automatically open folders that should expand
          const isSelected = selectedItems.has(fullPath);

          return (
            <li key={fullPath}>
              <div className={`tree-folder-header ${isFolderOpen ? 'opened' : ''}`}>
                <span className="arrow" onClick={() => handleToggleFolder(fullPath)}>
                  {folder.type === 'folder' && (isFolderOpen ? <FaAngleDown /> : <FaAngleRight />)}
                </span>
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => toggleItemSelection(folder, folder.type === 'folder')}
                  className='custom-checkbox'
                />
                <div className="popup-trigger">
                  {folder.type === 'folder' ? (
                    <img src="./folder.svg" className="folderN" alt="Folder Icon" />
                  ) : (
                    <FaFile className="file-icon" />
                  )}
                  <span className={`item-name ${isSelected ? 'selected' : ''}`}>{name}</span>
                </div>
              </div>
              {isFolderOpen && renderFolders(folder.children, fullPath)} {/* Recurse into children if folder is open */}
            </li>
          );
        })}
      </ul>
    );
  };
  const renderTree = () => {
    if (loading) {
      return <div>Loading...</div>;
    }

    if (!data) return null;

    const filteredData = filterData(data, searchQuery);

    // Check if filteredData.children is a valid object
    if (filteredData && filteredData.children && Object.keys(filteredData.children).length === 0) {
      return <div>No results found</div>;
    }

    return renderFolders(filteredData.children);
  };

  const filesData = responseData?.result?.map(file => ({
    storage: file.selectedStorageType,
    jobnam: file.backup_name,
    frome: file.frombackup_computer_name,
    rlocation: file.RestoreLocation,
    endpoint: file.torestore_computer_name,
    targetl: file.targetLocation,
    starttime: file.file_start_time,
    endtime: file.file_start_end,
    // duration:file.file_restore_timetaken,
    file: file.file,
    reason: file.reason,
    restore: file.restore
  })) || [];
  const hasReason = filesData.some(file => file.reason);
  return (
    <section className="selective-source-container">
      <h3>Select Data For Restore</h3>
      {loadingRestore && (
        <div className="alert-overlays">
          <div className="alert-selective">
            <p style={{ fontSize: "10px", border: "1px solid #007bff", borderRadius: "5px" }}><HiMiniInformationCircle aria-hidden="true" style={{ fontSize: "15px", color: "#007bff", marginBottom: "-3px" }} />After you navigate away from this page, the following information is no longer available.</p>
            <img src={PROLOAD} alt="Loading..." />
            <div className="progress-bars-container">
              <span class="loader">Restoring</span>
              <p>Job name:{jobname}</p>
              <p>Destination:{destination}</p>
              <div className="progress-bars" style={{ width: `${progressValue}%` }}></div>
              <progress value={progressValue} max="100" />
              <div className='progress-percentage'>{progressValue.toFixed(2)}%</div>
            </div>
          </div>
        </div>
      )}

      {showAlert && (
        <div className="Status-overlay">
          <div className="status-message">
            <div className='Status-exit-btn'>
              <h1>Restore Report</h1><img onClick={exportToExcel} src={XLSD} className='btnrs' height={20} width={20}></img>
              <span
                className="selective-closeB-btn"
                onClick={handleSearchClick}
              >
                <i className="bx bx-x"></i>
              </span>
            </div>
            {/*change by ankita */}
            <table className="list-view-gridS">
              <thead className='thead'>
                <tr className='tree'>
                  <th className='tree'>Storage Type</th>
                  <th className='tree'>Backup Name</th>
                  <th className='tree'>File Name</th>
                  <th className='tree'>Backup Endpoint</th>
                  <th className='tree'>Backup Location</th>
                  <th className='tree'>Restore Endpoint</th>
                  <th className='tree'>Restore Location</th>
                  <th className='tree'>Restore Start</th>
                  <th className='tree'>Restore End</th>
                  {/* <th>Restoration Duration</th> */}
                  {hasReason && <th>Reason</th>} {/* Conditionally render the header */}
                  <th className='tree'>Status</th>
                </tr>
              </thead>
              <tbody >
                {filesData.map((file, index) => (
                  <tr key={index}>
                    <td className='filess'>{file.storage === "LAN" ? "On-Premise" : file.storage === "UNC" ? "NAS/LAN" : file.storage}</td>
                    {/* {file.storage === "LAN" ? "Local Storage" : file.storage === "UNC" ? "LAN" : file.storage} */}
                    <td className='filess'>{file.jobnam}</td>
                    <td className='filess'>{file.file}</td>
                    <td className='filess'>{file.frome}</td>
                    <td className='filess'>{file.targetl}</td>
                    <td className='filess'>{file.endpoint}</td>
                    <td className='filess'>{file.rlocation}</td>
                    <td className='filess'>{file.starttime}</td>
                    <td className='filess'>{file.endtime}</td>
                    {/* <td className='filess'>{file.duration <= 0 ? "<1s" : file.duration}</td> */}
                    {/* <td className='filess'>{file.duration <= 0 ? "<1s" : `${file.duration}s`}</td> */}

                    {hasReason && <td className='reasonr'>{file.reason}</td>} {/* Conditionally render the data */}
                    <td className='filess'>{file.restore}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}


      <div className="file-browsser" ref={fileBrowserRef}>
        <span className="SrchB">
          <input
            className="bcksrch"
            type="texttt"
            placeholder="Search..."
            value={searchQuery}
            onChange={handleSearch}
            onKeyUp={handleKeyUp}  // Trigger onKeyUp event
          />
          <i className="bx bx-search SrchRB"></i>
        </span>
        {renderTree()}
      </div>
      <button className="restore-button-selective" onClick={handleRestore}>Restore</button>
    </section>
  );
}

export default Selective;
