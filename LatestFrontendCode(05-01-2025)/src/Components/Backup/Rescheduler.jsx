import React, { useState, useEffect, useRef, useContext } from "react";
import "./Rescheduler.css";
// import SUBMIT from "../../../Image/uploading.gif"; // Assuming this is for a loading indicator
import { Pointer, X, User, Database, Settings, FileText } from 'lucide-react'; // Added icons for the preview section
import config from "../../config";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { Backupindex } from "../../Context/Backupindex";
import SelectEndpointPopup from "../Restore/SelectEndpointPopup";
import { encryptData } from "./encryptionUtils";
import Gif from "./Gif";
import CryptoJS from "crypto-js";
import useSaveLogs from "../../Hooks/useSaveLogs";
import { ToastContainer, toast } from 'react-toastify';
import { useToast } from "../../ToastProvider";
import axios from "axios";
import axiosInstance from "../../axiosinstance";
import { NotificationContext } from "../../Context/NotificationContext";
import { sendNotification } from "../../Hooks/useNotification";
import { useNavigate } from "react-router-dom";
import RepoIcon from "../Reports/Jobs/RepoIcon";

function decryptData(encryptedData) {
  if (!encryptedData) return "";
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, "1234567890");
    const decrypted = bytes.toString(CryptoJS.enc.Utf8);
    return decrypted || "";
  } catch (error) {
    console.error("Decryption error:", error);
    return "";
  }
}


function Rescheduler({ action, jobName, jobId, agent, onClose, setShowNasPopup, setBackupName, buttontype, setSelectedDestination, setBackupType, setFileExtension, setEndPoint, setSourceCheck, handlePrevious, currentStep }) {
  // Helper function to format a Date object into a YYYY-MM-DDTHH:MM string (local time)
  const { CollectFormData, setSourceData, setCollectFormData, sourceData, selectedEndpointName, destinationNamePayload } = useContext(Backupindex);
  const { setNotificationData, notificationData, jobNotificationName } = useContext(NotificationContext);
  const formatLocalDateToHTMLInput = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const { showToast } = useToast();
  const navigate = useNavigate();

  // Function to set current date and time in the correct format for datetime-local
  const setCurrentDateTime = () => {
    const now = new Date();
    return formatLocalDateToHTMLInput(now);
  };
  const isWeekend = (dateInput) => {
    const date = new Date(dateInput);
    const day = date.getDay(); // 0 = Sunday, 6 = Saturday
    return day === 0 || day === 6;
  };

  const setOneMinuteAhead = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 1); // ADD +1 MINUTE
    return formatLocalDateToHTMLInput(now);
  };



  const [showSubmitGif, setShowSubmitGif] = useState(false);
  const [isWeekendDay, setIsWeekendDay] = useState(false);
  const [endPointListPopup, setEndPointListPopup] = useState(true);
  const [showRestorePopup, setShowRestorePopup] = useState(false);
  const [popupTime, setPopupTime] = useState({ visible: false, message: "" });
  const [destinationName, setDestinationName] = useState('');

  const [formData, setFormData] = useState({
    automaticBackup: false,
    nextTime: setOneMinuteAhead(), // Initialize with current local time string
    runAgainEvery: 1,
    runEveryUnit: "days",
    allowedDays: {
      monday: false,
      tuesday: false,
      wednesday: false,
      thursday: false,
      friday: false,
      saturday: false,
      sunday: false,
    },
    selectedSystems: [],
  });

  const inputRef = useRef(null);
  const [popup, setPopup] = useState({ visible: false, message: "" });
  const [submitting, setSubmitting] = useState(false);
  const accessToken = localStorage.getItem('AccessToken');
  // selectedDate now consistently stores a Date object for react-datepicker
  const [selectedDate, setSelectedDate] = useState(() => {
    const d = new Date();
    d.setMinutes(d.getMinutes() + 1);
    return d;
  });
  // Initialize with current Date object
  const [sendDate, setSendDate] = useState('');

  const [isSaturday, setIsSaturday] = useState('');
  const [isSunday, setIsSunday] = useState('');
  const [applyOnSameProfile, setApplyOnSameProfile] = useState(false);


  function isSaturdayCheck(dateStr) {
    return new Date(dateStr).getDay() === 6;
  }

  function isSundayCheck(dateStr) {
    return new Date(dateStr).getDay() === 0;
  }

  const hasMounted = useRef(0); // Change to counter instead of boolean

  useEffect(() => {
    hasMounted.current += 1; // Increment counter on each render

    if (hasMounted.current <= 2) { // Skip first AND second render
      return;
    }

    if (selectedDate && selectedDate < new Date()) {
      setPopupTime({
        visible: true,
        message: "Selected time cannot be in the past",
      });
    } else {
      setPopupTime({ visible: false, message: "" });
    }
  }, [selectedDate]);


  useEffect(() => {
    if (selectedDate) {
      const result = isWeekend(selectedDate);
      const result1 = isSaturdayCheck(selectedDate);
      const result2 = isSundayCheck(selectedDate);
      setIsWeekendDay(result);
      setIsSaturday(result1);
      setIsSunday(result2);
    }
  }, [selectedDate]);


  useEffect(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 1);
    setSelectedDate(now);

    const today = now.toLocaleString("en-us", { weekday: "long" }).toLowerCase(); // e.g., "saturday"

    const defaultAllowedDays = {
      monday: true,
      tuesday: true,
      wednesday: true,
      thursday: true,
      friday: true,
      saturday: false,
      sunday: false,
    };

    // If today is saturday or sunday, set it to true
    if (today === 'saturday') defaultAllowedDays.saturday = true;
    if (today === 'sunday') defaultAllowedDays.sunday = true;

    setFormData(prev => ({
      ...prev,
      nextTime: formatLocalDateToHTMLInput(now),
      allowedDays: defaultAllowedDays,
    }));

    const handleClickOutside = (event) => {
      if (inputRef.current && !inputRef.current.contains(event.target)) {
        // inputRef.current.blur();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const closePopupTime = () => {
    setPopupTime({ visible: false, message: "" });
  };

  const updateCheckedDay = (dateString) => {
    const dayOfWeek = new Date(dateString).toLocaleString("en-us", { weekday: "long" }).toLowerCase();
    const newAllowedDays = { ...formData.allowedDays };

    // Recalculate for this date directly:
    const isSat = new Date(dateString).getDay() === 6;
    const isSun = new Date(dateString).getDay() === 0;

    if (formData.runEveryUnit === "days") {
      ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].forEach(day => {
        newAllowedDays[day] = true;
      });
      newAllowedDays['saturday'] = isSat;
      newAllowedDays['sunday'] = isSun;
    } else if (formData.runEveryUnit === "months") {
      ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].forEach(day => {
        newAllowedDays[day] = true;
      });
      newAllowedDays['saturday'] = isSat;
      newAllowedDays['sunday'] = isSun;
    } else if (formData.runEveryUnit === "weeks") {
      Object.keys(newAllowedDays).forEach(day => {
        newAllowedDays[day] = false;
      });
      newAllowedDays[dayOfWeek] = true;
    }

    setFormData(prev => ({
      ...prev,
      allowedDays: newAllowedDays
    }));
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const inputValue = type === "checkbox" ? checked : value;

    setFormData((prevFormData) => {
      const newFormData = {
        ...prevFormData,
        [name]: inputValue,
      };

      if (name === "runEveryUnit") {
        if (value === "days") {
          newFormData.allowedDays = {
            monday: true,
            tuesday: true,
            wednesday: true,
            thursday: true,
            friday: true,
            saturday: false,
            sunday: false,
          };
        } else if (value === "weeks") {
          // When switching to weeks, all days should be false initially, user picks one
          newFormData.allowedDays = {
            monday: false,
            tuesday: false,
            wednesday: false,
            thursday: false,
            friday: false,
            saturday: false,
            sunday: false,
          };
          // If a date is already selected, set the corresponding day for "weeks"
          if (newFormData.nextTime) {
            const selectedDayOfWeek = new Date(newFormData.nextTime).toLocaleString("en-us", { weekday: "long" }).toLowerCase();
            newFormData.allowedDays[selectedDayOfWeek] = true;
          }
        } else if (value === "months") {
          // When switching to months, default to weekdays true
          newFormData.allowedDays = {
            monday: true,
            tuesday: true,
            wednesday: true,
            thursday: true,
            friday: true,
            saturday: false,
            sunday: false,
          };
          // If a date is already selected, set Saturday/Sunday based on it for "months"
          if (newFormData.nextTime) {
            const selectedDayOfWeek = new Date(newFormData.nextTime).toLocaleString("en-us", { weekday: "long" }).toLowerCase();
            newFormData.allowedDays['saturday'] = selectedDayOfWeek === 'saturday';
            newFormData.allowedDays['sunday'] = selectedDayOfWeek === 'sunday';
          }
        }
      }

      if (name === "nextTime") {
        // This block is primarily for the HTML datetime-local input
        const date = new Date(value); // This parses the local string into a Date object (in local time)
        const dayOfWeek = date.toLocaleString("en-us", { weekday: "long" }).toLowerCase();

        if (newFormData.runEveryUnit === "weeks") {
          Object.keys(newFormData.allowedDays).forEach(day => {
            newFormData.allowedDays[day] = false;
          });
          newFormData.allowedDays[dayOfWeek] = true;
        } else if (newFormData.runEveryUnit === "months") {
          newFormData.allowedDays = {
            monday: true,
            tuesday: true,
            wednesday: true,
            thursday: true,
            friday: true,
            saturday: dayOfWeek === 'saturday',
            sunday: dayOfWeek === 'sunday',
          };
        }
        // Also update selectedDate for react-datepicker when HTML input changes
        setSelectedDate(date);
      }

      return newFormData;
    });
  };

  const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();

  const handleChangeEvent = (e) => {
    const selectedTime = new Date(e.target.value); // Interprets value as local time
    const currentTime = new Date();

    if (selectedTime < currentTime) {
      // alert("You cannot select a past date and time.");
      const now = new Date();
      setSelectedDate(now); // Reset react-datepicker's date
      setFormData(prev => ({
        ...prev,
        nextTime: formatLocalDateToHTMLInput(now) // Reset HTML input's value
      }));
      return;
    }

    // Update selectedDate for react-datepicker and then trigger general handleChange
    setSelectedDate(selectedTime);
    updateCheckedDay(e.target.value); // Pass the local string
    setFormData(prev => ({
      ...prev,
      nextTime: e.target.value // Keep the HTML input's value as is (local string)
    }));
    localStorage.setItem('schedulerTime', encryptData(JSON.stringify({ schedulerValue: true })));
  };

  const handleDateChange = (newDate) => { // newDate is a Date object (local time) from DatePicker
    if (newDate < new Date()) {
      // alert("You cannot select a past date and time.");
      const now = new Date();
      setSelectedDate(now); // Reset to current Date object for DatePicker
      setFormData(prev => ({
        ...prev,
        nextTime: formatLocalDateToHTMLInput(now) // Reset HTML input string based on current local Date
      }));
      return;
    }
    setSelectedDate(newDate); // Update selectedDate for React DatePicker
    const formattedDateForHtmlInput = formatLocalDateToHTMLInput(newDate); // Format for HTML input
    setFormData(prev => ({
      ...prev,
      nextTime: formattedDateForHtmlInput // Set the HTML input value to local time string
    }));
    updateCheckedDay(formattedDateForHtmlInput); // Update allowed days based on this local string
    localStorage.setItem('schedulerTime', encryptData(JSON.stringify({ schedulerValue: true })));
  };

  const handleFormChange = (updatedFormData) => {
    setFormData(updatedFormData);
  };

  const handleFormSubmit = async (event) => {
    event.preventDefault();
    if (!sourceData.length > 0) {
      setPopup({ visible: true, message: "Please select a file. If you want to proceed, click on 'EndPoint" });
      return;
    }

    setShowSubmitGif(true);

    try {
      const { nextTime, runAgainEvery, allowedDays, runEveryUnit } = formData;
      const Current_Date = setCurrentDateTime();

      const { backupProfileId, bkupType, name, selectedExtensions, selectedPaths, selectedSystems } = CollectFormData;

      let destStorageToUse = destinationNamePayload;
      if (destinationNamePayload === "UNC") {
        const storeagedata = JSON.parse(localStorage.getItem("storage"));
        setDestinationName(storeagedata);
        destStorageToUse = storeagedata; // ✅ Use this in newformdata instead
      }

      const JsonBody = {
        allowedDays,
        backupProfileId,
        bkupType,
        deststorageType: destStorageToUse || null,
        name,
        nextTime,
        runAgainEvery,
        runEveryUnit,
        sc: null,
        selectedExtensions,
        selectedPaths,
        selectedSystems: selectedEndpointName,
        storageType: destinationNamePayload
      };

      const response = await axiosInstance.post(`${config.API.Server_URL}/backupprofilescreate`, JsonBody, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      // Success handling
      const downloadEvent = `${JsonBody?.name} Backup Schedule on ${Array.isArray(JsonBody?.selectedSystems) && JsonBody.selectedSystems.length > 0
        ? JsonBody.selectedSystems.join(', ')
        : 'No endpoints selected'
        }`
        ;
      handleLogsSubmit(downloadEvent);

      setShowSubmitGif(false);
      setPopup({ visible: true, message: "Backup Schedule Successful" });

      const Notification_local_Data = {
        id: Date.now(), // unique ID
        message: `✅ ${JsonBody?.name} Backup Schedule on ${Array.isArray(JsonBody?.selectedSystems) && JsonBody.selectedSystems.length > 0
          ? JsonBody.selectedSystems.join(', ')
          : 'No endpoints selected'
          }`,
        timestamp: new Date(),
        isRead: false,
      };

      sendNotification(`✅ ${JsonBody?.name} Backup Schedule on ${Array.isArray(JsonBody?.selectedSystems) && JsonBody.selectedSystems.length > 0
        ? JsonBody.selectedSystems.join(', ')
        : 'No endpoints selected'
        }`);

      // toast.success(`${jobNotificationName} backup Job successfully rescheduled`);
      showToast(`${JsonBody?.name} Backup Schedule on ${Array.isArray(JsonBody?.selectedSystems) && JsonBody.selectedSystems.length > 0
        ? JsonBody.selectedSystems.join(', ')
        : 'No endpoints selected'
        }`);
      setNotificationData((prev) => [Notification_local_Data, ...prev]);

      // Encrypt the data before saving
      const encrypted_Data = encryptData(JSON.stringify(Notification_local_Data));
      sessionStorage.setItem("notification_Data", encrypted_Data);
      sessionStorage.setItem("show_notification_Data", true);

    } catch (error) {
      setShowSubmitGif(false);
      setPopup({ visible: true, message: "Something Went Wrong" });
      console.error("Failed to create backup profile:", error);
    }
  };

  const closePopup = () => {
    if (!sourceData.length > 0) {
      setPopup({ visible: false, message: "" });
      return
    }

    setBackupName('')
    setSelectedDestination('')
    localStorage.setItem("encryptedBackupData", "");
    setBackupType('')
    setFileExtension('')
    setEndPoint('')
    setSourceCheck('')
    setSourceData('')
    setCollectFormData('')
    setPopup({ visible: false, message: "" });
    if (onClose) {
      onClose();
    }
    // location.href = "/"
    navigate("/progress")
  };

  const HandleSubmitClick = () => {
  }

  const handleSameProfile = () => {
    setApplyOnSameProfile(true)
  }

  // Variables for the new Profile Preview Section
  const backupNamePreview = CollectFormData?.name || 'N/A';
  const backupTypePreview = CollectFormData?.bkupType || 'N/A';
  const destinationStoragePreview = destinationNamePayload || 'N/A';

  const DetailItem = ({ icon: Icon, title, value }) => (
    <div className="flex items-center space-x-3 p-2 rounded-md transition-colors">
      <Icon className="w-5 h-5 text-blue-500 flex-shrink-0" />
      <div>
        <p className="font-medium text-gray-700 text-sm">{title}</p>
        <p className="text-gray-900 text-sm font-semibold break-all">{value}</p>
      </div>
    </div>
  );

  return (
    <div className="relative sm:p-1 lg:bg-white lg:custom-max-height rounded-lg shadow-xl mx-auto" style={{ minHeight: "62vh" }}>
      <form onSubmit={handleFormSubmit} className="space-y-6" style={{ width: "100%" }}>
        {/* Main Layout: 3-column grid for larger screens */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-2" style={{ width: "100%" }}>

          {/* Column 1: Backup Profile Preview (Details) - Enhanced Look */}
          <div className="flex flex-col space-y-6">
            <div className="p-2 border border-gray-200 rounded-xl shadow-lg bg-white h-full">
              <h2 className="text-xl font-bold text-gray-800 mb-4 pb-2 border-b border-gray-200">
                Backup Profile Details
              </h2>
              <div className="space-y-0">
                <DetailItem
                  icon={User}
                  title="Name of backup"
                  value={backupNamePreview}
                />
                <DetailItem
                  icon={Settings}
                  title="Backup Type"
                  value={backupTypePreview ? backupTypePreview.charAt(0).toUpperCase() + backupTypePreview.slice(1) : ""}
                />
                <DetailItem
                  icon={(props) => (
                    <RepoIcon repo={destinationStoragePreview} {...props} />
                  )}
                  title="Storage Type"
                  value={destinationStoragePreview === "LAN" ? "On-Premise" : destinationStoragePreview === "UNC" ? "NAS/UNC" : destinationStoragePreview}
                />
                {CollectFormData?.selectedExtensions?.length > 0 &&
                  <DetailItem
                    icon={FileText}
                    title="Selected Extensions"
                    value={CollectFormData?.selectedExtensions.join(", ") || "N/A"}
                  />
                }
              </div>

            </div>

            {/* Hidden Input: Kept here for form logic consistency, though visually hidden */}
            <div style={{ display: "none" }}>
              <input
                type="datetime-local"
                name="nextTime"
                value={formData.nextTime}
                onChange={handleChangeEvent}
                min={setCurrentDateTime()} // Ensure past dates cannot be selected
              />
            </div>
          </div>


          {/* Column 2: Scheduling Frequency & Include Days */}
          <div className="flex flex-col space-y-6">

            {/* Scheduling Frequency Buttons */}
            <div className="p-2 bg-gray-100 rounded-xl shadow-inner border border-gray-200">
              <h3 className="text-base font-semibold text-gray-800 mb-1 text-center">Scheduling Frequency</h3>
              <div className="flex justify-around space-x-2">
                <button
                  type="button"
                  className={`flex-1 py-2 px-2 text-sm font-medium rounded-lg transition-all duration-200
                    ${formData.runEveryUnit === "days"
                      ? "bg-blue-600 text-white shadow-md"
                      : "text-gray-700 hover:bg-gray-200"
                    }`}
                  onClick={() => handleChange({ target: { name: "runEveryUnit", value: "days" } })}
                >
                  Daily
                </button>
                <button
                  type="button"
                  className={`flex-1 py-2 px-4 text-sm font-medium rounded-lg transition-all duration-200
                    ${formData.runEveryUnit === "weeks"
                      ? "bg-blue-600 text-white shadow-md"
                      : "text-gray-700 hover:bg-gray-200"
                    }`}
                  onClick={() => handleChange({ target: { name: "runEveryUnit", value: "weeks" } })}
                >
                  Weekly
                </button>
                <button
                  type="button"
                  className={`flex-1 py-2 px-4 text-sm font-medium rounded-lg transition-all duration-200
                    ${formData.runEveryUnit === "months"
                      ? "bg-blue-600 text-white shadow-md"
                      : "text-gray-700 hover:bg-gray-200"
                    }`}
                  onClick={() => handleChange({ target: { name: "runEveryUnit", value: "months" } })}
                >
                  Monthly
                </button>
              </div>
            </div>

            {/* Include Days Checkboxes */}
            <div className="p-2 border border-gray-300 rounded-xl shadow-md flex-1 bg-white">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">Include Days</h3>
              <div className="grid grid-cols-2 gap-x-4 gap-y-3">
                {Object.keys(formData.allowedDays).map((day) => {
                  const isWeekday = ["monday", "tuesday", "wednesday", "thursday", "friday"].includes(day);
                  const isChecked =
                    (formData.runEveryUnit === "days" && isWeekday) ||
                    (formData.runEveryUnit === "months" && isWeekday) ||
                    formData.allowedDays[day];

                  const isDisabled =
                    (formData.runEveryUnit === "days" && isWeekday) ||
                    (formData.runEveryUnit === "months" && isWeekday);

                  return (
                    <label key={day} className={`flex items-center text-gray-700 ${isDisabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}>
                      <input
                        type="checkbox"
                        name={day}
                        checked={isChecked}
                        onChange={() => {
                          if (!isDisabled) {
                            handleFormChange({
                              ...formData,
                              allowedDays: {
                                ...formData.allowedDays,
                                [day]: !formData.allowedDays[day],
                              },
                            });
                          }
                        }}
                        disabled={isDisabled}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 capitalize text-sm">{day}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Column 3: React DatePicker */}
          <div className="flex flex-col space-y-6">
            {/* The DatePicker must be within a container with defined height/width constraints */}
            <div className="datepicker-wrapper flex-1 flex items-center justify-center rounded-xl shadow-md border border-gray-200 bg-white overflow-hidden">
              <DatePicker
                selected={selectedDate} // Expects a Date object
                onChange={handleDateChange} // Provides a Date object
                showTimeSelect
                dateFormat="Pp" // Displays both date and time (including minutes)
                inline // This prop makes the calendar always visible (not in a popup)
                minDate={new Date()} // Disable past dates
                timeFormat="h:mm aa" // Ensures mere minutes are shown
                timeIntervals={1} // Ensures minute selection is available
                filterTime={(time) => time > new Date()}
                className="w-full h-full"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-evenly" style={{ marginTop: "14px" }}>

          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="px-4 py-2 rounded-md bg-gray-400 hover:bg-gray-500 text-white text-sm font-medium disabled:opacity-50 transition-colors"
          >
            Previous
          </button>

          <div>
            <button
              type="submit"
              className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium disabled:opacity-50 transition-colors"
              disabled={submitting}
              onClick={HandleSubmitClick}
              style={{ "marginRight": "15px" }}
            >
              {submitting ? "Submitting..." : "Submit"}
            </button>

            <button
              type="button"
              style={{ cursor: Pointer }}
              className="px-4 py-2 rounded-md border border-blue-600 text-blue-600 hover:bg-blue-50 text-sm font-medium transition-colors"
              onClick={handleSameProfile}
            >
              Apply Same Profile On
            </button>
          </div>
        </div>

      </form>

      {/* ... (Popups and Modals remain the same) ... */}

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

      {popupTime.visible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000]">
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

      {/* Loading Overlay */}
      {submitting && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000]">
          <div className="bg-white rounded-lg p-8 text-center shadow-xl">
            {/* You can replace this with your SUBMIT GIF if needed */}
            <div className="animate-spin w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <div className="text-lg font-medium text-gray-900">Rescheduling...</div>
          </div>
        </div>
      )}

      {applyOnSameProfile && <SelectEndpointPopup setShowRestorePopup={setShowRestorePopup} setEndPointListPopup={setEndPointListPopup} setApplyOnSameProfile={setApplyOnSameProfile} applyOnSameProfile={applyOnSameProfile} />}

      {showSubmitGif && (
        <Gif />
      )}
    </div>
  );
}

export default Rescheduler;