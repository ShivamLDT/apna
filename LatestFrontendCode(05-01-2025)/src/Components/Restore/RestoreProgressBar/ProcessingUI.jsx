import React, { useContext, useEffect, useRef, useState } from "react";
import "./ProcessingUI.css"; // Move styles into this file
import config from "../../../config";
import { Backupindex } from "../../../Context/Backupindex";
import { io } from 'socket.io-client';
import { el } from "date-fns/locale/el";
import RestoreReportTable from "../TableView/RestoreReportTable";
import MiniMizeIcon from "../../../assets/minimize-icon.png"
import DeleteIcon from "../../../assets/delete.png"
import { Rnd } from "react-rnd";
import { Minus } from 'lucide-react';
import { NotificationContext } from "../../../Context/NotificationContext";
import { RestoreContext } from "../../../Context/RestoreContext";
import { UIContext } from "../../../Context/UIContext";
import AlertComponent from "../../../AlertComponent";

const ProcessingUI = ({ setShowProgress, setShowRestorePopup, showProgress }) => {
  const progressFillRef = useRef(null);
  const progressTextRef = useRef(null);
  const statusTitleRef = useRef(null);
  const [destination, setDestination] = useState()
  const [alert, setAlert] = useState(null);
  const jobNameRef = useRef(null);
  const [progressValue, setProgressValue] = useState(0);
  const socketRef = useRef(null);
  const { showLivePopup, setShowLivePopup, showLocalLive, setshowLocalLive, localShowLocalLive, setlocalShowLocalLive, setshowTableLive } = useContext(UIContext);
  const { endpointagentname, getRestoreData } = useContext(Backupindex);
  const [JobName, setJobName] = useState('');
  const [uniqueJobs, setUniqueJobs] = useState([]);
  const [popupTime, setPopupTime] = useState({ visible: false, message: "" });
  const [isMinimized, setIsMinimized] = useState(false);
  const [isFinish, setisFinish] = useState(false);
  const isFirstRender = useRef(true); // Track first render
  const { resultCount, setResultCount } = useContext(NotificationContext)
  const { restoreTotalData, showRestoreReportTable, setShowRestoreReportTable, reStoreTableData, storeMultipleRestoreName, ValdidateRestorePopup, setValdidateRestorePopup, openRestorePopup, setOpenRestorePopup, } = useContext(RestoreContext)
  const [showTableData, setShowTableData] = useState(false);
  const countRef = useRef(0);

  useEffect(() => {
    // setResultCount(resultCount + 1);
    // setResultCount(prev => prev + 1);
    setOpenRestorePopup(true);
    setShowProgress(false);
  }, []);

  useEffect(() => {


    if (isFirstRender.current) {
      isFirstRender.current = false; // Mark as not first render anymore
      return; // Skip effect logic on first render
    }
    if (reStoreTableData.length > 0 && openRestorePopup) {
      if (resultCount === reStoreTableData.length) {
        setShowLivePopup(false);
        setShowProgress(false);
        setOpenRestorePopup(false);
      }
    }
  }, [reStoreTableData]);



  useEffect(() => {
    if (reStoreTableData && Array.isArray(reStoreTableData.result) && reStoreTableData.result.length === 0 && Object.keys(reStoreTableData).length > 0) {
      // setShowLivePopup(false)
    }
    if (countRef.current > 0) {
      setShowRestoreReportTable(true);
      setshowTableLive(true);
    }
    countRef.current += 1;
  }, [reStoreTableData]);


  useEffect(() => {
    if (Array.isArray(uniqueJobs) && uniqueJobs.length > 0) {
      const allProgressZero = uniqueJobs.every(job => job.progress_number === 0);
      setShowTableData(allProgressZero);
      if (allProgressZero) {
        setShowTableData(true);
        // setShowLivePopup(false);
        // setShowProgress(false);
      } else {
        // setShowTable(false);
      }
    } else {
      // Optionally handle empty case
      // setShowTable(false);
    }

  }, [uniqueJobs]);

  function handleMiniMize() {
    setIsMinimized(prev => !prev);
    setlocalShowLocalLive(prev => !prev);
    setShowProgress(false);
    setShowRestorePopup(false);
  }
  function handleCross(e) {
    e.stopPropagation();
    setAlert({
      message: "After you navigate away from this page, the following information is no longer available.",
      type: "warning"
    });

  }

  useEffect(() => {
    if (!Array.isArray(reStoreTableData) || reStoreTableData.length === 0) return;
    const updatedPopup = ValdidateRestorePopup.filter((item, index) => {
      const resultEntry = reStoreTableData[index];
      const result = resultEntry?.result;
      return !Array.isArray(result);
    });
    setValdidateRestorePopup(updatedPopup);
    if (updatedPopup.length === 0) {
      setisFinish(true);
    }
  }, [reStoreTableData]);



  useEffect(() => {
    if (!storeMultipleRestoreName || storeMultipleRestoreName.length === 0) return;

    const socket = io(`${config.API.WEB_SOCKET}`);


    socket.on('connect', () => {
    });

    socket.on('backup_data', (data) => {
      const jobs = Array.isArray(data.backup_jobs) ? data.backup_jobs : [];
      // setUniqueJobs((prevJobs) => {
      //   const updatedJobs = [...prevJobs];
      //   const existingIds = new Set(prevJobs.map(j => j.id));
      //   storeMultipleRestoreName.forEach((storedJobName) => {
      //     const lowerCaseStoredName = storedJobName.toLowerCase().trim();
      //     const matchedJobs = jobs.filter(
      //       job =>
      //         job.name?.toLowerCase().trim().includes(lowerCaseStoredName) &&
      //         (job.restore_flag === true || job.restore_flag === 'true')
      //     );

      //     matchedJobs.forEach(job => {
      //       const progress = parseFloat(job.progress_number);
      //       const safeProgress = isNaN(progress) ? 0 : Math.min(100, Math.floor(progress));

      //       const existingIndex = updatedJobs.findIndex(j => j.id === job.id);

      //       if (existingIndex !== -1) {
      //         updatedJobs[existingIndex] = {
      //           ...updatedJobs[existingIndex],
      //           progress_number: safeProgress
      //         };
      //       } else {
      //         updatedJobs.push({
      //           id: job.id,
      //           name: job.name,
      //           progress_number: safeProgress
      //         });
      //       }
      //     });
      //   });

      //   return updatedJobs;
      // });
      // setUniqueJobs((prevJobs) => {
      //   const updatedJobs = [...prevJobs];
      //   const seenIds = new Set(prevJobs.map(j => j.id)); // initialize with existing

      //   storeMultipleRestoreName.forEach((storedJobName) => {
      //     const lowerCaseStoredName = storedJobName.toLowerCase().trim();
      //     const matchedJobs = jobs.filter(
      //       job =>
      //         job.name?.toLowerCase().trim().includes(lowerCaseStoredName) &&
      //         (job.restore_flag === true || job.restore_flag === 'true')
      //     );

      //     matchedJobs.forEach(job => {
      //       const progress = parseFloat(job.progress_number);
      //       const safeProgress = isNaN(progress) ? 0 : Math.min(100, Math.floor(progress));

      //       if (seenIds.has(job.id)) {
      //         // Already added, just update progress if needed
      //         const index = updatedJobs.findIndex(j => j.id === job.id);
      //         if (index !== -1) {
      //           updatedJobs[index] = {
      //             ...updatedJobs[index],
      //             progress_number: safeProgress
      //           };
      //         }
      //       } else {
      //         updatedJobs.push({
      //           id: job.id,
      //           name: job.name,
      //           progress_number: safeProgress
      //         });
      //         seenIds.add(job.id); // Add to set to prevent future duplicates
      //       }
      //     });
      //   });

      //   return updatedJobs;
      // });

      setUniqueJobs((prevJobs) => {
        let updatedJobs = [...prevJobs];
        const seenIds = new Set(prevJobs.map(j => j.id));
        storeMultipleRestoreName.forEach((storedJobName) => {
          const lowerCaseStoredName = storedJobName.toLowerCase().trim();
          const matchedJobs = jobs.filter(
            job =>
              job.name?.toLowerCase().trim().includes(lowerCaseStoredName) &&
              (job.restore_flag === true || job.restore_flag === 'true')
          );

          matchedJobs.forEach(job => {
            const progress = parseFloat(job.progress_number);
            const safeProgress = isNaN(progress) ? 0 : Math.min(100, Math.floor(progress));

            if (seenIds.has(job.id)) {
              // Already added → update
              updatedJobs = updatedJobs.map(j =>
                j.id === job.id ? { ...j, progress_number: safeProgress, restore_location: job.restore_location } : j
              );
            } else {
              // Add new one
              updatedJobs.push({
                id: job.id,
                name: job.name,
                progress_number: safeProgress,
                restore_location: job.restore_location
              });
              seenIds.add(job.id);
            }
          });
        });

        // 🟢 Deduplicate once more just in case
        const uniqueJobs = Array.from(new Map(updatedJobs.map(j => [j.id, j])).values());

        return uniqueJobs;
      });

    });

    socket.on('disconnect', () => {
    });

    socket.on('connect_error', (err) => {
      console.error('❌ Socket.IO connection error:', err);
      setPopupTime({
        visible: true,
        message: "SomeThing Went Wrong Please Try Again Later",
      });
    });

    return () => {
      socket.disconnect();
    };
  }, [storeMultipleRestoreName]);


  useEffect(() => {
    simulateProgress();

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
      } else {
        if (ws && ws.readyState === WebSocket.CLOSED) {
        }
      }
    });
  }, []);

  let ws = null;



  const updateUI = (data) => {
    if (data.progress !== undefined) {
      const progress = Math.min(Math.max(data.progress, 0), 100);
      const pr = Math.floor(100 - progressValue);
      const pr_1 = `${Math.floor(100 - progressValue)}%`;
    }
  };

  const simulateProgress = () => {
    let progress = 0;
    const statuses = ["Initializing", "Restoring", "Processing", "Finalizing"];
    let currentStatus = 0;

    const interval = setInterval(() => {
      progress += Math.random() * 5;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
      }
      if (progress > (currentStatus + 1) * 25 && currentStatus < statuses.length - 1) {
        currentStatus++;
      }

      updateUI({
        status: statuses[currentStatus],
        jobName: "test",
        progress
      });
    }, 500);
  };
  function closePopupTime() {
    setPopupTime({
      visible: false,
      message: "",
    });
    setShowLivePopup(false);
    setlocalShowLocalLive(false);
  }

  return (
    <>

      {localShowLocalLive ? <div className="progressBarData-wrapper">
        <div className="progressBarData-modal-overlay">
          <Rnd
            default={{
              x: window.innerWidth / 2 - 300,
              y: window.innerHeight / 2 - 250,
              width: 400,
              height: 500,
            }}
            minWidth={400}
            minHeight={300}
            bounds="window"
            dragHandleClassName="server-popup-drag-handle"
          >
            <div className="progressBarData-background"></div>
            <div className="pregressBarData-handle server-popup-drag-handle" >


              <div className="progressBarData-modal server-popup resizable-popup">
                <div className="MiniMize-section">
                  <div className="Minimize-section" onClick={handleMiniMize}>
                    <Minus />
                  </div>

                  <div className="cross-section" onClick={handleCross}>
                    <img className="cross-img" src={DeleteIcon} alt="" srcset="" />
                  </div>
                </div>

                <div className="progressBarData-modal-body">
                  <div className="progressBarData-process-icon progressBarData-pulse">
                    <div className="progressBarData-basket-icon"></div>
                    <div className="progressBarData-spinner"></div>
                  </div>
                  <h2 className="progressBarData-processing-title">PROCESSING</h2>
                  <p className="progressBarData-processing-subtitle">
                    Please wait while we set
                    <br />
                    things up for you!
                  </p>

                  <div className="progressBarData-status-section">
                    <div className="progressBarData-status-title" ref={statusTitleRef}>Restore Your Data</div>
                    {/* {storeMultipleRestoreName.map((name, index) => {
                      const matchingJobs = uniqueJobs.filter((job) => job.name === name);

                      // Check if any result array is empty
                      const isAnyResultEmpty = Array.isArray(reStoreTableData) &&
                        reStoreTableData.some(item => Array.isArray(item.result) && item.result.length === 0);
                      return (
                        <div key={index}>
                          {matchingJobs.length > 0 &&
                            matchingJobs.map((job) => {
                              const progress = Math.floor(job?.progress_number || 0);
                              return (
                                <div key={job.id}>
                                  {job?.progress_number === 0 ? (
                                    <div className="flex items-center justify-center gap-2 text-green-600 font-semibold text-center">
                                      {job.name} - Finish
                                      <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="18"
                                        height="18"
                                        fill="currentColor"
                                        viewBox="0 0 16 16"
                                      >
                                        <path d="M16 2L6 15l-5-5 1.5-1.5L6 12.2 14.5 2z" />
                                      </svg>
                                    </div>
                                  ) : (
                                    <>
                                      <div className="progress_data flex justify-between mb-3">
                                        <div className="progress-name">{job.name}</div>
                                        <div className="progress-time">{100 - progress}%</div>
                                      </div>
                                      <div className="progressBarData-progress-container mb-5">
                                        <div className="progressBarData-progress-bar">
                                          <div
                                            className="progressBarData-progress-fill"
                                            style={{ width: `${100 - progress}%` }}
                                          >
                                            {job.name}
                                          </div>
                                        </div>
                                      </div>
                                    </>
                                  )}
                                </div>
                              );
                            })}
                        </div>
                      );

                    })} */}

                    {[...new Set(storeMultipleRestoreName)].map((name, index) => {
                      const matchingJobs = uniqueJobs.filter((job) => job.name === name);

                      // ✅ Check if this job has an error
                      const errorData = Array.isArray(reStoreTableData)
                        ? reStoreTableData.find(item => item.jobName === name && item.error === true)
                        : null;

                      if (errorData) return <React.Fragment key={index}></React.Fragment>;

                      return (
                        <div key={index}>
                          {/* ✅ Show error message if restore failed */}
                          {/* {errorData && (
                            <div className="flex items-center justify-center gap-2 text-red-600 font-semibold text-center whitespace-normal break-all mb-3 p-2 bg-red-50 rounded">
                              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                                <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z" />
                              </svg>
                              <div>
                                <div>{name} - Failed</div>
                                <div className="text-xs text-red-500 mt-1">{errorData.message}</div>
                              </div>
                            </div>
                          )} */}

                          {/* Existing job rendering logic */}
                          {matchingJobs.length > 0 &&
                            matchingJobs.map((job) => {
                              const progress = Math.floor(job?.progress_number || 0);
                              return (
                                <div key={job.id}>
                                  {job?.progress_number === 0 ? (
                                    <div className="flex items-center justify-center gap-2 text-green-600 font-semibold text-center whitespace-normal break-all">
                                      {job.name} - Finish
                                      <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="18"
                                        height="18"
                                        fill="currentColor"
                                        viewBox="0 0 16 16"
                                      >
                                        <path d="M16 2L6 15l-5-5 1.5-1.5L6 12.2 14.5 2z" />
                                      </svg>
                                    </div>
                                  ) : (
                                    <>
                                      <div className="progress_data flex justify-between mb-3">
                                        <div className="progress-name whitespace-normal break-all">{job.name}</div>
                                        <div className="progress-time">{100 - progress}%</div>
                                      </div>
                                      <div className="progressBarData-progress-container mb-5">
                                        <div className="progressBarData-progress-bar">
                                          <div
                                            className="progressBarData-progress-fill"
                                            style={{ width: `${100 - progress}%` }}
                                          >
                                            {job.name}
                                          </div>
                                        </div>

                                        {job.restore_location &&
                                          <div className="progressBarData-restore-location mt-1 text-sm text-gray-500">
                                            Restore Location: {job.restore_location}
                                          </div>
                                        }
                                      </div>
                                    </>
                                  )}
                                </div>
                              );
                            })}

                          {/* ✅ Show waiting state if no jobs yet and no error */}
                          {matchingJobs.length === 0 && !errorData && (
                            <div className="flex items-center justify-center gap-2 text-gray-500 text-sm mb-3">
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500"></div>
                              {name} - Waiting for data...
                            </div>
                          )}
                        </div>
                      );
                    })}

                  </div>

                </div>
              </div>
            </div>

          </Rnd>
        </div >
      </div > : <h1 className="this is heading "></h1>}

      {
        popupTime.visible && (
          <div className="fixed inset-0  visible-popup flex items-center justify-center z-[100000]">
            <div className="bg-white rounded-lg p-6 shadow-xl text-center" style={{ marginTop: "85px" }}>
              <p className="text-lg font-semibold mb-4">{popupTime.message}</p>
              <button
                onClick={closePopupTime}
                className="px-8 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Ok
              </button>
            </div>
          </div>
        )
      }
      <div >
        <button
          className={`minimize-btn ${isMinimized ? 'minimized' : ''}`}
          onClick={handleMiniMize}
        >
          <div className="minimize-icon"></div>
        </button>

        <style jsx>{`
        .minimize-btn {
          position: absolute;
          width: 48px;
          height: 48px;
          background: #4285f4;
          border: none;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          // box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
          transition: all 0.2s ease;
          z-index: 10;
          overflow: hidden;
        }

        .minimize-btn:hover {
          transform: scale(1.05);
          // box-shadow: 0 6px 16px rgba(66, 133, 244, 0.4);
        }

        .minimize-btn.minimized {
          background: #666;
          box-shadow: 0 4px 12px rgba(102, 102, 102, 0.3);
        }

        .minimize-icon {
          width: 16px;
          height: 2px;
          background: white;
          border-radius: 1px;
          transition: transform 0.2s ease;
        }

        .minimize-btn.minimized .minimize-icon {
          transform: rotate(180deg);
        }

        /* Blinking Corner Dot Animation */
        .minimize-btn::before {
          content: '';
          position: absolute;
          top: 10px;
          right: 10px;
          width: 6px;
          height: 6px;
          background: #00ff88;
          border-radius: 50%;
          animation: blinkDot 1s ease-in-out infinite;
          // box-shadow: 0 0 4px rgba(0, 255, 136, 0.5);
        }

        @keyframes blinkDot {
          0%, 100% { 
            opacity: 1; 
            transform: scale(1); 
          }
          50% { 
            opacity: 0.3; 
            transform: scale(0.8); 
          }
        }
      `}</style>

        {alert && (
          <AlertComponent
            message={alert.message}
            type={alert.type}
            onClose={() => {
              setAlert(null);
              setShowLivePopup(false);      // from UIContext
              setlocalShowLocalLive(false); // hide local restore popup
              setShowProgress(false);
              setShowRestorePopup(false);
            }}
          />
        )}
      </div>
    </>
  );
};

export default ProcessingUI;