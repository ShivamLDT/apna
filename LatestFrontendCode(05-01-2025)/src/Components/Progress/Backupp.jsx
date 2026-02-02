import React, { useState, useEffect, useRef, useContext } from 'react';
import {
    Play,
    Pause,
    Square,
    Monitor,
    Info,
    X,
    CheckCircle,
    AlertCircle,
    Clock,
    XCircle,
    Upload,
    FileText,
    ChevronDown,
    ChevronRight,
    Folder,
    HardDrive,
    Cloud
} from 'lucide-react';

import { io } from 'socket.io-client';
import config from '../../config';
import { Backupindex } from '../../Context/Backupindex';
import { ToastContainer, toast } from 'react-toastify';
import { useToast } from '../../ToastProvider';
import CryptoJS from "crypto-js";
import axios from "axios";
import { sendNotification } from "../../Hooks/useNotification";
// Import Chart.js components
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import axiosInstance from '../../axiosinstance';

// Register the arc element for Doughnut charts
ChartJS.register(ArcElement, Tooltip, Legend);
import EndpointInfoPopup from '../Endpoint/EndpointInfoPopup';
import useSaveLogs from '../../Hooks/useSaveLogs';
import { NotificationContext } from "../../Context/NotificationContext";
import RepoIcon from '../Reports/Jobs/RepoIcon';
const useAgent = () => ({
    setAgentCount: (count) => {
    }
});


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

// Keep completed/failed jobs for 24h; always show in-progress jobs (avoids old backups cluttering UI)
const JOB_RETENTION_MS = 24 * 60 * 60 * 1000;
const filterRecentBackupJobs = (jobs, animatedData, agent) => {
    const now = Date.now();
    return jobs.filter((job) => {
        const displayJob = animatedData?.[agent]?.find((j) => String(j.id) === String(job.id)) || job;
        const status = displayJob?.status;
        const finished = displayJob?.finished;
        const progress = Number(displayJob?.progress_number ?? 0);
        const cloudProgress = Number(displayJob?.cloud_progress ?? 0);
        const isInProgress = status === "initiating" || status === "counting" ||
            (status !== "failed" && !finished && (progress < 100 || (displayJob?.cloud && cloudProgress < 100)));
        if (isInProgress) return true;
        const jobTime = job?.id ? (typeof job.id === "number" ? job.id * 1000 : parseFloat(job.id) * 1000) : 0;
        return jobTime > 0 && (now - jobTime) < JOB_RETENTION_MS;
    });
};

// FIXED: Updated ProgressDoughnutChart to handle both finished flag and progress >= 100
// Progress bar now shows incremental % during counting and upload (no more 0→100 jump)
const ProgressDoughnutChart = ({ progress, isFinished = false, isCounting = false, status }) => {
    const isFailed = status === "failed";
    let displayProgress;

    if (isCounting) {
        // Use actual progress during counting (e.g. file count or percentage)
        displayProgress = Math.max(0, Math.min(100, progress || 0));
    } else if (isFailed) {
        displayProgress = 0;    // failed jobs show 0% red
    } else if (isFinished || (progress != null && progress >= 100)) {
        displayProgress = 100;
    } else {
        // For active jobs, clamp progress between 0-100; default to 0 when undefined/NaN
        displayProgress = Math.max(0, Math.min(100, Number(progress) || 0));
    }

    // Determine if job is completed (finished flag OR progress >= 100)
    const jobCompleted = isFinished || progress >= 100;

    const data = {
        labels: ['Progress', 'Remaining'],
        datasets: [
            {
                data: [displayProgress, 100 - displayProgress],
                backgroundColor: [
                    isFailed ? '#EF4444' : jobCompleted ? '#22C55E' : displayProgress > 0 ? '#3B82F6' : '#9CA3AF',
                    '#E5E7EB',
                ],

                borderColor: [
                    isFailed ? '#EF4444' :
                        jobCompleted ? '#22C55E' :
                            displayProgress > 0 ? '#3B82F6' : '#9CA3AF',
                    '#E5E7EB',
                ],

                borderWidth: 1,
            },
        ],
    };

    const options = {
        cutout: '90%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                enabled: false,
            },
        },
    };

    return (
        <>
            <div className="relative w-12 h-12 flex items-center justify-center">
                <Doughnut data={data} options={options} />
                <div className="absolute text-xs font-semibold">
                    {Math.round(displayProgress)}%
                </div>
            </div>
            {/* <ToastContainer position="top-right" autoClose={3000} /> */}
        </>
    );
};

// SECOND progress bar (cloud progress)
const CloudProgressDoughnutChart = ({ progress, jobName, cloud }) => {
    const safe = Math.max(0, Math.min(100, progress || 0));
    const filename = jobName.split(/[\\/]/).pop();

    return (
        <div className="w-full">
            <hr className="border-t-1 border-gray-300"></hr>
            <div className="flex items-center gap-2 mb-1">
                {/* <span className="text-xs text-purple-600 font-semibold">

                </span> */}

                <span className="text-xs text-purple-600 font-semibold">
                    {Math.round(safe)}%  Cloud Upload to {cloud}: <i className='text-black not-italic break-word'>{filename}</i>
                </span>
            </div>

            <div className="w-full h-1 bg-purple-200 rounded-full overflow-hidden mt-1">
                <div
                    className="h-full bg-purple-600 rounded-full transition-all duration-300"
                    style={{ width: `${safe}%` }}
                />
            </div>
        </div>
    );
};


const Backupp = ({ searchQuery = '' }) => {
    // State variables from your original logic
    const [agentData, setAgentData] = useState({});
    const [agentFileCount, setAgentFileCount] = useState({});
    const [animatedData, setAnimatedData] = useState({});
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState('');
    const [modalChartData, setModalChartData] = useState([]);
    const [playStatus, setPlayStatus] = useState({});
    const [stopStatus, setStopStatus] = useState({});
    const [expandedBackups, setExpandedBackups] = useState({});
    const modalRef = useRef(null);
    const socket = useRef(null);
    const { setAgentCount } = useAgent();
    const [showAlert, setShowAlert] = useState(false);
    const [restoreFlag, setRestoreFlag] = useState(false);
    const [ips, setIps] = useState([]);
    const [filteredIps, setFilteredIps] = useState([]);
    const [userPrivileges, setUserPrivileges] = useState(null);
    const [showMachineInfo, setShowMachineInfo] = useState(false);
    const [selectedMachineAgent, setSelectedMachineAgent] = useState('');
    const [pendingAgent, setPendingAgent] = useState(null);
    const [allFiles, setAllFiles] = useState({});
    const [jobFiles, setJobFiles] = useState({});
    const { setNotificationData } = useContext(NotificationContext);
    const accessToken = localStorage.getItem("AccessToken");
    const [wsConnected, setWsConnected] = useState(true);
    const reconnectAttempts = useRef(0);
    const { profilePic, userRole, userName, handleLogsSubmit } = useSaveLogs();
    const { showToast } = useToast();
    const [pendingPlayAgent, setPendingPlayAgent] = useState(null);
    const [pendingPauseAgent, setPendingPauseAgent] = useState(null);

    const fetchIPs = async () => {
        try {
            const response = await axiosInstance.get(`${config.API.Server_URL}/clientnodes`, {
                headers: {
                    "Content-Type": "application/json",
                    token: accessToken,
                },
            });

            const data = response.data;

            if (Array.isArray(data.result)) {
                const sortedIps = data.result.sort((a, b) => {
                    if (a.agent.toLowerCase() < b.agent.toLowerCase()) return -1;
                    if (a.agent.toLowerCase() > b.agent.toLowerCase()) return 1;
                    return 0;
                });

                const ipAddresses = sortedIps.map(item => item.ipAddress);
                const hasDuplicateIP = ipAddresses.some((ip, index) => ipAddresses.indexOf(ip) !== index);

                if (hasDuplicateIP) {
                    fetchIPs();
                    return;
                }

                const updatedIps = sortedIps.map(item => {
                    if (item.progress < 100) {
                        return { ...item, lastConnected: false };
                    }
                    return item;
                });

                setIps(updatedIps);
                setFilteredIps(updatedIps);

            } else {
                console.error("Invalid data format received: result is not an array");
            }
        } catch (error) {
            console.error("Error fetching IPs:", error);
        }
    };

    useEffect(() => {
        fetchIPs();
        // const intervalId = setInterval(() => {
        //     fetchIPs();
        // }, 20000);

        // return () => {
        //     clearInterval(intervalId);
        // }
    }, [])

    useEffect(() => {
        const blink = `
    @keyframes blinkCloud {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }`;
        const s = document.createElement("style");
        s.innerHTML = blink;
        document.head.appendChild(s);
    }, []);


    const defaultPrivileges = {
        agentRead: false,
        progressPlay: false,
        progressPause: false,
        progressDelete: false,
    };

    useEffect(() => {
        const storedStatus = decryptData(localStorage.getItem("playStatusStorage"));

        if (storedStatus) {
            setPlayStatus(JSON.parse(storedStatus));
        } else {

            setPlayStatus(prev => {
                const newStatus = { ...prev };
                Object.keys(agentData).forEach(agent => {
                    if (newStatus[agent] === undefined) {
                        newStatus[agent] = true;
                    }
                });
                return newStatus;
            });
        }
    }, [agentData]);


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

        if (!parsedPrivileges) {
            defaultPrivileges.agentRead = true;
            defaultPrivileges.progressPlay = true;
            defaultPrivileges.progressPause = true;
            defaultPrivileges.progressDelete = true;
        } else {
            Object.keys(defaultPrivileges).forEach(key => {
                if (parsedPrivileges[key] !== undefined) {
                    defaultPrivileges[key] = parsedPrivileges[key];
                }
            });
        }

        setUserPrivileges(defaultPrivileges);
    }, []);

    useEffect(() => {
        // Load initial data from localStorage; prune old completed jobs to avoid clutter
        const storedAgentData = decryptData(localStorage.getItem("storedAgentDataa"));
        const storedAnimatedData = decryptData(localStorage.getItem("storedAnimatedDataa"));
        const storedJobFiles = decryptData(localStorage.getItem("storedJobFiles"));

        let agentDataFromStorage = storedAgentData ? JSON.parse(storedAgentData) : {};
        let animatedDataFromStorage = storedAnimatedData ? JSON.parse(storedAnimatedData) : {};
        const jobFilesFromStorage = storedJobFiles ? JSON.parse(storedJobFiles) : {};

        // Prune old completed/failed jobs per agent (keep last 24h)
        Object.keys(agentDataFromStorage).forEach((agent) => {
            agentDataFromStorage[agent] = filterRecentBackupJobs(agentDataFromStorage[agent] || [], animatedDataFromStorage, agent);
            if (animatedDataFromStorage[agent]) {
                const keptIds = new Set((agentDataFromStorage[agent] || []).map((j) => String(j.id)));
                animatedDataFromStorage[agent] = (animatedDataFromStorage[agent] || []).filter((j) => keptIds.has(String(j.id)));
            }
        });
        try {
            localStorage.setItem("storedAgentDataa", encryptData(JSON.stringify(agentDataFromStorage)));
            localStorage.setItem("storedAnimatedDataa", encryptData(JSON.stringify(animatedDataFromStorage)));
        } catch (e) {
            console.error("Failed to persist pruned backup data:", e);
        }

        setAgentData(agentDataFromStorage);
        setAnimatedData(animatedDataFromStorage);
        setJobFiles(jobFilesFromStorage);
    }, []);

    useEffect(() => {
        // Create WebSocket connection
        socket.current = io(`${config.API.WEB_SOCKET}`, {
            reconnection: true,
            reconnectionAttempts: Infinity,
            reconnectionDelay: 2000,
            reconnectionDelayMax: 8000,
        });

        if (socket.current) {
            socket.current.on("connect", () => {
                setWsConnected(true);
                reconnectAttempts.current = 0;
                // showToast("🔌 WebSocket Connected", "success");
                socket.current.emit("request_backup_data", {});
                socket.current.emit("request_backup_jobs", {});
            });

            socket.current.on("disconnect", () => {
                setWsConnected(false);

                reconnectAttempts.current += 1;
                // showToast(`⚠️ WebSocket connection lost. Reconnecting... (Attempt ${reconnectAttempts.current})`, "error");
            });

            socket.current.on("reconnect_attempt", (attempt) => {
                // showToast(`🔄 Reconnecting... Attempt ${attempt}`, "info");
            });

            socket.current.on("reconnect", () => {
                setWsConnected(true);
                // showToast("✅ WebSocket Reconnected", "success");
            });

            socket.current.on("reconnect_failed", () => {
                // showToast("❌ WebSocket failed to reconnect!", "error");
            });

            // Initial backup jobs on start (incl. "initiating" – show dialog/card as soon as job starts)
            socket.current.on("starting", (data) => {
                if (!data || !data.backup_jobs) return;
                try {
                    const fetchedData = Array.isArray(data.backup_jobs) ? data.backup_jobs : [data.backup_jobs];
                    const uniqueAgents = new Set();

                    fetchedData.forEach(job => {
                        const agent = job.agent;
                        uniqueAgents.add(agent);

                        setAgentData(prev => {
                            const newAgentData = { ...prev };
                            if (!newAgentData[agent]) newAgentData[agent] = [];

                            const existingIndex = newAgentData[agent].findIndex(j => String(j.id) === String(job.id));
                            if (existingIndex !== -1) {
                                newAgentData[agent][existingIndex] = job;
                            } else {
                                newAgentData[agent].push(job);
                            }
                            try {
                                localStorage.setItem("storedAgentDataa", encryptData(JSON.stringify(newAgentData)));
                            } catch (e) {
                                console.error("Failed to persist agentData from starting:", e);
                            }
                            return newAgentData;
                        });

                        setAnimatedData(prev => {
                            const newAnimatedData = { ...prev };
                            if (!newAnimatedData[agent]) newAnimatedData[agent] = [];
                            const existingIndex = newAnimatedData[agent].findIndex(j => String(j.id) === String(job.id));
                            const displayJob = {
                                ...job,
                                progress_number: job.progress_number ?? 0,
                                finished: job.status === "failed" ? false : (job.finished === true || (job.progress_number >= 100)),
                            };
                            if (existingIndex !== -1) {
                                newAnimatedData[agent][existingIndex] = displayJob;
                            } else {
                                newAnimatedData[agent].push(displayJob);
                            }
                            try {
                                localStorage.setItem("storedAnimatedDataa", encryptData(JSON.stringify(newAnimatedData)));
                            } catch (e) {
                                console.error("Failed to persist animatedData from starting:", e);
                            }
                            return newAnimatedData;
                        });

                        // Handle file-level updates from "starting" event (use String(job.id) for key)
                        if (job.filename && !job.cloud) {
                            setJobFiles(prev => {
                                const newJobFiles = { ...prev };
                                if (!newJobFiles[agent]) newJobFiles[agent] = {};
                                const jobKey = String(job.id);
                                if (!newJobFiles[agent][jobKey]) newJobFiles[agent][jobKey] = [];

                                const fileName = job.filename.split(/[\\/]/).pop();
                                const existingFileIndex = newJobFiles[agent][jobKey].findIndex(f => f.name === fileName);

                                // KEEP ORIGINAL: File-level logic unchanged
                                const fileData = {
                                    name: fileName,
                                    status: (job.finished || job.progress_number_file >= 100) ? "completed" :
                                        (job.progress_number_file > 0 && job.progress_number_file < 100) ? "uploading" :
                                            (job.status === "failed") ? "failed" : "pending",
                                    progress: Math.min(job.progress_number_file, 100),
                                    lastUpdated: Date.now()
                                };

                                if (existingFileIndex !== -1) {
                                    newJobFiles[agent][jobKey][existingFileIndex] = {
                                        ...newJobFiles[agent][jobKey][existingFileIndex],
                                        ...fileData
                                    };
                                } else {
                                    newJobFiles[agent][jobKey].push(fileData);
                                }
                                return newJobFiles;
                            });
                        }
                    });
                } catch (error) {
                    console.error("Error processing starting data:", error);
                }
            });

            // FIXED: Updated backup_data handler to properly handle completion status
            socket.current.on("backup_data", (data) => {
                if (!data || data.restore_flag === true) return;
                if (!data.backup_jobs) return;

                try {
                    const fetchedData = Array.isArray(data.backup_jobs) ? data.backup_jobs : [data.backup_jobs];
                    const validJobs = fetchedData.filter(job => job.restore_flag !== true);
                    if (validJobs.length === 0) return;
                    // const restoreFlag = data.restore_flag || false;
                    // if (restoreFlag) return;

                    const uniqueAgents = new Set();
                    const sortedData = validJobs.sort((a, b) => a.id - b.id);

                    sortedData.forEach(job => {
                        const agent = job.agent;
                        uniqueAgents.add(agent);

                        // Update agentData - Store the raw job data
                        setAgentData(prev => {
                            const newAgentData = { ...prev };
                            if (!newAgentData[agent]) newAgentData[agent] = [];

                            const existingIndex = newAgentData[agent].findIndex(j => String(j.id) === String(job.id));
                            if (existingIndex !== -1) {
                                newAgentData[agent][existingIndex] = job;
                            } else {
                                newAgentData[agent].push(job);
                            }

                            if (job.status !== "counting") {
                                localStorage.setItem("storedAgentDataa", encryptData(JSON.stringify(newAgentData)));
                            }
                            return newAgentData;
                        });

                        // Update animatedData - This is used for display
                        setAnimatedData(prev => {
                            const newAnimatedData = { ...prev };
                            if (!newAnimatedData[agent]) newAnimatedData[agent] = [];

                            const existingIndex = newAnimatedData[agent].findIndex(j => String(j.id) === String(job.id));
                            const previousJob = existingIndex !== -1 ? newAnimatedData[agent][existingIndex] : null;

                            // 🔥 FIX: Define isFileLevel before using it
                            const isOverallLevel = job.progress_number !== undefined && !job.progress_number_file && !job.progress_number_upload;
                            const isFileLevel = job.progress_number_file !== undefined;
                            const isCloudLevel = job.progress_number_upload !== undefined;
                            // Use progress_number when provided (incl. file-level updates) for incremental bar
                            const hasOverallProgress = job.progress_number !== undefined && !isNaN(parseFloat(job.progress_number));

                            const cloudProgressForCompletion = isCloudLevel
                                ? (job.progress_number_upload ?? 0)
                                : (previousJob?.cloud_progress ?? 100);
                            const isCloudUploadDone = !job.cloud || cloudProgressForCompletion >= 100;
                            const isJobCompleted =
                                !isFileLevel &&
                                job.status !== "failed" &&
                                isCloudUploadDone &&
                                (
                                    job.finished === true ||
                                    (job.progress_number != null && job.progress_number >= 100)
                                );
                            const isCloud = !!job.cloud;

                            const progressToUse = Math.max(0, Math.min(100, job.progress_number || 0));

                            const animatedJob = {
                                ...(previousJob || {}),
                                ...job, // merge original ALWAYS

                                // Separate cloud & overall progress

                                cloud_filename: (job.cloud && job.progress_number_upload !== undefined)
                                    ? job.filename
                                    : previousJob?.cloud_filename,

                                cloud_progress: isCloudLevel
                                    ? Math.max(0, Math.min(100, job.progress_number_upload))
                                    : previousJob?.cloud_progress ?? 0,

                                overall_progress: !isCloud
                                    ? progressToUse
                                    : (previousJob?.overall_progress ?? 0),

                                progress_number_original: job.progress_number,

                                // Use progress_number when provided for incremental bar; else keep previous
                                progress_number: hasOverallProgress
                                    ? Math.max(0, Math.min(100, parseFloat(job.progress_number)))
                                    : (isOverallLevel
                                        ? Math.max(0, Math.min(100, job.progress_number || 0))
                                        : previousJob?.progress_number || 0),

                                progress_number_file: isFileLevel
                                    ? Math.max(0, Math.min(100, job.progress_number_file || 0))
                                    : previousJob?.progress_number_file || 0,

                                progress_number_upload: isCloudLevel
                                    ? Math.max(0, Math.min(100, job.progress_number_upload || 0))
                                    : previousJob?.progress_number_upload || 0,



                                // When server/client reports failed, do not show as completed (avoids 100% + green)
                            // RCA: When cloud upload in progress (cloud_progress < 100), job is NOT finished even if staging progress_number=100
                                finished: job.status === "failed" ? false
                                    : (isCloudLevel && (job.progress_number_upload ?? 0) < 100) ? false
                                    : (isCloud && (previousJob?.cloud_progress ?? 0) < 100) ? false
                                    : (job.finished === true || (job.progress_number != null && job.progress_number >= 100)),
                                accuracy: job.accuracy ?? 0,
                                Jname: job.name
                            };

                            if (
                                isJobCompleted &&
                                !isFileLevel &&
                                job.status !== "failed" &&
                                (!prev[agent] ||
                                    !prev[agent][existingIndex] ||
                                    !prev[agent][existingIndex].finished)
                            ) {
                                const Notification_local_Data = {
                                    id: Date.now(),
                                    message: `✅ Backup completed for "${animatedJob?.Jname}" on endpoint "${agent}"`,
                                    timestamp: new Date(),
                                    isRead: false,
                                };
                                sendNotification(`✅ Backup completed for "${animatedJob?.Jname}" on endpoint "${agent}"`);
                                setNotificationData(prev => [Notification_local_Data, ...prev]);
                                showToast(`Backup completed for "${animatedJob?.Jname}" on endpoint "${agent}"`);
                            }

                            // Handle failed job
                            if (job.status === "failed" && !isFileLevel) {
                                const failMessage = `❌ Backup failed for "${job.name}" on endpoint "${agent}"`;

                                const Notification_local_Data = {
                                    id: Date.now(),
                                    message: failMessage,
                                    timestamp: new Date(),
                                    isRead: false,
                                };
                                sendNotification(failMessage);
                                handleLogsSubmit(failMessage);
                                setNotificationData(prev => [Notification_local_Data, ...prev]);
                                showToast(failMessage, "error");
                            }

                            if (existingIndex !== -1) {
                                newAnimatedData[agent][existingIndex] = animatedJob;
                            } else {
                                newAnimatedData[agent].push(animatedJob);
                            }

                            try {
                                localStorage.setItem(
                                    "storedAnimatedDataa",
                                    encryptData(JSON.stringify(newAnimatedData))
                                );
                            } catch (e) {
                                console.error("Failed to save animatedData:", e);
                            }

                            return newAnimatedData;
                        });



                        // Handle file-level updates only when filename is present (use String(job.id) for key)
                        if (job.filename && !job.cloud) {
                            setJobFiles(prev => {
                                const newJobFiles = { ...prev };
                                if (!newJobFiles[agent]) newJobFiles[agent] = {};
                                const jobKey = String(job.id);
                                if (!newJobFiles[agent][jobKey]) newJobFiles[agent][jobKey] = [];

                                const fileName = job.filename.split(/[\\/]/).pop();
                                const existingFileIndex = newJobFiles[agent][jobKey].findIndex(f => f.name === fileName);

                                // KEEP ORIGINAL: File-level logic unchanged
                                const fileData = {
                                    name: fileName,
                                    status: (job.finished || job.progress_number_file >= 100) ? "completed" :
                                        (job.progress_number_file > 0 && job.progress_number_file < 100) ? "uploading" :
                                            (job.status === "failed") ? "failed" : "pending",
                                    progress: Math.min(job.progress_number_file, 100),
                                    lastUpdated: Date.now(),
                                };

                                if (existingFileIndex !== -1) {
                                    newJobFiles[agent][jobKey][existingFileIndex] = {
                                        ...newJobFiles[agent][jobKey][existingFileIndex],
                                        ...fileData
                                    };
                                } else {
                                    newJobFiles[agent][jobKey].push(fileData);
                                }

                                localStorage.setItem("storedJobFiles", encryptData(JSON.stringify(newJobFiles)));
                                return newJobFiles;
                            });
                        }
                    });

                    setAgentCount(uniqueAgents.size);
                } catch (error) {
                    console.error("Error processing WebSocket data:", error);
                }
            });

            return () => {
                if (socket.current) {
                    socket.current.disconnect();
                }
            };
        }
    }, []);

    // Same icon style as UNC: percentage/doughnut only, no spinning; Upload when in progress
    const getStatusIcon = (job) => {
        const isFailed = job.status === "failed";
        const isCounting = job.status === "counting";
        const cloudProgress = Number(job?.cloud_progress ?? 0);
        const isCloudUploadInProgress = !!job?.cloud && cloudProgress < 100;
        const isCompleted = !isCounting && job.status !== "failed" && !isCloudUploadInProgress && (job.finished === true || (job.progress_number != null && job.progress_number >= 100));
        const isUploading = !isCounting && !isCompleted && (job.progress_number > 0 || (job?.cloud && cloudProgress > 0));

        if (isFailed) return <XCircle className="w-5 h-5 text-red-500" />;
        if (isCompleted) return <CheckCircle className="w-5 h-5 text-green-500" />;
        if (isUploading) return <Upload className="w-5 h-5 text-blue-500" />;
        if (isCounting) return <Clock className="w-5 h-5 text-gray-400" />;
        return <Clock className="w-5 h-5 text-gray-400" />;
    };


    // Match UNC style: always show percentage as status text (no "Initiating..." spinner text)
    const getStatusText = (job, displayProgress = 0) => {
        const isCounting = job.status === "counting";
        const cloudProgress = Number(job?.cloud_progress ?? 0);
        const isCloudUploadInProgress = !!job?.cloud && cloudProgress < 100;
        const isCompleted = job.status !== "failed" && !isCloudUploadInProgress && (job.finished === true || (job.progress_number != null && job.progress_number >= 100));
        const isUploading = !isCounting && !isCompleted && (job.progress_number > 0 || (job.cloud && cloudProgress > 0));

        const isLAN = job.repo === "LAN" || job.repo === "UNC";
        const pct = Math.round(displayProgress);

        if (job.status === "failed") return "Failed";
        if (isCounting) return "Counting Files";
        if (isCompleted) {
            return `${pct}% ${isLAN ? "Completed" : "Staging Complete"}`;
        }
        if (isUploading) {
            return (job.cloud && cloudProgress > 0) ? `${pct}% Cloud Upload` : `${pct}% ${isLAN ? "Processing" : "Staging"}`;
        }
        return pct > 0 ? `${pct}%` : "Pending";
    };


    // Get file status icon
    const getFileStatusIcon = (status) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case 'uploading':
                return <Upload className="w-4 h-4 text-blue-500 animate-pulse" />;
            case 'pending':
                return <Clock className="w-4 h-4 text-gray-400" />;
            case 'failed':
                return <XCircle className="w-4 h-4 text-red-500" />;
            default:
                return <FileText className="w-4 h-4 text-gray-400" />;
        }
    };

    // Check if job has files (use String(jobId) so 123 and "123" match)
    const hasFiles = (agent, jobId) => {
        const key = String(jobId);
        return jobFiles[agent] && jobFiles[agent][key] && jobFiles[agent][key].length > 0;
    };

    // Get files for a job with proper sorting
    const getJobFiles = (agent, jobId) => {
        const key = String(jobId);
        const files = (jobFiles[agent] && jobFiles[agent][key]) || [];

        return files.sort((a, b) => {
            const statusOrder = { uploading: 0, pending: 1, failed: 2, completed: 3 };

            if (statusOrder[a.status] !== statusOrder[b.status]) {
                return statusOrder[a.status] - statusOrder[b.status];
            }

            if (b.progress !== a.progress) {
                return b.progress - a.progress;
            }

            return b.lastUpdated - a.lastUpdated;
        });
    };

    // Toggle backup expansion
    const toggleBackupExpansion = (agentId, backupId) => {
        const key = `${agentId}-${backupId}`;
        setExpandedBackups(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };

    // Control button handlers
    const handlePlay = (agent) => {
        setPendingPlayAgent(agent);
        // socket.current.emit('message', { agent, action: 'play' });
        // setPlayStatus(prev => {
        //     const newStatus = { ...prev, [agent]: true };
        //     const downloadEvent = `${agent} jobs is playing`;
        //     handleLogsSubmit(downloadEvent);
        //     return newStatus;
        // });
    };

    const handleOkPlay = () => {
        if (pendingPlayAgent) {
            const agent = pendingPlayAgent;
            socket.current.emit('message', { agent, action: 'play' });
            setPlayStatus(prev => {
                const newStatus = { ...prev, [agent]: true };
                localStorage.setItem("playStatusStorage", encryptData(JSON.stringify(newStatus)));
                return newStatus;
            });
            setStopStatus(prev => ({ ...prev, [agent]: false }));
            const logEvent = `${agent} jobs is playing`;
            handleLogsSubmit(logEvent);
            showToast(logEvent, "success");
            setPendingPlayAgent(null);
        }
    };

    const handleOkPause = () => {
        if (pendingPauseAgent) {
            const agent = pendingPauseAgent;
            socket.current.emit('message', { agent, action: 'pause' });

            setPlayStatus(prev => {
                const newStatus = { ...prev, [agent]: false };
                localStorage.setItem("playStatusStorage", encryptData(JSON.stringify(newStatus)));
                return newStatus;
            });

            setStopStatus(prev => ({ ...prev, [agent]: false }));
            const logEvent = `${agent} jobs is paused`;
            handleLogsSubmit(logEvent);
            showToast(logEvent, "success");

            setPendingPauseAgent(null);
        }
    };

    const handleCancelPlay = () => {
        setPendingPlayAgent(null);
    };

    const handleCancelPause = () => {
        setPendingPauseAgent(null);
    };

    const handlePause = (agent) => {
        setPendingPauseAgent(agent);
        // socket.current.emit('message', { agent, action: 'pause' });
        // setPlayStatus(prev => ({ ...prev, [agent]: false }));
        // const downloadEvent = `${agent} jobs is paused`;
        // handleLogsSubmit(downloadEvent);
    };

    const handleStop = (agent) => {
        setPendingAgent(agent);
        setShowAlert(true);
    };

    const handleOk = () => {
        if (pendingAgent) {
            const agent = pendingAgent;
            const action = 'stop';
            socket.current.emit('message', { agent, action });
            setPlayStatus(prev => ({ ...prev, [agent]: false }));
            setStopStatus(prev => ({ ...prev, [agent]: true }));
            const downloadEvent = `${agent} jobs is stopped`;
            handleLogsSubmit(downloadEvent);
            setPendingAgent(null);
        }

        setShowAlert(false);
    };

    const handleCancel = () => {
        setPendingAgent(null);
        setShowAlert(false);
    };


    const getButtonClass = (agent, action) => {
        const isPlaying = playStatus[agent] === true;

        if (action === 'play') {
            if (isPlaying) {
                return 'bg-gray-600 cursor-not-allowed';
            }
            return 'bg-green-600 hover:bg-green-700';
        } else if (action === 'pause') {
            if (!isPlaying) {
                return 'bg-gray-600 cursor-not-allowed';
            }
            return 'bg-yellow-600 hover:bg-yellow-700';
        }

        if (action === 'stop') {
            return 'bg-red-600 hover:bg-red-700';
        }

        return 'bg-gray-600';
    };

    const handleMachineInfo = (agent) => {
        setSelectedMachineAgent(agent);
        setShowMachineInfo(true);
    };

    const closeMachineInfo = () => {
        setShowMachineInfo(false);
        setSelectedMachineAgent('');
    };

    const openModal = (agent) => {
        const data = animatedData[agent] || [];
        setModalChartData(data);
        setSelectedAgent(agent);
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

    return (
        <div className="w-full bg-gray-50">
            {/* Status Indicators */}
            <div className="bg-white border-b border-gray-200 p-4">
                <div>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                            <span className="text-sm text-gray-700">Uploading</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                            <span className="text-sm text-gray-700">Completed</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-gray-400 rounded-full"></div>
                            <span className="text-sm text-gray-700">Pending</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                            <span className="text-sm text-gray-700">Failed</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="pt-2 masonry" style={{ columnCount: "2", columnGap: "1.5rem" }}>
                {restoreFlag ? (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                        <AlertCircle className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
                        <p className="text-yellow-800 font-medium">Restore in progress. Data and progress will not be displayed.</p>
                    </div>
                ) : (
                    Object.keys(agentData)
                        .filter(agent => agent.toLowerCase().includes(searchQuery.toLowerCase()))
                        .map(agent => {
                            const mainJobs = filterRecentBackupJobs(agentData[agent] || [], animatedData, agent)
                                .sort((a, b) => b.scheduled_time?.localeCompare(a.scheduled_time));

                            const isOffline = ips.some(item => item.agent === agent && item.lastConnected !== "True");
                            const isAgentPlaying = playStatus[agent] === true;
                            const isActionPending = !!pendingPlayAgent || !!pendingPauseAgent || !!pendingAgent;

                            return (
                                <div
                                    key={agent}
                                    className={`bg-white rounded-lg shadow-lg border-2 transition-all duration-300 ${isOffline ? 'border-red-400 shadow-red-200' : 'border-gray-200'
                                        }`}
                                    style={{ breakInside: "avoid", marginBottom: "0.5rem" }}>
                                    {/* Agent Header */}
                                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 rounded-t-lg">
                                        <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-3 sm:space-y-0">
                                            <div className="flex items-center space-x-3">
                                                <Monitor className="w-6 h-6" />
                                                <div>
                                                    <h3 className="text-lg font-semibold">{agent}</h3>
                                                </div>
                                            </div>

                                            {/* Control Buttons */}
                                            <div className="flex items-center space-x-2">
                                                <button
                                                    onClick={() => handleMachineInfo(agent)}
                                                    className="p-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors"
                                                    title="Machine Info"
                                                >
                                                    <Info className="w-4 h-4" />
                                                </button>

                                                {isOffline ? (
                                                    <span className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-full font-medium">
                                                        Offline
                                                    </span>
                                                ) : (
                                                    <>

                                                        {userPrivileges?.progressPlay && (
                                                            <button
                                                                onClick={() => handlePlay(agent)}
                                                                className={`p-2 rounded-lg transition-colors ${getButtonClass(agent, 'play')}`}
                                                                disabled={isAgentPlaying || isActionPending}
                                                                title="Play"
                                                            >
                                                                <Play className={`w-4 h-4 ${getButtonClass(agent, 'play')}`} />
                                                            </button>
                                                        )}

                                                        {userPrivileges?.progressPause && (
                                                            <button
                                                                onClick={() => handlePause(agent)}
                                                                className={`p-2 rounded-lg transition-colors ${getButtonClass(agent, 'pause')}`}
                                                                disabled={!isAgentPlaying || isActionPending}
                                                                title="Pause"
                                                            >
                                                                <Pause className={`w-4 h-4 ${getButtonClass(agent, 'pause')}`} />
                                                            </button>
                                                        )}

                                                        {/* {userPrivileges?.progressDelete && (
                                                            <button
                                                                onClick={() => handleStop(agent)}
                                                                className={`p-2 ${getButtonClass(agent, 'stop')} hover:bg-red-600 rounded-lg transition-colors`}
                                                                title="Stop"
                                                            >
                                                                <Square className="w-4 h-4" />
                                                            </button>
                                                        )} */}
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Content */}
                                    <div className="overflow-auto bgMaxH">
                                        {mainJobs.length > 0 ? (
                                            mainJobs.map((job) => {
                                                // Use animatedData for display with fallback to original job (match id as string so 123 === "123")
                                                const jobToDisplay =
                                                    animatedData[agent]?.find(aJob => String(aJob.id) === String(job.id))
                                                    || job;


                                                const isCounting = jobToDisplay.status === "counting";
                                                const isFailed = jobToDisplay.status === "failed";
                                                const cloudProgress = Number(jobToDisplay?.cloud_progress ?? 0);
                                                const isCloudUploadInProgress = !!jobToDisplay?.cloud && cloudProgress < 100;
                                                // RCA: Job not completed when cloud upload in progress - staging 100% but cloud 50% should show 50%
                                                const isCompleted = jobToDisplay.status !== "failed" &&
                                                    !isCloudUploadInProgress &&
                                                    (jobToDisplay.finished === true || (jobToDisplay.progress_number != null && jobToDisplay.progress_number >= 100));
                                                const expansionKey = `${agent}-${job.id}`;
                                                const isExpanded = expandedBackups[expansionKey];
                                                const jobHasFiles = hasFiles(agent, job.id);

                                                // RCA: All progress from socket - when cloud upload in progress, use cloud_progress; for UNC use file-level when < 100%
                                                const files = jobHasFiles ? getJobFiles(agent, job.id) : [];
                                                const maxFileProgress = files.length > 0 ? Math.max(...files.map(f => Number(f.progress ?? 0))) : 0;
                                                const jobProgress = Number(jobToDisplay?.progress_number ?? job?.progress_number ?? 0);
                                                const fileLevelProgress = Number(jobToDisplay?.progress_number_file ?? job?.progress_number_file ?? 0);
                                                const isUNC = jobToDisplay?.repo === "UNC";
                                                const fileLevelIndicatesInProgress = (jobHasFiles && maxFileProgress < 100) || (fileLevelProgress > 0 && fileLevelProgress < 100);
                                                const statusProgressValue = isCloudUploadInProgress
                                                    ? cloudProgress
                                                    : (isUNC && fileLevelIndicatesInProgress)
                                                        ? Math.max(maxFileProgress, fileLevelProgress, jobProgress < 100 ? jobProgress : 0)
                                                        : Math.max(maxFileProgress, fileLevelProgress, jobProgress);

                                                const displayProgress =
                                                    isFailed
                                                        ? 0
                                                        : isCompleted
                                                            ? 100
                                                            : Math.max(0, Math.min(100, Number(statusProgressValue) || 0));

                                                const isUploading = !isCounting && !isCompleted && displayProgress > 0;

                                                return (
                                                    <div key={job.id} className="border border-gray-200 overflow-hidden">
                                                        <div
                                                            className={`p-4 ${jobHasFiles ? 'cursor-pointer' : ''} transition-colors 
                                                                ${jobToDisplay.status === "failed"
                                                                    ? 'bg-red-50 hover:bg-red-100'
                                                                    : isCounting
                                                                        ? 'bg-gray-50 hover:bg-gray-100'
                                                                        : isCompleted
                                                                            ? 'bg-green-50 hover:bg-green-100'
                                                                            : isUploading
                                                                                ? 'bg-blue-50 hover:bg-blue-100'
                                                                                : 'bg-gray-50 hover:bg-gray-100'
                                                                }
`}

                                                            onClick={jobHasFiles ? () => toggleBackupExpansion(agent, job.id) : undefined}
                                                        >
                                                            <div className="flex items-center justify-between">
                                                                <div className="flex items-center space-x-3">
                                                                    {jobHasFiles && (
                                                                        isExpanded ? (
                                                                            <ChevronDown className="w-5 h-5 text-gray-500" />
                                                                        ) : (
                                                                            <ChevronRight className="w-5 h-5 text-gray-500" />
                                                                        )
                                                                    )}
                                                                    {getStatusIcon(jobToDisplay)}
                                                                    {jobToDisplay.repo &&
                                                                        <RepoIcon repo={jobToDisplay.repo} />
                                                                    }

                                                                    <div>
                                                                        <div className="flex items-center space-x-2">
                                                                            <h4 className="text-sm text-gray-900">
                                                                                {jobToDisplay.name}
                                                                            </h4>
                                                                        </div>
                                                                        <p className="text-sm text-gray-600">
                                                                            Scheduled: {jobToDisplay.scheduled_time} <br />
                                                                            {isCounting ? (
                                                                                <span>• Counting Files: {Math.max(0, jobToDisplay.progress_number || 0)}</span>
                                                                            ) : (
                                                                                <span>Progress: {displayProgress}%</span>
                                                                            )}
                                                                        </p>
                                                                    </div>
                                                                </div>

                                                                <div className="text-right flex items-center space-x-1">
                                                                    {/* RCA: Always show progress % from socket - no spinner, sync with socket data */}
                                                                    <div className="flex items-center gap-3">
                                                                        <ProgressDoughnutChart
                                                                            progress={displayProgress}
                                                                            isFinished={isCompleted}
                                                                            isCounting={isCounting}
                                                                            status={jobToDisplay.status}
                                                                        />
                                                                    </div>

                                                                    <p className={`text-xs 
                                                                        ${jobToDisplay.status === "failed"
                                                                            ? 'text-red-600'
                                                                            : isCounting
                                                                                ? 'text-gray-500'
                                                                                : isCompleted
                                                                                    ? 'text-green-600'
                                                                                    : isUploading
                                                                                        ? 'text-blue-600'
                                                                                        : 'text-gray-500'
                                                                        }
`}>
                                                                        {getStatusText(jobToDisplay, displayProgress)}

                                                                    </p>

                                                                </div>
                                                            </div>
                                                            {jobToDisplay.cloud && (
                                                                <>
                                                                    <div className='flex item-center gap-2'>

                                                                        <CloudProgressDoughnutChart
                                                                            progress={jobToDisplay.cloud_progress}
                                                                            jobName={jobToDisplay?.cloud_filename || jobToDisplay?.filename}
                                                                            cloud={jobToDisplay?.cloud}
                                                                        />
                                                                    </div>

                                                                </>
                                                            )}
                                                        </div>

                                                        {/* Expanded Files Table View */}
                                                        {isExpanded && jobHasFiles && (
                                                            <div className="border-t border-gray-200 bg-gray-50">
                                                                <div className="p-2">
                                                                    <div className="overflow-x-auto max-h-40">
                                                                        <table className="w-full table-fixed break-words whitespace-normal bg-white border border-gray-200 rounded-lg overflow-hidden">
                                                                            <thead className="bg-gray-100">
                                                                                <tr>
                                                                                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase break-words whitespace-normal w-32">Status</th>
                                                                                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase break-words whitespace-normal">File Name</th>
                                                                                </tr>
                                                                            </thead>
                                                                            <tbody className="divide-y divide-gray-200">
                                                                                {getJobFiles(agent, job.id).map((file, fileIndex) => (
                                                                                    <tr key={fileIndex} className="hover:bg-gray-50 transition-colors">
                                                                                        <td className="px-2 py-3 flex gap-2 items-center break-words whitespace-normal w-32">
                                                                                            {getFileStatusIcon(file.status)}
                                                                                            <span className="text-xs text-gray-900">
                                                                                                {Math.min(100, Math.max(0, parseFloat(Number(file.progress).toFixed(1))))}%
                                                                                            </span>
                                                                                        </td>
                                                                                        <td className="px-2 py-3 break-words whitespace-normal max-w-xs">
                                                                                            <span className="text-xs text-gray-900">
                                                                                                {file.name}
                                                                                            </span>
                                                                                        </td>
                                                                                    </tr>
                                                                                ))}
                                                                            </tbody>
                                                                        </table>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })
                                        ) : (
                                            <div className="text-center py-8">
                                                <Folder className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                                                <p className="text-gray-500">No jobs available for this agent</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })
                )}
            </div>

            {/* Confirmation Alert Modal */}
            {showAlert && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex items-center space-x-3 mb-4">
                            <AlertCircle className="w-8 h-8 text-red-500" />
                            <h3 className="text-lg font-semibold text-gray-900">Confirm Stop</h3>
                        </div>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to stop the backup process for {pendingAgent}? This action cannot be undone.
                        </p>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={handleCancel}
                                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleOk}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                            >
                                Stop Backup
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {pendingPlayAgent && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex items-center space-x-3 mb-4">
                            <Play className="w-8 h-8 text-green-500" />
                            <h3 className="text-lg font-semibold text-gray-900">Confirm Play</h3>
                        </div>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to resume the backup process for {pendingPlayAgent}?
                        </p>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={handleCancelPlay}
                                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleOkPlay}
                                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                            >
                                Start Backup
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {pendingPauseAgent && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex items-center space-x-3 mb-4">
                            <Pause className="w-8 h-8 text-yellow-500" />
                            <h3 className="text-lg font-semibold text-gray-900">Confirm Pause</h3>
                        </div>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to pause the backup process for {pendingPauseAgent}?
                        </p>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={handleCancelPause}
                                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleOkPause}
                                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                            >
                                Pause Backup
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Machine Info Modal */}
            {showMachineInfo && (
                <EndpointInfoPopup
                    loading={false}
                    selectedEndpoint={ips.find(ip => ip.agent === selectedMachineAgent)}
                    onClose={closeMachineInfo}
                />
            )}


            {/* <ToastContainer position="top-right" autoClose={3000} /> */}
        </div>
    );
};

export default Backupp;