import React, { useState, useEffect, useRef, useContext } from "react";
import "./Rescheduler.css";
import { X, User, Settings, Database } from 'lucide-react';
import config from "../../config";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import useSaveLogs from "../../Hooks/useSaveLogs";
import { useToast } from "../../ToastProvider";
import CryptoJS from "crypto-js";
import { sendNotification } from '../../Hooks/useNotification';
import axiosInstance from "../../axiosinstance";
import { NotificationContext } from "../../Context/NotificationContext";
import AlertComponent from "../../AlertComponent";
import RepoIcon from "../Reports/Jobs/RepoIcon";

function encryptData(data) {
  const encryptedData = CryptoJS.AES.encrypt(data, "1234567890").toString();
  return encryptedData;
}

function Rescheduler({ action, jobName, jobId, agent, filteredJobsData, onClose }) {
  const formatLocalDateToHTMLInput = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const { setNotificationData } = useContext(NotificationContext);

  const setCurrentDateTime = (minutesToAdd = 1) => {
    const now = new Date(Date.now() + minutesToAdd * 60 * 1000);
    return formatLocalDateToHTMLInput(now);
  };

  const { showToast } = useToast();
  const [alert, setAlert] = useState(null);
  const inputRef = useRef(null);
  const [popup, setPopup] = useState({ visible: false, message: "" });
  const [submitting, setSubmitting] = useState(false);
  const accessToken = localStorage.getItem('AccessToken');

  const [selectedDate, setSelectedDate] = useState(new Date(Date.now() + 60 * 1000));

  const [formData, setFormData] = useState({
    automaticBackup: false,
    nextTime: setCurrentDateTime(1),
    runAgainEvery: 1,
    runEveryUnit: "days",
    allowedDays: {
      monday: false, tuesday: false, wednesday: false, thursday: false, friday: false, saturday: false, sunday: false,
    },
    selectedSystems: [],
  });

  const { handleLogsSubmit } = useSaveLogs();
  const selectedJob = filteredJobsData ? filteredJobsData.find(job => job.id === jobId) : null;

  useEffect(() => {
    const now = new Date(Date.now() + 60 * 1000);
    const today = now.toLocaleString("en-us", { weekday: "long" }).toLowerCase();

    setSelectedDate(now);
    setFormData(prev => ({
      ...prev,
      nextTime: formatLocalDateToHTMLInput(now),
      allowedDays: {
        monday: true,
        tuesday: true,
        wednesday: true,
        thursday: true,
        friday: true,
        saturday: today === "saturday",
        sunday: today === "sunday",
      }
    }));
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const formatted = formatLocalDateToHTMLInput(now);

      setSelectedDate(now);
      setFormData(prev => ({ ...prev, nextTime: formatted }));
    }, 60000);

    return () => clearInterval(interval);
  }, []);


  useEffect(() => {
    if (jobId && filteredJobsData) {
      const job = filteredJobsData.find(job => job.id === jobId);
      if (job && job.day_of_week) {
        const daysArray = job.day_of_week.split(",");
        setFormData(prev => ({
          ...prev,
          allowedDays: {
            monday: daysArray.includes("mon"),
            tuesday: daysArray.includes("tue"),
            wednesday: daysArray.includes("wed"),
            thursday: daysArray.includes("thu"),
            friday: daysArray.includes("fri"),
            saturday: daysArray.includes("sat"),
            sunday: daysArray.includes("sun"),
          }
        }));
      }
    }
  }, [jobId, filteredJobsData]);

  const handleFormChange = (updatedFormData) => {
    setFormData(updatedFormData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const inputValue = type === "checkbox" ? checked : value;

    setFormData((prevFormData) => {
      const newFormData = { ...prevFormData, [name]: inputValue };

      if (name === "runEveryUnit") {
        if (value === "days") {
          newFormData.allowedDays = { monday: true, tuesday: true, wednesday: true, thursday: true, friday: true, saturday: false, sunday: false };
        } else if (value === "weeks") {
          newFormData.allowedDays = { monday: false, tuesday: false, wednesday: false, thursday: false, friday: false, saturday: false, sunday: false };
          if (newFormData.nextTime) {
            const selectedDay = new Date(newFormData.nextTime).toLocaleString("en-us", { weekday: "long" }).toLowerCase();
            newFormData.allowedDays[selectedDay] = true;
          }
        } else if (value === "months") {
          newFormData.allowedDays = { monday: true, tuesday: true, wednesday: true, thursday: true, friday: true, saturday: false, sunday: false };
          if (newFormData.nextTime) {
            const selectedDay = new Date(newFormData.nextTime).toLocaleString("en-us", { weekday: "long" }).toLowerCase();
            newFormData.allowedDays.saturday = selectedDay === "saturday";
            newFormData.allowedDays.sunday = selectedDay === "sunday";
          }
        }
      }

      if (name === "nextTime") {
        const date = new Date(value);
        const dayOfWeek = date.toLocaleString("en-us", { weekday: "long" }).toLowerCase();
        if (newFormData.runEveryUnit === "weeks") {
          Object.keys(newFormData.allowedDays).forEach((day) => { newFormData.allowedDays[day] = false; });
          newFormData.allowedDays[dayOfWeek] = true;
        } else if (newFormData.runEveryUnit === "months") {
          newFormData.allowedDays = {
            monday: true, tuesday: true, wednesday: true, thursday: true, friday: true,
            saturday: dayOfWeek === "saturday", sunday: dayOfWeek === "sunday",
          };
        }
        setSelectedDate(date);
      }
      return newFormData;
    });
  };

  const handleDateChange = (newDate) => {
    if (newDate < new Date()) {
      setAlert({ message: "You cannot select a past date and time.", type: 'warning' });
      const now = new Date(Date.now() + 60 * 1000);
      setSelectedDate(now);
      setFormData(prev => ({ ...prev, nextTime: formatLocalDateToHTMLInput(now) }));
      return;
    }

    setSelectedDate(newDate);
    const formattedDateForHtmlInput = formatLocalDateToHTMLInput(newDate);

    setFormData(prev => {
      const updated = { ...prev, nextTime: formattedDateForHtmlInput };
      const dayOfWeek = newDate.toLocaleString("en-us", { weekday: "long" }).toLowerCase();

      if (updated.runEveryUnit === "days") {
        updated.allowedDays = {
          monday: true, tuesday: true, wednesday: true, thursday: true, friday: true,
          saturday: dayOfWeek === "saturday", sunday: dayOfWeek === "sunday",
        };
      } else if (updated.runEveryUnit === "weeks") {
        updated.allowedDays = Object.fromEntries(Object.keys(updated.allowedDays).map(d => [d, d === dayOfWeek]));
      } else if (updated.runEveryUnit === "months") {
        updated.allowedDays = {
          monday: true, tuesday: true, wednesday: true, thursday: true, friday: true,
          saturday: dayOfWeek === "saturday", sunday: dayOfWeek === "sunday",
        };
      }
      return updated;
    });

    localStorage.setItem("schedulerTime", encryptData(JSON.stringify({ schedulerValue: true })));
  };

  const handleFormSubmit = async (event) => {
    event.preventDefault();
    const { nextTime, runAgainEvery, allowedDays, runEveryUnit } = formData;
    const localDateObject = new Date(nextTime);
    const nextTimeForPayload = formatLocalDateToHTMLInput(localDateObject);

    const dataToSend = {
      nextTime: nextTimeForPayload,
      runAgainEvery,
      allowedDays,
      runEveryUnit,
      action: { action: action, jobName: jobName, jobId: jobId, agent: agent },
      jobName: {},
    };

    setSubmitting(true);
    try {
      await axiosInstance.post(`${config.API.Server_URL}/scheduler/action/reschedule`, dataToSend, {
        headers: { 'Content-Type': 'application/json', token: accessToken }
      });
      setPopup({ visible: true, message: "Job successfully rescheduled!" });
      handleLogsSubmit(`Job:${jobName} is rescheduled on ${agent}.`);

      const Notification_local_Data = { id: Date.now(), message: `✅ Job:${jobName} is rescheduled on ${agent}.`, timestamp: new Date(), isRead: false };
      showToast(`Job:${jobName} is rescheduled on ${agent}.`);
      setNotificationData((prev) => [Notification_local_Data, ...prev]);
      sendNotification(`✅ Job "${jobName}" has been rescheduled on "${agent}".`)
    } catch (error) {
      console.error("Error rescheduling job:", error);
      setPopup({ visible: true, message: "Error rescheduling the job. Please try again." });
      showToast("Error rescheduling the job", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const closePopup = () => {
    setPopup({ visible: false, message: "" });
    if (onClose) onClose();
  };

  return (
    <div className="relative w-full bg-white lg:bg-transparent mx-auto">
      <div className="flex justify-end lg:hidden mb-2">
        <button onClick={onClose} className="text-gray-500"><X size={24} /></button>
      </div>

      <form onSubmit={handleFormSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-2">

          {/* COLUMN 1: Backup Profile Details (Span 4/12) */}
          <div className="lg:col-span-4 bg-white p-2 rounded-xl border border-gray-200 shadow-sm flex flex-col h-full">
            <h2 className="text-lg font-bold text-gray-900 mb-2 pb-2 border-b border-gray-100">
              Backup Profile Details
            </h2>
            <div className="space-y-6">
              <div className="flex items-start gap-3">
                <div className="mt-1 text-blue-500"><User size={20} /></div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Name of backup</p>
                  <p className="text-sm font-semibold text-gray-800 break-all">{jobName}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-1 text-blue-500"><Settings size={20} /></div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Source Location</p>
                  <p className="text-sm font-semibold text-gray-800 break-all">{selectedJob?.src_location}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-1 text-blue-500"><RepoIcon repo={selectedJob?.repo} /></div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Repository</p>
                  <p className="text-base font-semibold text-gray-800">{selectedJob?.repo === "LAN" ? "On-Premise" : selectedJob?.repo === "UNC" ? "NAS/UNC" : selectedJob?.repo}</p>
                </div>
              </div>
            </div>
          </div>

          {/* COLUMN 2: Frequency & Days (Span 4/12) */}
          <div className="lg:col-span-3 flex flex-col gap-2 h-full">
            <div className="bg-gray-50 p-2 rounded-xl border border-gray-200 shadow-sm">
              <h3 className="text-base font-semibold text-center text-gray-800 mb-4">Scheduling Frequency</h3>
              <div className="flex bg-gray-200/50 p-1 rounded-lg">
                {["days", "weeks", "months"].map((unit) => (
                  <button
                    key={unit}
                    type="button"
                    onClick={() => handleChange({ target: { name: "runEveryUnit", value: unit } })}
                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-200 capitalize
                      ${formData.runEveryUnit === unit ? "bg-blue-600 text-white shadow-md" : "text-gray-600 hover:text-gray-900 hover:bg-white/50"}`}
                  >
                    {unit === "days" ? "Daily" : unit === "weeks" ? "Weekly" : "Monthly"}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white p-2 rounded-xl border border-gray-200 shadow-sm flex-grow">
              <h3 className="text-base font-semibold text-gray-800 mb-4">Include Days</h3>
              <div className="grid grid-cols-2 gap-y-3 gap-x-2">
                {["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].map((day) => {
                  const isWeekday = ["monday", "tuesday", "wednesday", "thursday", "friday"].includes(day);
                  const isChecked = ((formData.runEveryUnit === "days" || formData.runEveryUnit === "months") && isWeekday) ? true : formData.allowedDays[day];
                  const isDisabled = (formData.runEveryUnit === "days" && isWeekday) || (formData.runEveryUnit === "months" && isWeekday);

                  return (
                    <label key={day} className={`flex items-center gap-2 ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}>
                      <input
                        type="checkbox"
                        checked={isChecked}
                        disabled={isDisabled}
                        onChange={() => {
                          if (!isDisabled) {
                            if (formData.runEveryUnit === "weeks") {
                              handleFormChange({ ...formData, allowedDays: Object.fromEntries(Object.keys(formData.allowedDays).map((d) => [d, d === day])) });
                            } else if (formData.runEveryUnit === "days" || formData.runEveryUnit === "months") {
                              handleFormChange({ ...formData, allowedDays: { ...formData.allowedDays, [day]: !formData.allowedDays[day], monday: true, tuesday: true, wednesday: true, thursday: true, friday: true } });
                            } else {
                              handleFormChange({ ...formData, allowedDays: { ...formData.allowedDays, [day]: !formData.allowedDays[day] } });
                            }
                          }
                        }}
                        className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-600 capitalize">{day}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          </div>

          {/* COLUMN 3: Date Picker (Span 4/12) */}
          <div className="lg:col-span-5 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-auto">
            <div className="endpoint-rescheduler w-full p-0 flex-grow">
              <DatePicker
                selected={selectedDate}
                onChange={handleDateChange}
                showTimeSelect
                dateFormat="Pp"
                inline
                minDate={new Date()}
                timeFormat="h:mm aa"
                timeIntervals={1}
                filterTime={(time) => time > new Date()}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-0 pt-2 border-t border-gray-200">
          <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
          <button type="submit" disabled={submitting} className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:ring-4 focus:ring-blue-500/30 transition-all disabled:bg-gray-400">
            {submitting ? "Submitting..." : "Submit"}
          </button>
        </div>
      </form>

      {popup.visible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000]">
          <div className="bg-white rounded-lg p-6 shadow-xl text-center max-w-sm mx-4">
            <p className="text-lg font-semibold mb-4 text-gray-800">{popup.message}</p>
            <button onClick={closePopup} className="px-8 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Ok</button>
          </div>
        </div>
      )}

      {submitting && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 text-center shadow-xl">
            <div className="flex space-x-2 justify-center mb-4">
              <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"></div>
              <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <div className="text-gray-900 font-medium">Rescheduling...</div>
          </div>
        </div>
      )}

      {alert && <AlertComponent message={alert.message} type={alert.type} onClose={() => setAlert(null)} />}
    </div>
  );
}

export default Rescheduler;