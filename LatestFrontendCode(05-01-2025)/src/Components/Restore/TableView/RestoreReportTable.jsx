import React, { useContext, useEffect, useState, useRef } from 'react';
import { Minus, ArrowBigLeft, ArrowBigRight } from 'lucide-react';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Slider from 'react-slick';
import { FaFileExcel } from 'react-icons/fa';
import { IoMdClose } from 'react-icons/io';
import * as XLSX from 'xlsx';
import { Backupindex } from '../../../Context/Backupindex';
import MiniMizeIcon from "../../../assets/minimize-icon.png"
import DeleteIcon from "../../../assets/delete.png"
import { el } from 'date-fns/locale/el';
import { useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import { useToast } from '../../../ToastProvider';
import RepoIcon from '../../Reports/Jobs/RepoIcon';
import { RestoreContext } from "../../../Context/RestoreContext";
import { UIContext } from '../../../Context/UIContext';
const RestoreReportTable = ({ setShowRestorePopup, setShowProgress }) => {
  const { showTableLive, setshowTableLive, setlocalShowLocalLive } = useContext(UIContext);
  const [tableData, setTableData] = useState([]);
  const [tableGroups, setTableGroups] = useState([]);
  const [showMessage, setShowMessage] = useState("");
  const [isMinimized, setIsMinimized] = useState(false);
  const [restoreTableNameData, setRestoreTableNameData] = useState(null);
  // const [newRestoreName, setNewRestoreName] = useState([]);
  const [currentSlide, setCurrentSlide] = useState(0);
  const { restoreTotalData, setShowRestoreReportTable, reStoreTableData, restoreNameTable } = useContext(RestoreContext)
  const [popupTime, setPopupTime] = useState({ visible: false, message: "" });
  const Navigate = useNavigate();

  // 👇 ADDED: useRef for external slider control
  const sliderRef = useRef(null);


  function formatDateString(str) {
    // Match patterns like: 2025 11 26, 12:31:17
    const regex = /^(\d{4}) (\d{2}) (\d{2}), (.*)$/;

    const match = String(str).match(regex);
    if (!match) return str; // return original if not matching

    const [, year, month, day, time] = match;
    return `${year}/${month}/${day}, ${time}`;
  }


  function handleMiniMize() {
    setIsMinimized(prev => !prev);
    setshowTableLive(prev => !prev);
  }

  const { showToast } = useToast();

  const headerMapping = {
    selectedStorageType: 'Storage Type',
    backup_name: 'Backup Name',
    file: 'File Name',
    frombackup_computer_name: 'Backup EndPoint',
    RestoreLocation: 'Restore Location',
    torestore_computer_name: 'Restore EndPoint',
    targetLocation: 'Backup Location',
    file_start_time: 'Restore Start',
    file_start_end: 'Restore End',
    file_restore_timetaken: 'Time Taken',
    reason: 'Reason',
    restore: 'Status',
  };
  useEffect(() => {
    if (!reStoreTableData || reStoreTableData.length === 0) return;

    const hasErrors = reStoreTableData.some(item => item.error === true);
    const hasSuccess = reStoreTableData.some(item =>
      Array.isArray(item.result) && item.result.length > 0
    );

    if (hasErrors && !hasSuccess) {
      // All failed - use error toast
      showToast("Restore operations failed", "error");
    } else if (!hasErrors && hasSuccess) {
      // All successful
      showToast("Your Restore Complete");
    }
  }, [reStoreTableData]);


  const settings = {
    dots: true,
    infinite: false,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,

    // 👇 REMOVED: nextArrow and prevArrow settings

    afterChange: (index) => {
      setCurrentSlide(index);
      const group = tableGroups[index];
      if (group.error === true) {
        setRestoreTableNameData(group.jobName || "N/A");
      } else {
        const firstName = group?.result?.[0]?.backup_name || "N/A";
        setRestoreTableNameData(firstName);
      }
    },

    appendDots: (dots) => (
      // 👇 MODIFIED: Added inline style to ensure dots are positioned correctly
      <ul style={{ position: 'absolute', bottom: '10px', width: '100%', display: 'flex', justifyContent: 'center' }}>
        {dots.map((dot, index) => (
          <li key={index} onClick={() => {
            setCurrentSlide(index);
            const group = tableGroups[index];
            if (group.error === true) {
              setRestoreTableNameData(group.jobName || "N/A");
            } else {
              const firstName = group?.result?.[0]?.backup_name || "N/A";
              setRestoreTableNameData(firstName);
            }
            // 👇 ADDED: Manually navigate to slide on dot click
            if (sliderRef.current) sliderRef.current.slickGoTo(index);
          }}>
            {dot}
          </li>
        ))}
      </ul>
    )
  };



  useEffect(() => {
    setTableGroups(reStoreTableData || []);

    // Set initial heading - check for error or success
    if (reStoreTableData && reStoreTableData.length > 0) {
      const firstGroup = reStoreTableData[0];

      // If it's an error, use jobName from error object
      if (firstGroup.error === true) {
        setRestoreTableNameData(firstGroup.jobName || "N/A");
      } else {
        // Otherwise use backup_name from result
        const firstName = firstGroup?.result?.[0]?.backup_name || "N/A";
        setRestoreTableNameData(firstName);
      }
    }

    const allEmpty = Array.isArray(reStoreTableData) &&
      reStoreTableData.every(item => Array.isArray(item.result) && item.result.length === 0);

    if (allEmpty) {
      setShowMessage("No Data Found");
    } else {
      setShowMessage(null);
    }
  }, [reStoreTableData]);


  const excludedKeys = ['backup_id', 'backup_name_id', 'backup_pid', 't14', 'file_restore_timetaken'];
  let headers = Object.keys(tableData[0] || {}).filter(
    (key) => !excludedKeys.includes(key)
  );

  const hasFailedStatus = tableData.some(item => item.restore === 'failed');
  if (!hasFailedStatus) {
    headers = headers.filter(key => key !== 'reason');
  }

  const exportToExcel = () => {
    if (!tableGroups || tableGroups.length === 0) {
      setPopupTime({ visible: true, message: "No Data Available" });
      return;
    }

    let dataToProcess = [];
    if (
      tableGroups[currentSlide] &&
      tableGroups[currentSlide].result &&
      Array.isArray(tableGroups[currentSlide].result)
    ) {
      dataToProcess = tableGroups[currentSlide].result;  // <-- use current slide
    } else {
      dataToProcess = [];
    }

    if (dataToProcess.length === 0) {
      setPopupTime({ visible: true, message: "No Data Available" });
      return;
    }

    const dataToExport = dataToProcess.map((item) => {
      const filteredItem = {};
      const keysToUse =
        orderedHeaders && orderedHeaders.length > 0
          ? orderedHeaders
          : Object.keys(dataToProcess[0]);

      keysToUse.forEach((key) => {
        if (key === "reason" && item.restore === "success") return;
        if (key === "file_restore_timetaken") return;

        const label = headerMapping[key] || key;
        filteredItem[label] = item[key] || "";
      });

      return filteredItem;
    });

    const worksheet = XLSX.utils.json_to_sheet(dataToExport);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Restore Report");
    XLSX.writeFile(workbook, `restore_report_${restoreTableNameData}.xlsx`);
  };


  function closePopupTime() {
    setPopupTime({ visible: false, message: "" })
  }

  function HandleCLosePopup() {
    setShowRestoreReportTable(false);
    setShowRestorePopup(false);
    setShowProgress(false);
    // setlocalShowLocalLive(false)
  }
  function HandleClickBackLog() {
    Navigate("/backup-logs");
  }
  const orderedHeaders = [
    'selectedStorageType',
    'backup_name',
    'file',
    'frombackup_computer_name',
    'targetLocation',
    'torestore_computer_name',
    'RestoreLocation',
    'file_start_time',
    'file_start_end',
    'file_restore_timetaken',
    'reason',
    'restore'
  ];

  if (!Array.isArray(tableData)) {
    return (
      <div className="popup-overlayT">
        <div className="modal">
          <div className="flex items-center justify-center h-full">
            <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
              <div
                className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
                style={{ animation: 'oceanSlide 3s infinite' }}
              />
              <h4>{showMessage}</h4>
              <style>{`
                @keyframes oceanSlide {
                  0% { transform: translateX(-150%); }
                  66% { transform: translateX(0%); }
                  100% { transform: translateX(150%); }
                }
              `}</style>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {showTableLive ? ( // Conditional opening tag
        <div className="RestoreTable_overLay fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="ml-6 mr-6 bg-white rounded-lg shadow-lg w-full max-h-[80vh] h-[84%] flex flex-col overflow-hidden" style={{ height: "84%" }}>

            {/* Top Navbar (Sticky) */}
            <div className="bg-blue-500 text-white px-6 py-4 flex justify-between items-center sticky top-0 z-20">
              <h2 className="text-xl font-semibold">Restore Report of {restoreTableNameData || "N/A"}</h2>
              <div className="flex items-center gap-4">
                <div className="MiniMize-section">
                  <div className="Minimize-section" onClick={handleMiniMize}>
                    <Minus />
                  </div>
                </div>
                <button
                  onClick={exportToExcel}
                  title="Download Excel"
                  className="hover:text-green-200 text-xl"
                >
                  <FaFileExcel />
                </button>
                <button
                  onClick={HandleCLosePopup}
                  title="Close"
                  className="hover:text-red-300 text-2xl"
                >
                  <IoMdClose />
                </button>
              </div>
            </div>

            <div className="overflow-auto flex-1 relative px-2">

              {/* 👇 Wrap Slider in a relative div to position arrows absolutely over it */}
              <div className="relative">
                <Slider
                  {...settings}
                  ref={sliderRef} // 👈 Assigned ref to Slider
                >
                  {Array.isArray(tableGroups) &&
                    tableGroups?.map((group, groupIndex) => {
                      const currentTableData = group.result || [];

                      if (currentTableData.length === 0) {
                        const isError = group.error === true;

                        if (isError) {
                          return (
                            <div
                              key={`error-${groupIndex}`}
                              className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg mb-4 shadow-sm"
                              style={{ width: "100%", display: "flex" }}
                            >
                              <div className="flex items-center gap-3">
                                <div className="flex items-center justify-center w-8 h-8 bg-red-100">
                                  <span className="text-red-600 text-lg">❌</span>
                                </div>
                                <div>
                                  <span className="text-lg font-semibold text-red-700">
                                    {group.jobName || "Restore Failed"}
                                  </span>
                                  <p className="text-sm text-red-600 mt-1">
                                    {group.message || "Restore operation failed. Please try again."}
                                  </p>
                                </div>
                              </div>
                              <button
                                onClick={HandleCLosePopup}
                                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors duration-200 font-medium text-sm"
                              >
                                Close
                              </button>
                            </div>
                          );
                        }

                        return (
                          <div
                            key={`success-${groupIndex}`}
                            className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg mb-4 shadow-sm"
                            style={{ width: "100%", display: "flex" }}
                          >
                            <div className="flex items-center gap-3">
                              <div className="flex items-center justify-center w-8 h-8 bg-green-100">
                                <span className="text-green-600 text-lg">✅</span>
                              </div>
                              <div>
                                <span className="text-lg font-semibold text-green-700">
                                  {group.jobName || "Restore Completed"}
                                </span>
                                <p className="text-sm text-green-600 mt-1">
                                  Restore completed successfully. Check details in backlogs.
                                </p>
                              </div>
                            </div>
                            <button
                              onClick={HandleClickBackLog}
                              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors duration-200 font-medium text-sm"
                            >
                              View Backup-logs
                            </button>
                          </div>
                        );
                      }

                      // If result is NOT empty → render table slide
                      const excludedKeys = ['backup_id', 'file_restore_timetaken', 'backup_name_id', 'backup_pid', 't14', 'file_restore_timetaken'];
                      let headers = Object.keys(currentTableData[0] || {}).filter(key => !excludedKeys.includes(key));
                      const hasFailedStatus = currentTableData?.some(item => item.restore === 'failed');
                      if (!hasFailedStatus) headers = headers.filter(key => key !== 'reason');
                      return (
                        <div key={`table-${groupIndex}`} className='main-table-container'>
                          <div className="w-full">
                            <table className="min-w-full table-fixed border-collapse">
                              <thead>
                                <tr>
                                  {orderedHeaders.map((key) => {
                                    const hasFailedItems = currentTableData.some(item => item.restore === 'failed');

                                    // If reason is not needed (no failed items)
                                    if (key === 'reason' && !hasFailedItems) return null;

                                    // Never show time taken field
                                    if (key === 'file_restore_timetaken') return null;

                                    const isPathColumn = key === 'targetLocation' || key === 'RestoreLocation';
                                    const isReasonColumn = key === 'reason';


                                    return (
                                      <th
                                        key={key}
                                        className={`
                                        px-2 py-2 text-left text-xs font-medium text-gray-700 bg-gray-100 border-r
                                        ${key === 'backup_name' ? "w-40" : ""}
                                        ${key === 'file' ? "w-28" : ""}
                                      `}
                                        // 👇 ADDED: Inline style for max-width (Tailwind v2 compatible fix for overflow)
                                        style={{
                                          maxWidth: isPathColumn ? '200px' : (isReasonColumn ? '250px' : 'auto'),
                                          width: isPathColumn ? '200px' : (isReasonColumn ? '250px' : 'auto'),
                                          overflowWrap: 'break-word', // Ensure wrapping works
                                        }}
                                      >

                                        <div className="break-words whitespace-normal">
                                          {headerMapping[key] || key}
                                        </div>
                                      </th>
                                    );
                                  })}
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-200" style={{ maxWidth: "300px" }}>
                                {currentTableData.map((item, index) => (
                                  <tr key={index} className="hover:bg-gray-50">
                                    {orderedHeaders.map((key) => {
                                      const hasFailedItems = currentTableData.some(item => item.restore === 'failed');
                                      // Skip rendering cells for columns that shouldn't be shown
                                      if (key === 'reason' && !hasFailedItems) return null;
                                      // Never show time taken field
                                      if (key === 'file_restore_timetaken') return null;

                                      let value = item[key];
                                      // Conditionally clear values for unwanted fields
                                      if (key === 'reason' && item.restore !== 'failed') {
                                        value = '';
                                      }

                                      const isPathColumn = key === 'targetLocation' || key === 'RestoreLocation';
                                      const isReasonColumn = key === 'reason';

                                      return (
                                        <td
                                          key={key}
                                          className="px-2 py-2 text-xs text-gray-900 border-r border-gray-200 align-top">
                                          <div
                                            className={`break-words whitespace-normal ${key === "file" ? "max-w-xs" : ""}`}
                                            // 👇 ADDED: Inline style for max-width (Tailwind v2 compatible fix for overflow)
                                            style={{
                                              maxWidth: isPathColumn ? '200px' : (isReasonColumn ? '250px' : 'auto'),
                                            }}
                                          >
                                            {/* Special handling for storage type to show icon */}
                                            {key === 'selectedStorageType' || key === 'storage Type' ? (
                                              <div className="flex items-center justify-center mt-1 gap-1">
                                                <RepoIcon repo={value} />
                                                {/* <span>{value !== undefined && value !== '' ? String(value) : '-'}</span> */}
                                              </div>
                                            ) : (
                                              // Regular text display for other columns
                                              value !== undefined && value !== '' ? formatDateString(String(value)) : '-'
                                            )}
                                          </div>
                                        </td>
                                      );
                                    })}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      );
                    })}
                </Slider>

                {/* 👇 External Arrow Controls for responsive positioning */}
                {tableGroups && tableGroups.length > 1 && ( // Only show arrows if there's more than one slide
                  <>
                    <button
                      onClick={() => sliderRef.current.slickPrev()}
                      className="
                      absolute left-2 top-1/2 transform -translate-y-1/2 z-50
                      bg-blue-500 text-white rounded-full
                      w-10 h-10 md:w-8 md:h-8 sm:w-7 sm:h-7
                      flex items-center justify-center
                      shadow-lg hover:bg-blue-600
                    "
                    >
                      <ArrowBigLeft />
                    </button>
                    <button
                      onClick={() => sliderRef.current.slickNext()}
                      className="
                      absolute right-2 top-1/2 transform -translate-y-1/2 z-50
                      bg-blue-500 text-white rounded-full
                      w-10 h-10 md:w-8 md:h-8 sm:w-7 sm:h-7
                      flex items-center justify-center
                      shadow-lg hover:bg-blue-600
                    "
                    >
                      <ArrowBigRight />
                    </button>
                  </>
                )}

              </div>
              {/* Closes <div className="relative"> */}
            </div>
            {/* Closes <div className="overflow-auto flex-1 relative px-2"> */}
          </div>
          {/* Closes <div className="ml-6 mr-6 bg-white ..."> */}
        </div>
      ) : null} {/* Closes <div className="RestoreTable_overLay..."> and the conditional (using null instead of "") */}

      <button
        className={`minimize-btn ${isMinimized ? 'Data' : ''}`} style={{ bottom: "85px" }}
        onClick={handleMiniMize}
      >
        <div className="icon-L">L</div>
      </button>

      {popupTime.visible && (
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
      )}
      {/* <ToastContainer position="top-right" autoClose={3000} /> */}
    </>
  );
};

export default RestoreReportTable;