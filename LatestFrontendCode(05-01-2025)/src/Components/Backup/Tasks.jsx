import React, { useState, useEffect, useRef } from 'react';
import './Backup.css';
import ProgressTracker from './ProgressTracker';
import Endpoint from './Endpoint';
import LocalIcon from '../../assets/Localdisk.png';
import GoogleDriveIcon from '../../assets/googledrive.png';
import AzureIcon from '../../assets/azure.png';
import AWSIcon from '../../assets/aws.png';
import NASIcon from '../../assets/nas.png';
import OneDriveIcon from '../../assets/onedrive.png';
import FileExtensions from './FileExtensions';
import axios from 'axios';
import { encryptData } from "./encryptionUtils";
import { decryptData } from "./encryptionUtils";
import { useContext } from "react";
import { Backupindex } from "../../Context/Backupindex";
import Resecheduler from "./Rescheduler"
import Las from "./nas/Las"
import Gif from './Gif';
import GDriveModal from './PopupModel/GDriveModal';
import config from "../../config"
import { Loader2 } from 'lucide-react';
import CryptoJS from "crypto-js";
import useSaveLogs from '../../Hooks/useSaveLogs';
import { useToast } from '../../ToastProvider';
import { ToastContainer, toast } from 'react-toastify';
import { sendNotification } from '../../Hooks/useNotification';
import axiosInstance from '../../axiosinstance';
import { NotificationContext } from "../../Context/NotificationContext";
import { useNavigate } from 'react-router-dom';
// import Browser from './Browser';
export default function BackupConfiguration({
  backupName,
  setBackupName,
  selectedDestination,
  setSelectedDestination,
  backupType,
  setBackupType,
  setFileExtension,
  setEndPoint,
  setSourceCheck,
  endPoint

}) {
  const { errorPopupStoreData, setErrorPopupStoreData, getRestoreData, destinationNamePayload, backupIndex, setBackupIndex, sourceData, setSourceData, CollectFormData, setCollectFormData, nextruntimeCheckList, setnextruntimeCheckList, setDestinationNamePayload } = useContext(Backupindex);
  const { setNotificationData, } = useContext(NotificationContext);
  const [checkBackIndex, setCheckBackIndex] = useState()
  const [currentStep, setCurrentStep] = useState(0);
  const [destinationsdata, setDestinationsdata] = useState();
  const [buttontype, setButtontype] = useState("full");
  const [fileNameSend, setFileNameSend] = useState('');
  const [showSubmitGif, setShowSubmitGif] = useState(false)
  const [dstLoader, setDstLoader] = useState(false);
  const { showToast } = useToast();
  const navigate = useNavigate();
  // const [storageStates, setStorageStates] = useState({
  //   LocalStorage: true,
  //   GoogleDrive: true,
  //   AwsS3: true,
  //   //Dropbox: false,
  //   Azure: true,
  //   // NasUNC: false,
  //   UNC: true,
  //   // ApnaCloud: false
  //   OneDrive: true
  // });
  const storageStates = decryptData(localStorage.getItem("storageStates"));

  const [gdriveModel, setGdriveModel] = useState(false);
  const [gdriveModelData, setGdriveModelData] = useState('');
  function onClose() {
    setShowNasPopup(false)
  }
  const [destinationName, setDestinationName] = useState('');

  const [destinationsMapData, setDestinationsMapData] = useState(null);
  const [popup, setPopup] = useState({ visible: false, message: "" });
  const [errorPopup, setErrorPopup] = useState({ visible: false, message: "" });

  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [backuptypejob, setbackuptypejob] = useState('instant');
  const [sendBackType, setSendBackType] = useState('full')

  const [loading, setLoading] = useState(true);
  const [nextruntimedata, setnextruntimedata] = useState('');
  const [showNasPopup, setShowNasPopup] = useState(false);
  const isSubmittingInstantBackup = useRef(false);
  const [selected, setSelected] = useState("include"); // default: include is active

  const handleInclude1 = () => {
    setSelected("include");
    // your logic here
  };



  const handleExclude1 = () => {
    setSelected("exclude");
  };
  const handleRowClick = (endpoint) => {
    setSelectedEndpoint(endpoint);
  };

  const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();

  const handleContinue = () => {
    const form_val = sessionStorage.getItem("encryptedBackupData");
    const decrypted = decryptData(form_val);
    const backupName1 = decrypted?.backupName;
    const selectedDestination1 = decrypted?.selectedDestination;
    const backupType1 = decrypted?.backupType;
    if (!backupName1) {
      setErrorPopup({ visible: true, message: "Please First Enter Your Backup Name" });
    } else if (!selectedDestination1) {
      setErrorPopup({ visible: true, message: "Please Select Your Destination" });
    } else if (!backupType1) {
      setErrorPopup({ visible: true, message: "Please Select Your BackUpType" });
    } else {
      if (currentStep < 3) {
        setCurrentStep((prev) => prev + 1);
      }
    };
  }

  // const handleScheduleBackup = () => {

  //   if (!sourceData.length > 0) {
  //     setErrorPopupStoreData(true);
  //     setErrorPopup({ visible: true, message: "Please select a file for backup" });
  //     return
  //   }
  //   if (currentStep < 3) {
  //     setCurrentStep((prev) => prev + 1);
  //   }
  //   const now = new Date();
  //   now.setMinutes(now.getMinutes() + 1); // Add 1 minute
  //   const isoString = now.toISOString();
  //   const rendomString = generateRandomString();
  //   let destStorageToUse = destinationName;
  //   if (destinationName === "NAS/UNC") {
  //     const storeagedata = JSON.parse(localStorage.getItem("storage"));
  //     setDestinationName(storeagedata);
  //     destStorageToUse = storeagedata; // ✅ Use this in newformdata instead
  //   }
  //   const newformdata = {
  //     backupProfileId: rendomString,
  //     bkupType: buttontype,
  //     deststorageType: destStorageToUse,
  //     name: backupName,
  //     nextTime: isoString,
  //     runEveryUnit: backuptypejob,
  //     selectedExtensions: [fileNameSend],
  //     selectedPaths: getRestoreData,
  //     selectedSystems: [endPoint],
  //   }
  //   setCollectFormData(newformdata);
  // };

  useEffect(() => {
    // Always reset destination when entering Backup page
    setSelectedDestination("On-Premise");
    setDestinationNamePayload("LAN");

    // Clear persisted destination
    sessionStorage.removeItem("encryptedBackupData");
  }, []);


  const handleScheduleBackup = () => {

    if (!sourceData.length > 0) {
      setErrorPopupStoreData(true);
      setErrorPopup({ visible: true, message: "Please select a file for backup" });
      return
    }
    if (currentStep < 3) {
      setCurrentStep((prev) => prev + 1);
    }
    const now = new Date();
    now.setMinutes(now.getMinutes() + 1); // Add 1 minute
    const isoString = now.toISOString();
    const rendomString = generateRandomString();
    let destStorageToUse = destinationName;
    if (destinationName === "UNC") {
      const storeagedata = JSON.parse(localStorage.getItem("storage"));
      setDestinationName(storeagedata);
      destStorageToUse = storeagedata; // ✅ Use this in newformdata instead
    }

    const extensionsArray = fileNameSend
      ? fileNameSend.split(',').map(ext => ext.trim()).filter(ext => ext !== '')
      : [];

    const paths = Array.isArray(getRestoreData) ? getRestoreData : (getRestoreData ? [getRestoreData] : []);
    const selectedPathsDeduped = [...new Set(paths)];

    const newformdata = {
      backupProfileId: rendomString,
      bkupType: buttontype,
      deststorageType: destStorageToUse || null,
      name: backupName,
      nextTime: isoString,
      runEveryUnit: backuptypejob,
      selectedExtensions: extensionsArray,
      selectedPaths: selectedPathsDeduped,
      selectedSystems: [endPoint],
    }
    setCollectFormData(newformdata);
  };

  useEffect(() => {
    setFileExtension(fileNameSend)
  }, [fileNameSend]);
  useEffect(() => {
    setCurrentStep(backupIndex?.step);
  }, [backupIndex]);

  useEffect(() => {
    const formData = {
      backupName,
      selectedDestination,
      backupType,
    };
    const encrypted = encryptData(formData);
    sessionStorage.setItem("encryptedBackupData", encrypted);
  }, [backupName, selectedDestination, backupType]);

  useEffect(() => {
    const encrypted = sessionStorage.getItem("encryptedBackupData");
    if (encrypted) {
      const decrypted = decryptData(encrypted);

      if (decrypted) {
        setBackupName(decrypted.backupName || "");
        setSelectedDestination(decrypted.selectedDestination || "");
        setBackupType(decrypted.backupType || "");
      }
    }
  }, []);

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleNameChange = (e) => {
    if (e.target.value.length <= 30) {
      setBackupName(e.target.value);
    }
  };

  const accessToken = localStorage.getItem("AccessToken");

  const fetchData = async (selectedIP, path) => {
    try {
      setLoading(true);

      const response = await axiosInstance.post(`${config.API.Server_URL}api/browse`, {
        path: path || "",
        node: ""
      }, {
        headers: {
          "Content-Type": "application/json",
          token: accessToken
        }
      });

      const serverData = response.data;
      // Update the state with the merged data
      setData(mergedData);
    } catch (error) {
      // Handle 500 status specifically
      if (error.response?.status === 500) {
        console.error('Server error: 500 - Internal Server Error');
        return; // Skip processing if there's a 500 error
      }

      // Optionally log the error or handle it differently
      console.error('An error occurred:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    async function FetchApi() {
      setDstLoader(true);
      try {
        const response = await axiosInstance.post(`${config.API.FLASK_URL}/dststorage`, storageStates, {
          headers: {
            'Content-Type': 'application/json',
            'token': `${accessToken}`,
          },
        });
        // const parseData = JSON.parse(response?.config?.data);
        setDestinationsdata(response?.data?.storageStates);

        setDstLoader(false);
      } catch (error) {
        console.error('Error during form submission:', error.response ? error.response.data : error.message);
      }
      finally {
        setDstLoader(false);
      }
    }
    FetchApi();

  }, []);

  function generateRandomString(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }


  useEffect(() => {
    if (!destinationsdata) return;
    const destinations = [
      { name: 'On-Premise', image: LocalIcon },
      { name: 'Google Drive', image: GoogleDriveIcon },
      { name: 'One Drive', image: OneDriveIcon },
      { name: 'AWS', image: AWSIcon },
      { name: 'Azure', image: AzureIcon },
      { name: 'NAS/UNC', image: NASIcon }
    ];

    // Mapping `name` to `obj` key
    const keyMap = {
      'On-Premise': 'LocalStorage',
      'Google Drive': 'GoogleDrive',
      'One Drive': 'OneDrive',
      'AWS': 'AwsS3',
      'Azure': 'Azure',
      'NAS/UNC': 'UNC'
    };

    const result = destinations.map(dest => {
      const key = keyMap[dest.name];
      return {
        name: dest.name,
        image: dest.image,
        showvalue: destinationsdata[key]
      };
    });

    setDestinationsMapData(result)

  }, [destinationsdata])
  useEffect(() => {
    // fetchData();
  }, [])



  function HandleButtonState(data) {
    setBackupType(data);
    switch (data) {
      case "Full Backup":
        setButtontype("full");
        setSendBackType('full')
        break;
      case "Incremental Backup":
        setButtontype("incremental");
        setSendBackType("incremental")
        break;
      case "Differential Backup":
        setButtontype("differential");
        setSendBackType("differential");
        break;
      default:
        break;
    }
  }


  function handleInclude(e) {
    e.preventDefault();
    localStorage.setItem('Includexcludevalue', JSON.stringify(true));
  }
  function handleExclude(e) {
    e.preventDefault();
    localStorage.setItem('Includexcludevalue', JSON.stringify(false));
  }



  function HandleDist(name) {
    if (name?.name === "NAS/UNC" || name?.name === "On-Premise") {
      setGdriveModel(false);
      if (name?.name === "NAS/UNC") {
        setShowNasPopup(true);
      } else {
        setDestinationNamePayload("LAN");
        setDestinationName(name?.name);
        setSelectedDestination(name?.name);
      }
    } else {
      // ✅ DON'T set destinationNamePayload here - let GDriveModal handle it after validation
      // Only set temporary data for the modal
      setGdriveModelData(name);
      setGdriveModel(true);
      // Don't set these until validation passes in GDriveModal
    }
  }

  // function HandleDist(name) {
  //   if (name?.name == "One Drive") {
  //     setDestinationNamePayload("ONEDRIVE");
  //   }
  //   else if (name?.name == "On-Premise") {
  //     setDestinationNamePayload("LAN");
  //   }
  //   else if (name?.name == "Google Drive") {
  //     setDestinationNamePayload("GDRIVE");
  //   }

  //   else if (name?.name == "AWS") {
  //     setDestinationNamePayload("AWSS3");
  //   }
  //   else if (name?.name == "Azure") {
  //     setDestinationNamePayload("AZURE");
  //   }

  //   else if (name?.name == "NAS/UNC") {
  //     setDestinationNamePayload("UNC");
  //   }
  //   if (name?.name === "NAS/UNC" || name?.name === "On-Premise") {
  //     setGdriveModel(false);
  //     if (name?.name === "NAS/UNC") {
  //       setShowNasPopup(true);
  //     }
  //   }
  //   else {
  //     setGdriveModelData(name);
  //     setGdriveModel(true);
  //   }
  //   setDestinationName(name?.name);
  //   setSelectedDestination(name?.name);
  // }

  const handleinstantbackup = async () => {
    if (!sourceData.length > 0) {
      setErrorPopupStoreData(true);
      setErrorPopup({ visible: true, message: "Please select a file for backup" });
      return "";
    }

    // Prevent duplicate submission (e.g. double-click before state updates)
    if (isSubmittingInstantBackup.current) {
      return;
    }
    isSubmittingInstantBackup.current = true;
    setShowSubmitGif(true);

    // Declared outside try so catch block can access it for error messages
    let newformdata = null;

    try {
      setbackuptypejob('instant');
      const now = new Date();
      now.setMinutes(now.getMinutes() + 1); // Add 1 minute
      const isoString = now.toISOString();  // ISO format
      setnextruntimedata(isoString);
      const rendomString = generateRandomString();

      let destStorageToUse = destinationName;
      if (destinationName === "UNC" || destinationName === "NAS/UNC") {
        const storeagedata = JSON.parse(localStorage.getItem("storage"));
        setDestinationName(storeagedata);
        destStorageToUse = storeagedata; // ✅ Use this in newformdata instead
      }

      const extensionsArray = fileNameSend
        ? fileNameSend.split(',').map(ext => ext.trim()).filter(ext => ext !== '')
        : [];

      // Dedupe paths so same folder is not scheduled twice in one request
      const paths = Array.isArray(getRestoreData) ? getRestoreData : (getRestoreData ? [getRestoreData] : []);
      const selectedPathsDeduped = [...new Set(paths)];

      newformdata = {
        backupProfileId: rendomString,
        bkupType: sendBackType,
        deststorageType: destStorageToUse || null,
        name: backupName,
        nextTime: isoString,
        runEveryUnit: backuptypejob,
        sc: null,
        selectedExtensions: extensionsArray,
        selectedPaths: selectedPathsDeduped,
        selectedSystems: [endPoint],
        storageType: destinationNamePayload
      };

      const response = await axiosInstance.post(`${config.API.Server_URL}/backupprofilescreate`, newformdata, {
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 120000, // 2 min - server may wait for client response
      });

      // Success handling
      sendNotification(`✅ ${newformdata?.name} Instant Backup Schedule on ${newformdata?.selectedSystems[0]}`)
      const downloadEvent = `${newformdata?.name} Instant Backup Schedule on ${newformdata?.selectedSystems[0]}`;
      handleLogsSubmit(downloadEvent);

      setShowSubmitGif(false);
      setPopup({ visible: true, message: "Backup Schedule Successful" });

      const Notification_local_Data = {
        id: Date.now(), // unique ID
        message: `✅ ${newformdata?.name} Backup Schedule on ${newformdata?.selectedSystems[0]}`,
        timestamp: new Date(),
        isRead: false,
      };

      // Encrypt the data before saving
      const encrypted_Data = encryptData(JSON.stringify(Notification_local_Data));
      // toast.success(`${newformdata?.name} Backup Schedule on ${newformdata?.selectedSystems[0]}`);
      showToast(`${newformdata?.name} Instant Backup Schedule on ${newformdata?.selectedSystems[0]}`)
      setNotificationData((prev) => [...prev, Notification_local_Data]);
      sessionStorage.setItem("notification_Data", encrypted_Data);
      sessionStorage.setItem("show_notification_Data", true);

    } catch (error) {
      console.error("Failed to create backup profile:", error);

      setShowSubmitGif(false);

      const failMessage = `❌ ${newformdata?.name} Instant Backup failed to Schedule on ${newformdata?.selectedSystems?.[0] ?? "endpoint"}`;
      const Notification_local_Data = {
        id: Date.now(), // unique ID
        message: failMessage,
        timestamp: new Date(),
        isRead: false,
      };
      sendNotification(failMessage);
      const encrypted_Data = encryptData(JSON.stringify(Notification_local_Data));
      showToast(failMessage, "error");
      setNotificationData((prev) => [...prev, Notification_local_Data]);
      sessionStorage.setItem("notification_Data", encrypted_Data);
      sessionStorage.setItem("show_notification_Data", true);
      setPopup({ visible: true, message: "Something Went Wrong" });
    } finally {
      isSubmittingInstantBackup.current = false;
      setShowSubmitGif(false);
    }
  };



  const closePopup = () => {
    setCollectFormData('');
    // setCurrentStep(0);
    sessionStorage.setItem("encryptedBackupData", "");
    setBackupName('')
    setSelectedDestination('')
    setBackupType('')
    setFileExtension('')
    setEndPoint('')
    setSourceCheck('');
    setSourceData('')
    setPopup({ visible: false, message: "" });
    if (onClose) {
      onClose();
    }
    // location.href = "/progress"
    navigate("/progress")
  };
  const ErrorclosePopup = () => {
    setPopup({ visible: false, message: "" });
    setErrorPopup(false)
    // if (onClose) {
    //   onClose();
    // }
  }


  const closeGdrivePopup = () => {
    setGdriveModel(false)
  }
  return (
    <>
      <div className='bg-white p-1 rounded shadow space-y-6 mt-2' style={{ marginTop: "3%" }}>
        <ProgressTracker currentStep={currentStep} />

      </div>
      <div className="bg-white p-2 rounded shadow space-y-3 mt-2 backupinfo" style={{ marginTop: "13px" }}>
        {currentStep === 0 && (
          <>
            {/* <div className="flex justify-between items-center">
                <h2 className="font-semibold text-lg">Backup Information</h2>

              </div> */}

            <div className="relative w-full mt-1">
              {/* <input
                  type="text"
                  value={backupName}
                  onChange={handleNameChange}
                  required
                  className="peer border border-gray-300 rounded px-3 pt-2 pb-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
                /> */}
              <div className="relative">
                <input type="text"
                  value={backupName}
                  onChange={handleNameChange}
                  required
                  id="floating_outlined" style={{ border: "2px solid #cbc9c9" }} className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer" placeholder=" " />
                <label htmlFor="floating_outlined" className="absolute text-sm border-gray-300 text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white dark:bg-gray-900 px-2 peer-focus:px-2 peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto start-1 backup_lable">Backup Name (max 30 characters)</label>
              </div>
              {/* <label className={`absolute left-3 text-gray-500 transition-all duration-200
                ${backupName ? 'text-xs top-1' : 'text-sm top-3.5'} peer-focus:text-xs peer-focus:top-1`}>
                  Backup Name (max 30 characters)
                </label> */}
            </div>

            <div className="mt-0">
              <h3 className="font-medium mb-2">Choose Destination</h3>
              <div className="grid grid-cols-2 sm:grid-cols-6 gap-4">
                {dstLoader ? (<div className="flex items-center justify-center col-span-full h-24">
                  <Loader2 className="animate-spin h-6 w-6 text-blue-500" />
                  <span className="ml-2 text-sm text-gray-600">Loading destinations...</span>
                </div>
                ) :

                  destinationsMapData?.some(dest => dest.showvalue) ? (
                    destinationsMapData
                      .filter(dest => dest.showvalue)
                      .map((dest, idx) => (
                        <div
                          key={idx}
                          onClick={() => HandleDist(dest)}
                          className={`cursor-pointer border rounded-lg p-0 flex flex-col items-center justify-center text-center shadow-sm transition
                        ${selectedDestination === dest.name ? 'border-blue-500 bg-blue-50' : 'border-gray-300'} destinationtype`}
                        >
                          <img
                            src={dest.image}
                            alt={dest.name}
                            className="w-10 h-12 mb-0"
                          />
                          <div className="">
                            <span className="text_drive font-semibold">{dest.name}</span>
                          </div>
                        </div>
                      ))
                  ) : (
                    <div className="text-gray-500 text-center font-medium">No destination available</div>
                  )}
              </div>
            </div>
            <div>
              <h3 className="font-medium mb-2">Select Backup Type</h3>
              <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg backuptypesec">
                {['Full Backup', 'Incremental Backup', 'Differential Backup'].map((type) => (
                  <button
                    key={type}
                    // onClick={() => setBackupType(type)}
                    onClick={() => HandleButtonState(type)}
                    className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200
                        ${backupType === type ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'}
                      `}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {currentStep === 1 && (
          <div>
            <div className="main-extension-div flex justify-between">
              <div className="extension-div">
                <h2 className="text-lg font-semibold">File Extensions</h2>
                <p className="text-sm text-gray-600">Configure file types to include.</p>
              </div>
              <div className="button-div">
                {/* <button
                  onClick={handleInclude1}
                  type="button"
                  className={`text-white font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none m-3
          ${selected === "include"
                      ? "bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                      : "bg-white text-gray-900 border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:ring-4 focus:ring-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 dark:focus:ring-gray-700"}
        `}
                >
                  Include
                </button> */}

                {/* <button
                  onClick={handleExclude1}
                  type="button"
                  className={`text-white font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none
          ${selected === "exclude"
                      ? "bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                      : "bg-white text-gray-900 border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:ring-4 focus:ring-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 dark:focus:ring-gray-700"}
        `}
                >
                  Exclude
                </button> */}
              </div>
            </div>
            <FileExtensions setFileNameSend={setFileNameSend} />
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <h2 className="text-lg font-semibold">Step 3: Schedule Settings</h2>
            <p className="text-sm text-gray-600">Select Your EndPoint</p>
            <Endpoint setEndPoint={setEndPoint} setSourceCheck={setSourceCheck} />
          </div>
        )}

        {currentStep === 3 && (
          <div>
            <h2 className="text-lg font-semibold">Step 4: Review & Confirm</h2>
            <p className="text-sm text-gray-600">Schedule Your Backup Time</p>
            <div className="resechdule-section">
              <div className="backup-rescheduler">
                <Resecheduler setBackupName={setBackupName} setSelectedDestination={setSelectedDestination} setBackupType={setBackupType} setFileExtension={setFileExtension} setEndPoint={setEndPoint} setSourceCheck={setSourceCheck} buttontype={buttontype} handlePrevious={handlePrevious} currentStep={currentStep} />
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-around pt-4">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="px-4 py-2 rounded-md bg-gray-300 hover:bg-gray-400 text-sm font-medium disabled:opacity-50"
          >
            Previous
          </button>
          <div>  {currentStep === 2 ? "" : <button
            onClick={handleContinue}
            disabled={currentStep === 3}
            className="px-4 py-2 rounded-md bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium disabled:opacity-50"
          >
            Continue
          </button>}

            {sourceData?.length > 0 && currentStep === 2 ?
              <div>
                <button
                  type="button"
                  onClick={handleinstantbackup}
                  disabled={showSubmitGif}
                  // disabled={currentStep === 2}
                  style={{ marginLeft: "15px" }}
                  className="px-4 py-2 rounded-md bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium disabled:opacity-50 "
                >
                  Instant Backup Job
                </button>

                <button
                  disabled={currentStep === 3}
                  onClick={handleScheduleBackup}
                  style={{ marginLeft: "13px" }}
                  className="px-4 py-2 rounded-md bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium disabled:opacity-50"
                >
                  Save and Schedule
                </button>
              </div>
              : ""}
          </div>

        </div>
      </div>
      {showNasPopup ? <Las
        setShowNasPopup={setShowNasPopup}
        onClose={onClose}
        setDestinationName={setDestinationName}
        setSelectedDestination={setSelectedDestination}
        setDestinationNamePayload={setDestinationNamePayload}
      /> : ""}
      {showSubmitGif && (
        <Gif />
      )}

      {popup.visible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000]">
          <div className="bg-white rounded-lg p-6 shadow-xl text-center" style={{ marginTop: "85px" }}>
            <p className="text-lg font-semibold mb-4">{popup.message}</p>
            <button
              onClick={closePopup}
              className="px-8 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Ok
            </button>
          </div>
        </div>
      )}

      {errorPopup.visible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000]">
          <div className="bg-white rounded-lg p-6 shadow-xl text-center" >
            <p className="text-lg font-semibold mb-4">{errorPopup.message}</p>
            <button
              onClick={ErrorclosePopup}
              className="px-8 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Ok
            </button>
          </div>
        </div>
      )}

      {gdriveModel && <GDriveModal
        closeGdrivePopup={closeGdrivePopup}
        gdriveModelData={gdriveModelData}
        setDestinationName={setDestinationName}
        setSelectedDestination={setSelectedDestination}
        setDestinationNamePayload={setDestinationNamePayload}
        destinationPayload={gdriveModelData?.payload}
      />}
      {/* <ToastContainer position="top-right" autoClose={3000} /> */}

    </>
  );
}