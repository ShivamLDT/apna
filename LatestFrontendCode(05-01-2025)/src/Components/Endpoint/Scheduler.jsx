import React, { useState, useEffect, useContext } from 'react';
import { Backupindex } from '../../Context/Backupindex';
import config from '../../config';
import './Scheduler.css';
import Popup from './Popup';
import Rescheduler from './Rescheduler'
import RepoIcon from '../Reports/Jobs/RepoIcon';
import { ToastContainer, toast } from 'react-toastify';
import { useToast } from '../../ToastProvider';
import CryptoJS from "crypto-js";
import axios from 'axios';
import { sendNotification } from '../../Hooks/useNotification';
import axiosInstance from '../../axiosinstance';
import { NotificationContext } from "../../Context/NotificationContext";
import {
    Play,
    Pause,
    Edit3,
    Trash2,
    Search,
    Clock,
    Calendar,
    CheckCircle,
    X,
    AlertTriangle
} from 'lucide-react';
import useSaveLogs from '../../Hooks/useSaveLogs';

function encryptData(data) {
    const encryptedData = CryptoJS.AES.encrypt(data, "1234567890").toString();

    return encryptedData;
}
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

const formatDate = (dateString) => {
    const date = new Date(dateString);
    // Format date in local timezone
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const formattedDate = `${year}-${month}-${day}`;

    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const formattedTime = `${hours}:${minutes}:${seconds}`;

    return { formattedDate, formattedTime };
};

const isJobScheduledInNextFourHours = (nextRunTime) => {
    const jobTime = new Date(nextRunTime);
    const currentTime = new Date();
    const fourHoursFromNow = new Date(currentTime.getTime() + 4 * 60 * 60 * 1000);
    return jobTime > currentTime && jobTime <= fourHoursFromNow;
};

const calculateCountdown = (nextRunTime) => {
    const currentTime = new Date();
    const difference = new Date(nextRunTime) - currentTime;

    if (difference <= 1000) {
        return "Started";
    }

    const hours = Math.floor(difference / (1000 * 60 * 60));
    const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((difference % (1000 * 60)) / 1000);

    return `${hours}h ${minutes}m ${seconds}s`;
};

const isPaused = (job, countdowns) =>
    !job?.next_run_time || (countdowns?.[job.id] === "Paused");


const ConfirmationPopup = ({ onConfirm, onCancel }) => {
    const [deleteInput, setDeleteInput] = useState("");
    const [isDeleteConfirmed, setIsDeleteConfirmed] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleDeleteClick = () => {
        if (onConfirm) {
            onConfirm();
        }
        setIsDeleteConfirmed(true);
        setLoading(true);
    };

    return (
        <>
            {!isDeleteConfirmed && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                        <div className="flex items-center mb-4">
                            <AlertTriangle className="text-red-500 mr-3" size={24} />
                            <h3 className="text-lg font-semibold text-gray-900">Confirm Deletion</h3>
                        </div>
                        <p className="text-gray-600 mb-4">Are you sure you want to delete the selected job?</p>
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Type <strong>"delete my job"</strong> to confirm:
                            </label>
                            <input
                                type="text"
                                value={deleteInput}
                                onChange={(e) => setDeleteInput(e.target.value)}
                                placeholder="delete my job"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
                            />
                        </div>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={onCancel}
                                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleDeleteClick}
                                disabled={deleteInput !== "delete my job"}
                                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                            >
                                Yes, Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {isDeleteConfirmed && loading && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-8 text-center">
                        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                        <div className="text-lg font-medium text-gray-900">Deleting...</div>
                    </div>
                </div>
            )}
        </>
    );
};

const LoadingOverlay = ({ message = "Loading..." }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 text-center">
            <div className="flex space-x-2 justify-center mb-4">
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <div className="text-lg font-medium text-gray-900">{message}</div>
        </div>
    </div>
);


const SuccessPopup = ({ message, onClose, isError = false }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-sm w-full p-6 text-center">
            {isError ? (
                <X className="text-red-500 mx-auto mb-4" size={48} />
            ) : (
                <CheckCircle className="text-green-500 mx-auto mb-4" size={48} />
            )}
            <h3 className={`text-lg font-medium mb-4 ${isError ? 'text-red-700' : 'text-gray-900'}`}>
                {message}
            </h3>
            <button
                onClick={onClose}
                className={`px-6 py-2 rounded-md transition-colors ${isError
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
            >
                OK
            </button>
        </div>
    </div>
);


const RenamePopup = ({ jobName, onSubmit, onCancel }) => {
    const [newName, setNewName] = useState(jobName || '');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(newName);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Rename Job</h3>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            New Name:
                        </label>
                        <input
                            type="text"
                            value={newName}
                            onChange={(e) => setNewName(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                            required
                        />
                    </div>
                    <div className="flex gap-3 justify-end">
                        <button
                            type="button"
                            onClick={onCancel}
                            className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                            Rename
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const Scheduler = ({ jobsData = [], onClose, agent, onJobActionSuccess }) => {
    const [filteredJobsData, setFilteredJobsData] = useState([]);
    const [countdowns, setCountdowns] = useState({});
    const [selectedJob, setSelectedJob] = useState(null);
    const [isRenamePopupVisible, setRenamePopupVisible] = useState(false);
    const [showConfirmDelete, setShowConfirmDelete] = useState(false);
    const [jobsToDelete, setJobsToDelete] = useState([]);
    const [userPrivileges, setUserPrivileges] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [isPlayConfirmed, setIsPlayConfirmed] = useState(false);
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [showSuccessPopup, setShowSuccessPopup] = useState({ visible: false, isError: false });
    const [jobNewName, setJobNewName] = useState('');
    const [showReschedulerModal, setShowReschedulerModal] = useState(false);
    const { profilePic, userName, userRole, handleLogsSubmit } = useSaveLogs();
    const { setNotificationData, jobNotificationName, setJobNotificationName } = useContext(NotificationContext);
    const { showToast } = useToast();
    const defaultPrivileges = {
        agentPause: false,
        agentUpdate: false,
        agentDelete: false,
    };

    useEffect(() => {
        const storedPrivileges = decryptData(localStorage.getItem('user_privileges'));
        let parsedPrivileges = null;

        if (storedPrivileges) {
            try {
                parsedPrivileges = JSON.parse(storedPrivileges);
            } catch (error) {
                console.error('Error parsing user_privileges from localStorage:', error);
            }
        }

        const privileges = { ...defaultPrivileges };

        if (parsedPrivileges) {
            Object.keys(privileges).forEach(key => {
                if (parsedPrivileges[key] !== undefined) {
                    privileges[key] = parsedPrivileges[key];
                }
            });
        }
        else {
            privileges.agentPause = true;
            privileges.agentUpdate = true;
            privileges.agentDelete = true;
        }

        setUserPrivileges(privileges);
    }, []);

    useEffect(() => {
        if (!jobsData || !Array.isArray(jobsData)) {
            setFilteredJobsData([]);
            return;
        }

        const updatedJobsData = jobsData.map(job => {
            const currentTime = new Date();
            const jobNextRunTime = new Date(job.next_run_time);

            let countdown = "Paused";

            if (jobNextRunTime >= currentTime) {
                countdown = calculateCountdown(job.next_run_time);
            }

            return { ...job, countdown };
        });

        setFilteredJobsData(updatedJobsData);

        const initialCountdowns = {};
        updatedJobsData.forEach(job => {
            initialCountdowns[job.id] = job.countdown;
        });
        setCountdowns(initialCountdowns);

        const interval = setInterval(() => {
            setCountdowns(prevCountdowns => {
                const updatedCountdowns = { ...prevCountdowns };

                updatedJobsData.forEach(job => {
                    const currentTime = new Date();
                    const jobNextRunTime = new Date(job.next_run_time);

                    if (jobNextRunTime >= currentTime) {
                        updatedCountdowns[job.id] = calculateCountdown(job.next_run_time);
                    }
                });

                return updatedCountdowns;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, [jobsData]);

    const accessToken = localStorage.getItem('AccessToken');

    const fetchAPI = async (action, jobId, jobName, agentName, extraPayload = {}) => {
        try {
            setLoading(true);
            setIsPlayConfirmed(true); // Assuming this is for a general "processing" state

            const payload = {
                action,
                jobId,
                jobName,
                agentName,
                ...extraPayload,
            };

            const method = action === 'delete' ? 'DELETE' : 'POST';

            // const response = await axios({
            //     method: method,
            //     url: `${config.API.Server_URL}/scheduler/action`,
            //     data: payload,
            //     headers: {
            //         'Content-Type': 'application/json',
            //         token: accessToken
            //     }
            // });

            const response = await axiosInstance.post(`${config.API.Server_URL}/scheduler/action`, payload, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken
                }
            });
            // Success handling
            setSuccessMessage(`${action.charAt(0).toUpperCase() + action.slice(1)} successful!`);
            setShowSuccessPopup({ visible: true, isError: false });

            if (onJobActionSuccess) {
                onJobActionSuccess();
                const downloadEvent = `Job:${jobName} is ${action}ed.`;
                handleLogsSubmit(downloadEvent);
            }

            // Handle specific action notifications
            const actionMessage = `${action.charAt(0).toUpperCase() + action.slice(1)} successful!`;
            let notificationMessage = '';
            let toastMessage = '';

            switch (actionMessage) {
                case "Pause successful!":
                    notificationMessage = `✅ ${jobNotificationName} backup is paused`;
                    toastMessage = `${jobNotificationName} backup is paused`;
                    break;
                case "Play successful!":
                    notificationMessage = `✅ ${jobNotificationName} backup is play`;
                    toastMessage = `${jobNotificationName} backup is play`;
                    break;
                case "Rename successful!":
                    notificationMessage = `✅ ${jobNotificationName} backup is Rename successful`;
                    toastMessage = `${jobNotificationName} backup is Rename successful`;
                    break;
            }

            if (notificationMessage) {
                const Notification_local_Data = {
                    id: Date.now(),
                    message: notificationMessage,
                    timestamp: new Date(),
                    isRead: false,
                };
                // toast.success(toastMessage);
                showToast(toastMessage);
                sendNotification(notificationMessage)
                setNotificationData((prev) => [Notification_local_Data, ...prev]);
            }

            setShowSuccessPopup({ visible: true, isError: false });

        } catch (error) {
            console.error('API call error:', error);

            // Enhanced error handling
            let errorMessage = 'An error occurred. Please try again.';
            if (error.response) {
                switch (error.response.status) {
                    case 400:
                        errorMessage = 'Invalid request data';
                        break;
                    case 401:
                        errorMessage = 'Authentication required';
                        break;
                    case 403:
                        errorMessage = 'Access denied - insufficient permissions';
                        break;
                    case 404:
                        errorMessage = 'Job not found';
                        break;
                    case 500:
                        errorMessage = 'Server error occurred';
                        break;
                    default:
                        errorMessage = error.response.data?.message || 'Action failed. Please try again.';
                }
            } else if (error.request) {
                errorMessage = 'Network error - please check your connection';
            }

            setSuccessMessage(errorMessage);
            setShowSuccessPopup({ visible: true, isError: true });

            // Optional: Add error notification
            const Notification_local_Data = {
                id: Date.now(),
                message: `❌ Failed to ${action} ${jobNotificationName} backup job`,
                timestamp: new Date(),
                isRead: false,
            };
            sendNotification(`❌ Failed to ${action} ${jobNotificationName} backup job`)
            setNotificationData((prev) => [Notification_local_Data, ...prev]);
            // toast.error(errorMessage);
            showToast(errorMessage, "error");

        } finally {
            setLoading(false);
            setIsPlayConfirmed(false);
            setSelectedJob(null); // Deselect job after action
        }
    };

    const handlePause = () => {
        if (selectedJob) {
            const job = filteredJobsData.find(job => job.id === selectedJob);
            fetchAPI('pause', selectedJob, job.name, agent);
        }
    };

    const handlePlay = () => {
        if (selectedJob) {
            const job = filteredJobsData.find(job => job.id === selectedJob);
            fetchAPI('play', selectedJob, job.name, agent);
        }
    };

    const handleRename = () => {
        if (selectedJob) {
            const job = filteredJobsData.find(job => job.id === selectedJob);
            if (job) {
                setJobNewName(job.name);
                setRenamePopupVisible(true);
            }
        }
    };

    const handleRenameSubmit = (newName) => {
        if (selectedJob) {
            const job = filteredJobsData.find(job => job.id === selectedJob);
            if (job) {
                fetchAPI('rename', selectedJob, job.name, agent, { jobNewName: newName });
                setRenamePopupVisible(false);
            }
        }
    };

    const handleReschedule = () => {
        setShowReschedulerModal(true); // Open the Rescheduler modal
    };

    // Close the Rescheduler modal
    const closeReschedulerModal = () => {
        setShowReschedulerModal(false);
        if (onJobActionSuccess) {
            onJobActionSuccess(); // Re-fetch jobs data after reschedule
        }
    };

    const handleDelete = () => {
        if (selectedJob) {
            setJobsToDelete([selectedJob]);
            setShowConfirmDelete(true);
        }
    };

    const handleConfirmDelete = async () => {
        try {
            setLoading(true);
            setIsPlayConfirmed(true); // Use this for deletion loading too

            for (const jobId of jobsToDelete) {
                const job = filteredJobsData.find(job => job.id === jobId);
                if (job) {
                    const payload = {
                        action: 'delete',
                        jobName: job.name,
                        agentName: agent,
                        jobId: job.id,
                    };

                    const response = await axiosInstance.delete(
                        `${config.API.Server_URL}/scheduler/action`,
                        {
                            action: "delete",
                            jobName: job.name,
                            agentName: agent,
                            jobId: job.id
                        }
                    );

                    // Success handling
                    setSuccessMessage('Delete successful!');
                    setShowSuccessPopup({ visible: true, isError: false });

                    if (onJobActionSuccess) {
                        onJobActionSuccess();
                        const downloadEvent = `${job.name} job deleted.`;
                        handleLogsSubmit(downloadEvent);
                    }

                    const Notification_local_Data = {
                        id: Date.now(),
                        message: `✅ ${jobNotificationName} backup Job Delete successful!`,
                        timestamp: new Date(),
                        isRead: false,
                    };
                    sendNotification(`✅ ${jobNotificationName} backup Job Delete successful!`)
                    setNotificationData((prev) => [Notification_local_Data, ...prev]);
                    // toast.success(`${jobNotificationName} backup Job Delete successful!`);
                    showToast(`${jobNotificationName} backup Job Delete successful!`);

                    setShowSuccessPopup({ visible: true, isError: false });
                }
            }

        } catch (error) {
            console.error('Error during delete action:', error);

            // Enhanced error handling
            let errorMessage = 'An error occurred. Please try again.';
            if (error.response) {
                switch (error.response.status) {
                    case 400:
                        errorMessage = 'Invalid delete request';
                        break;
                    case 401:
                        errorMessage = 'Authentication required';
                        break;
                    case 403:
                        errorMessage = 'Access denied - insufficient permissions';
                        break;
                    case 404:
                        errorMessage = 'Job not found';
                        break;
                    case 500:
                        errorMessage = 'Server error occurred';
                        break;
                    default:
                        errorMessage = error.response.data?.message || 'Delete failed. Please try again.';
                }
            } else if (error.request) {
                errorMessage = 'Network error - please check your connection';
            }

            setSuccessMessage(errorMessage);
            setShowSuccessPopup({ visible: true, isError: true });
            // toast.error(errorMessage);
            showToast(errorMessage, "error");

            // Optional: Add error notification
            const Notification_local_Data = {
                id: Date.now(),
                message: `❌ Failed to delete ${jobNotificationName} backup jobs`,
                timestamp: new Date(),
                isRead: false,
            };
            sendNotification(`❌ Failed to delete ${jobNotificationName} backup jobs`)
            setNotificationData((prev) => [Notification_local_Data, ...prev]);

        } finally {
            setShowConfirmDelete(false);
            setJobsToDelete([]);
            setLoading(false);
            setIsPlayConfirmed(false);
            setSelectedJob(null); // Deselect job after action
            // Again, consider refetching data here
        }
    };

    const handleCancelDelete = () => {
        setShowConfirmDelete(false);
        setJobsToDelete([]);
    };

    const handleSelectionChange = (jobId, jobname) => {
        setJobNotificationName(jobname)

        setSelectedJob(prevJobId => (prevJobId === jobId ? null : jobId));
    };

    const handleSearchChange = (event) => {
        setSearchQuery(event.target.value);
    };

    if (!filteredJobsData || !Array.isArray(filteredJobsData)) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">No jobs data available</div>
            </div>
        );
    }

    const sortedJobsData = [...filteredJobsData].sort((a, b) => new Date(a.next_run_time) - new Date(b.next_run_time));
    const isButtonDisabled = (jobId) => selectedJob !== jobId;

    const filteredAndSortedJobsData = sortedJobsData.filter((job) => {
        const jobName = job.name.toLowerCase();
        const jobTime = job.next_run_time ? new Date(job.next_run_time).toLocaleString() : '';
        return jobName.includes(searchQuery.toLowerCase()) || jobTime.includes(searchQuery);
    });

    return (
        <div className="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col h-full max-h-screen">
            {/* Fixed Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-2 py-1 flex-shrink-0">
                <div className="flex items-start sm:items-center justify-between flex-col sm:flex-row">
                    {/* Title */}
                    <h2 className="text-xl font-bold mb-1 sm:mb-0">
                        Scheduled Jobs of: {agent}
                    </h2>

                    {/* Right section: Search + Close Button */}
                    <div className="flex items-center gap-2 mt-1 sm:mt-0">
                        {/* Search Bar */}
                        <div className="hidden sm:flex items-center gap-2">
                            <div className="relative max-w-[12rem] w-full">
                                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                                <input
                                    type="text"
                                    placeholder="Search by job name..."
                                    value={searchQuery}
                                    onChange={handleSearchChange}
                                    className="pl-7 pr-2 py-1 rounded-md text-black text-sm w-full focus:ring-2 focus:ring-blue-300 focus:outline-none"
                                />
                            </div>
                        </div>

                        {/* Close Button (Visible on all screens) */}
                        {onClose && (
                            <button
                                onClick={onClose}
                                className="absolute top-2 right-2 sm:static sm:ml-2 text-white hover:text-gray-200 transition-colors"
                            >
                                <X size={24} />
                            </button>
                        )}
                    </div>
                </div>
            </div>


            {/* Small screen search bar */}
            <div className="p-1 border-b border-gray-200 sm:hidden flex-shrink-0">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Search by job name..."
                        value={searchQuery}
                        onChange={handleSearchChange}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    />
                </div>
            </div>

            {/* Desktop Table View with Fixed Header */}
            <div className="hidden lg:flex lg:flex-col lg:flex-1 custom-max-height overflow-y-auto">
                <table className="w-full table-fixed">
                    <thead className="bg-gray-50 border-b border-gray-200 sticky top-0 z-10">
                        <tr>
                            <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 tracking-wider w-16">
                                Sr.No.
                            </th>
                            <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 tracking-wider w-16">
                                Select
                            </th>
                            <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 tracking-wider" style={{ width: '15%' }}>
                                Job Name
                            </th>
                            {/* <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 tracking-wider w-24">
                                Backup Type
                            </th> */}
                            <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 tracking-wider w-20">
                                Repository
                            </th>
                            <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 tracking-wider" style={{ width: '15%' }}>
                                Source Location
                            </th>
                            <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 tracking-wider w-28">
                                Next Run Date
                            </th>
                            <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 tracking-wider w-24">
                                Next Run Time
                            </th>
                            <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 tracking-wider w-28">
                                Time Countdown
                            </th>
                            <th className="px-2 py-3 text-center text-xs font-medium text-gray-500 tracking-wider w-32">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {filteredAndSortedJobsData.length === 0 ? (
                            <tr>
                                <td colSpan="9" className="px-6 py-12 text-center text-gray-500">
                                    <div className="flex flex-col items-center">
                                        <Clock size={48} className="text-gray-400 mb-4" />
                                        <p className="text-lg">No jobs found for this endpoint</p>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            filteredAndSortedJobsData.map((job, index) => {
                                let formattedDate = "Paused";
                                let formattedTime = "Paused";
                                let countdown = "Paused";

                                if (job.next_run_time != null) {
                                    const formattedDateTime = formatDate(job.next_run_time);
                                    formattedDate = formattedDateTime.formattedDate;
                                    formattedTime = formattedDateTime.formattedTime;
                                    countdown = countdowns[job.id] || calculateCountdown(job.next_run_time);
                                }

                                const isUpcoming = job.next_run_time ? isJobScheduledInNextFourHours(job.next_run_time) : false;

                                return (
                                    <tr key={job.id} className={`hover:bg-gray-50 ${isUpcoming ? 'bg-yellow-100' : ''}`}>
                                        <td className="px-2 py-3 text-sm text-gray-900 text-center whitespace-nowrap">
                                            {index + 1}
                                        </td>
                                        <td className="px-2 py-3 text-center whitespace-nowrap">
                                            <input
                                                type="checkbox"
                                                checked={selectedJob === job.id}
                                                onChange={() => handleSelectionChange(job.id, job.name)}
                                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                            />
                                        </td>
                                        <td className="px-3 py-3">
                                            <div className="text-sm font-medium text-gray-900 break-words whitespace-normal overflow-hidden">
                                                {job.name}
                                            </div>
                                        </td>
                                        {/* <td className="px-2 py-3 text-sm text-gray-900 text-center whitespace-nowrap">
                                            Incremental
                                        </td> */}
                                        <td className="px-2 py-3 text-center whitespace-nowrap">
                                            <div className="flex justify-center">
                                                <RepoIcon repo={job.repo} />
                                            </div>
                                        </td>
                                        <td className="px-3 py-3">
                                            <div className="text-sm font-medium text-gray-900 break-words whitespace-normal overflow-hidden">
                                                {job.src_location}
                                            </div>
                                        </td>
                                        <td className="px-2 py-3 text-sm text-gray-500 whitespace-nowrap">
                                            <div className="flex items-center justify-start">
                                                <Calendar size={12} className="mr-1 flex-shrink-0" />
                                                <span className="text-xs">{formattedDate}</span>
                                            </div>
                                        </td>
                                        <td className="px-2 py-3 text-sm text-gray-500 whitespace-nowrap">
                                            <div className="flex items-center justify-start">
                                                <Clock size={12} className="mr-1 flex-shrink-0" />
                                                <span className="text-xs">{formattedTime}</span>
                                            </div>
                                        </td>
                                        <td className="px-2 py-3 whitespace-nowrap">
                                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${countdown === "Paused"
                                                ? 'bg-gray-100 text-gray-800'
                                                : isUpcoming
                                                    ? 'bg-yellow-100 text-yellow-800'
                                                    : 'bg-green-100 text-green-800'
                                                }`}>
                                                {countdown}
                                            </span>
                                        </td>
                                        <td className="px-2 py-3 text-sm font-medium whitespace-nowrap">
                                            <div className="flex items-center justify-center gap-1">
                                                {userPrivileges?.agentPause && (
                                                    <button
                                                        onClick={() => isPaused(job, countdowns) ? handlePlay() : handlePause()}
                                                        disabled={isButtonDisabled(job.id)}
                                                        className={`flex items-center p-1 rounded-md text-sm font-medium transition-colors
                                                        ${isButtonDisabled(job.id)
                                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                                : isPaused(job, countdowns)
                                                                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                                                                    : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                                                            }`}
                                                        title={isPaused(job, countdowns) ? "Play" : "Pause"}
                                                    >
                                                        {isPaused(job, countdowns) ? <Play size={14} /> : <Pause size={14} />}
                                                        <span className="text-xs">{isPaused(job, countdowns) ? "" : ""}</span>
                                                    </button>
                                                )}
                                                {userPrivileges?.agentUpdate && (
                                                    <button
                                                        onClick={handleRename}
                                                        disabled={isButtonDisabled(job.id)}
                                                        className={`flex items-center p-1 rounded-md text-sm font-medium transition-colors
                                                ${isButtonDisabled(job.id)
                                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'}`}
                                                        title="Rename"
                                                    >
                                                        <Edit3 size={14} />
                                                    </button>
                                                )}
                                                {userPrivileges?.agentUpdate && (
                                                    <button
                                                        onClick={handleReschedule}
                                                        disabled={isButtonDisabled(job.id)}
                                                        className={`flex items-center p-1 rounded-md text-sm font-medium transition-colors
                                                ${isButtonDisabled(job.id)
                                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'}`}
                                                        title="Re-schedule"
                                                    >
                                                        <Clock size={14} />
                                                    </button>
                                                )}
                                                {userPrivileges?.agentDelete && (
                                                    <button
                                                        onClick={handleDelete}
                                                        disabled={isButtonDisabled(job.id)}
                                                        className={`flex items-center p-1 rounded-md text-sm font-medium transition-colors
                                                ${isButtonDisabled(job.id)
                                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                                : 'bg-red-100 text-red-700 hover:bg-red-200'}`}
                                                        title="Delete"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>

            {/* Mobile Card View with Scrollable Content */}
            <div className="lg:hidden flex-1 overflow-y-auto">
                <div className="p-4 space-y-4 custom-max-height">
                    {filteredAndSortedJobsData.length === 0 ? (
                        <div className="text-center py-12">
                            <Clock size={48} className="text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-500">No jobs found for this endpoint</p>
                        </div>
                    ) : (
                        filteredAndSortedJobsData.map((job, index) => {
                            let formattedDate = "Paused";
                            let formattedTime = "Paused";
                            let countdown = "Paused";

                            if (job.next_run_time != null) {
                                const formattedDateTime = formatDate(job.next_run_time);
                                formattedDate = formattedDateTime.formattedDate;
                                formattedTime = formattedDateTime.formattedTime;
                                countdown = countdowns[job.id] || calculateCountdown(job.next_run_time);
                            }

                            const isUpcoming = job.next_run_time ? isJobScheduledInNextFourHours(job.next_run_time) : false;

                            return (
                                <div key={job.id} className={`border rounded-lg p-4 ${isUpcoming ? 'border-yellow-300 bg-yellow-50' : 'border-gray-200'}`}>
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center space-x-3">
                                            <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                                            <input
                                                type="checkbox"
                                                checked={selectedJob === job.id}
                                                onChange={() => handleSelectionChange(job.id)}
                                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                            />
                                        </div>
                                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${countdown === "Paused"
                                            ? 'bg-gray-100 text-gray-800'
                                            : isUpcoming
                                                ? 'bg-yellow-100 text-yellow-800'
                                                : 'bg-green-100 text-green-800'
                                            }`}>
                                            {countdown}
                                        </span>
                                    </div>

                                    <h3 className="font-medium text-gray-900 mb-2 break-words whitespace-normal w-full">{job.name}</h3>
                                    <h3 className="font-medium text-gray-900 mb-2 w-28"><RepoIcon repo={job.repo} /></h3>
                                    <h3 className="font-medium text-gray-900 mb-2">{job.src_location}</h3>

                                    <div className="space-y-2 text-sm text-gray-600 mb-4">
                                        <div className="flex items-center">
                                            <Calendar size={16} className="mr-2" />
                                            {formattedDate}
                                        </div>
                                        <div className="flex items-center">
                                            <Clock size={16} className="mr-2" />
                                            {formattedTime}
                                        </div>
                                    </div>

                                    {/* Mobile Action Buttons */}
                                    <div className="flex flex-wrap gap-2">
                                        {userPrivileges?.agentPause && (
                                            <button
                                                onClick={handlePause}
                                                disabled={isButtonDisabled(job.id)}
                                                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                                                ${isButtonDisabled(job.id)
                                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                        : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'}`}
                                            >
                                                <Pause size={16} className="mr-1" />
                                                Pause
                                            </button>
                                        )}
                                        <button
                                            onClick={handlePlay}
                                            disabled={isButtonDisabled(job.id)}
                                            className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                                            ${isButtonDisabled(job.id)
                                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                    : 'bg-green-100 text-green-700 hover:bg-green-200'}`}
                                        >
                                            <Play size={16} className="mr-1" />
                                            Play
                                        </button>
                                        {userPrivileges?.agentUpdate && (
                                            <button
                                                onClick={handleRename}
                                                disabled={isButtonDisabled(job.id)}
                                                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                                                ${isButtonDisabled(job.id)
                                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200'}`}
                                            >
                                                <Edit3 size={16} className="mr-1" />
                                                Rename
                                            </button>
                                        )}
                                        {userPrivileges?.agentUpdate && (
                                            <button
                                                onClick={handleReschedule}
                                                disabled={isButtonDisabled(job.id)}
                                                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                                                ${isButtonDisabled(job.id)
                                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200'}`}
                                            >
                                                <Clock size={16} className="mr-1" />
                                                Re-schedule
                                            </button>
                                        )}
                                        {userPrivileges?.agentDelete && (
                                            <button
                                                onClick={handleDelete}
                                                disabled={isButtonDisabled(job.id)}
                                                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                                                ${isButtonDisabled(job.id)
                                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                        : 'bg-red-100 text-red-700 hover:bg-red-200'}`}
                                            >
                                                <Trash2 size={16} className="mr-1" />
                                                Delete
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </div>

            {/* Popup Components */}
            {
                showConfirmDelete && (
                    <ConfirmationPopup
                        onConfirm={handleConfirmDelete}
                        onCancel={handleCancelDelete}
                    />
                )
            }

            {
                isRenamePopupVisible && (
                    <RenamePopup
                        jobName={jobNewName}
                        onSubmit={handleRenameSubmit}
                        onCancel={() => setRenamePopupVisible(false)}
                    />
                )
            }

            {
                (loading || isPlayConfirmed) && (
                    <LoadingOverlay message="Processing..." />
                )
            }

            {
                showSuccessPopup?.visible && (
                    <SuccessPopup
                        message={successMessage}
                        isError={showSuccessPopup.isError}
                        onClose={() => {
                            setShowSuccessPopup({ visible: false, isError: false });
                            setSuccessMessage('');
                        }}
                    />
                )
            }

            {/* Rescheduler Modal */}
            {
                showReschedulerModal && (
                    <Popup onClose={closeReschedulerModal}> {/* Use the Popup component here */}
                        <div className="endpoint-rescheduler">
                            <Rescheduler
                                action="reschedule"
                                jobName={filteredJobsData.find(job => job.id === selectedJob)?.name}
                                jobId={selectedJob}
                                agent={agent}
                                filteredJobsData={filteredJobsData}
                                onClose={closeReschedulerModal} // Pass onClose to Rescheduler
                            />
                        </div>
                    </Popup>
                )
            }
            {/* <ToastContainer position="top-right" autoClose={3000} /> */}

        </div >
    );
};

export default Scheduler;