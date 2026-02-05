import React, { useState, useEffect, useRef } from 'react';
import {
    Monitor,
    X,
    CheckCircle,
    AlertCircle,
    Clock,
    XCircle,
    Download,
    FileText,
    ChevronDown,
    ChevronRight,
    Folder,
    HardDrive,
} from 'lucide-react';

import { io } from 'socket.io-client';
import config from '../../config';

// Import Chart.js components
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import CryptoJS from "crypto-js";
import { useToast } from "../../ToastProvider";
// Register the arc element for Doughnut charts
ChartJS.register(ArcElement, Tooltip, Legend);

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

// Show only currently running or pending restore jobs (hide completed/failed)
const filterRecentRestoreJobs = (jobs, animatedData, agent) => {
    return jobs.filter((job) => {
        const displayJob = animatedData?.[agent]?.find((j) => String(j.id) === String(job.id)) || job;
        const status = displayJob?.status;
        const finished = displayJob?.finished;
        const isInProgress = status === "counting" || (!finished && status !== "completed" && status !== "failed");
        return isInProgress;
    });
};

const ProgressDoughnutChart = ({ progress, status }) => {
    const clampedProgress = Math.min(100, Math.max(0, parseFloat(Number(progress).toFixed(0)) || 0));
    const isFailed = status === "failed";
    const data = {
        labels: ['Remaining', 'Completed'],
        datasets: [
            {
                data: [clampedProgress, 100 - clampedProgress],
                backgroundColor: [
                    clampedProgress === 100 ? '#22C55E' :
                        clampedProgress === 0 ? '#9CA3AF' :
                            '#3B82F6',
                    '#E5E7EB',
                ],
                borderColor: [
                    clampedProgress === 100 ? '#22C55E' :
                        clampedProgress === 0 ? '#9CA3AF' :
                            '#3B82F6',
                    '#E5E7EB',
                ],
                borderWidth: 1,
            },
        ],
    };

    const options = {
        cutout: '90%',
        radius: '100%',
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
        <div className="relative w-12 h-12 flex items-center justify-center">
            <Doughnut data={data} options={options} />
            <div className="absolute text-xs font-semibold">
                {clampedProgress}%
            </div>
        </div>
    );
};


const AccuracyProgress = ({ accuracy }) => {
    const safe = Math.max(0, Math.min(100, Number(accuracy) || 0));

    return (
        <div className="w-full">
            <hr className="border-t-1 border-gray-300"></hr>
            <div className="flex items-center gap-2 mb-1">
                {/* <span className="text-xs text-purple-600 font-semibold">

                </span> */}

                <span className="text-xs text-green-600 font-semibold">
                    Restored: {safe}%
                </span>
            </div>

            <div className="w-full h-1 bg-green-200 rounded-full overflow-hidden mt-1">
                <div
                    className="h-full bg-green-600 rounded-full transition-all duration-300"
                    style={{ width: `${safe}%` }}
                />
            </div>
        </div>
    );
};

const Restorepp = ({ searchQuery = '' }) => {
    // State variables
    const [agentData, setAgentData] = useState({}); // Stores job data grouped by agent
    const [animatedData, setAnimatedData] = useState({}); // Stores animated progress data
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState('');
    const [modalChartData, setModalChartData] = useState([]);
    const [playStatus, setPlayStatus] = useState({}); // Manages play/pause state for agents
    const [stopStatus, setStopStatus] = useState({}); // Manages stop state for agents
    const [expandedRestores, setExpandedRestores] = useState({}); // Manages expanded view for restore jobs
    const modalRef = useRef(null); // Ref for modal
    const socket = useRef(null); // Ref for WebSocket connection
    const { setAgentCount } = useAgent(); // Hook for setting agent count
    const [showAlert, setShowAlert] = useState(false); // State for confirmation alert
    const [ips, setIps] = useState([]); // Stores IP addresses/machine info
    const [filteredIps, setFilteredIps] = useState([]); // Filtered IP addresses
    const [userPrivileges, setUserPrivileges] = useState(null); // User privilege state
    const [showMachineInfo, setShowMachineInfo] = useState(false); // State for machine info modal
    const [selectedMachineAgent, setSelectedMachineAgent] = useState(''); // Selected agent for machine info
    const [pendingAgent, setPendingAgent] = useState(null); // Agent pending stop confirmation
    const [jobFiles, setJobFiles] = useState({}); // Stores files associated with each job
    const [restoreLocationCache, setRestoreLocationCache] = useState({});
    const { showToast } = useToast();
    const accessToken = localStorage.getItem("AccessToken"); // Auth token from local storage

    // Default user privileges
    const defaultPrivileges = {
        agentRead: false,
        progressPlay: false,
        progressPause: false,
        progressDelete: false,
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

        // Set default privileges or merge with parsed ones
        if (!parsedPrivileges) {
            // If no privileges found, enable all by default as per original logic
            defaultPrivileges.agentRead = true;
            defaultPrivileges.progressPlay = true;
            defaultPrivileges.progressPause = true;
            defaultPrivileges.progressDelete = true;
        } else {
            // Apply parsed privileges, ensuring defaults for missing keys
            Object.keys(defaultPrivileges).forEach(key => {
                if (parsedPrivileges[key] !== undefined) {
                    defaultPrivileges[key] = parsedPrivileges[key];
                }
            });
        }
        setUserPrivileges(defaultPrivileges);
    }, []);

    // Effect for loading initial data from localStorage (for persistence); prune old completed jobs
    useEffect(() => {
        const storedAgentData = decryptData(localStorage.getItem("storedRestoreAgentData"));
        const storedAnimatedData = decryptData(localStorage.getItem("storedRestoreAnimatedData"));
        const storedJobFiles = decryptData(localStorage.getItem("storedRestoreJobFiles"));

        let agentDataFromStorage = storedAgentData ? JSON.parse(storedAgentData) : {};
        let animatedDataFromStorage = storedAnimatedData ? JSON.parse(storedAnimatedData) : {};
        const jobFilesFromStorage = storedJobFiles ? JSON.parse(storedJobFiles) : {};

        // Prune old completed/failed restore jobs per agent (keep last 24h)
        Object.keys(agentDataFromStorage).forEach((agent) => {
            const restoreJobs = (agentDataFromStorage[agent] || []).filter((j) => j.restore_flag === true || j.restore_flag === "true");
            const filtered = filterRecentRestoreJobs(restoreJobs, animatedDataFromStorage, agent);
            agentDataFromStorage[agent] = filtered;
            if (animatedDataFromStorage[agent]) {
                const keptIds = new Set(filtered.map((j) => String(j.id)));
                animatedDataFromStorage[agent] = (animatedDataFromStorage[agent] || []).filter((j) => keptIds.has(String(j.id)));
            }
        });
        try {
            localStorage.setItem("storedRestoreAgentData", encryptData(JSON.stringify(agentDataFromStorage)));
            localStorage.setItem("storedRestoreAnimatedData", encryptData(JSON.stringify(animatedDataFromStorage)));
        } catch (e) {
            console.error("Failed to persist pruned restore data:", e);
        }

        setAgentData(agentDataFromStorage);
        setAnimatedData(animatedDataFromStorage);
        setJobFiles(jobFilesFromStorage);
    }, []);

    // Main WebSocket effect for receiving restore progress updates
    useEffect(() => {
        // Create WebSocket connection
        socket.current = io(`${config.API.WEB_SOCKET}`);

        if (socket.current) {
            socket.current.on("connect", () => {
                socket.current.emit("request_restore_data", {}); // Request initial restore data
                socket.current.emit("request_restore_jobs", {}); // Request initial restore jobs
            });

            // Listener for initial 'starting' restore jobs (similar to backup)
            socket.current.on("starting", (data) => {
                if (!data || !data.backup_jobs) return; // Assuming 'backup_jobs' field might contain restore jobs initially

                try {
                    const fetchedData = Array.isArray(data.backup_jobs) ? data.backup_jobs : [data.backup_jobs];
                    const restoreJobs = fetchedData.filter(job => job.restore_flag === true || job.restore_flag === 'true');

                    if (restoreJobs.length === 0) return;

                    const uniqueAgents = new Set();
                    restoreJobs.forEach(job => {
                        const agent = job.agent;
                        setRestoreLocationCache(prev => {
                            const newCache = { ...prev };
                            if (!newCache[job.id] && job.restore_location) {
                                newCache[job.id] = job.restore_location;
                            }
                            return newCache;
                        });
                        uniqueAgents.add(agent);

                        setAgentData(prev => {
                            const newAgentData = { ...prev };
                            if (!newAgentData[agent]) newAgentData[agent] = [];

                            const existingIndex = newAgentData[agent].findIndex(j => j.name === job.name && j.scheduled_time === job.scheduled_time && String(j.id) === String(job.id));
                            if (existingIndex !== -1) {
                                newAgentData[agent][existingIndex] = job;
                            } else {
                                newAgentData[agent].push(job);
                            }
                            return newAgentData;
                        });

                        // RCA: Update animatedData so progress comes from socket; avoid 100% on dialog appear (UNC/cloud restore)
                        setAnimatedData(prev => {
                            const newAnimatedData = { ...prev };
                            if (!newAnimatedData[agent]) newAnimatedData[agent] = [];
                            const existingIndex = newAnimatedData[agent].findIndex(j => String(j.id) === String(job.id));
                            const displayJob = {
                                ...job,
                                progress_number: job.progress_number ?? 0,
                                finished: job.finished ?? false,
                            };
                            if (existingIndex !== -1) {
                                newAnimatedData[agent][existingIndex] = displayJob;
                            } else {
                                newAnimatedData[agent].push(displayJob);
                            }
                            try {
                                localStorage.setItem("storedRestoreAnimatedData", encryptData(JSON.stringify(newAnimatedData)));
                            } catch (e) {
                                console.error("Failed to persist animatedData from starting (restore):", e);
                            }
                            return newAnimatedData;
                        });

                        // Update jobFiles for individual files being restored (use String(job.id) for key)
                        setJobFiles(prev => {
                            const newJobFiles = { ...prev };
                            if (!newJobFiles[agent]) newJobFiles[agent] = {};
                            const jobKey = String(job.id);
                            if (!newJobFiles[agent][jobKey]) newJobFiles[agent][jobKey] = [];

                            if (job.status === "counting" && job.filename) {
                                const fileName = job.filename.split(/[\\/]/).pop();
                                const existingFileIndex = newJobFiles[agent][jobKey].findIndex(f => f.name === fileName);

                                const fileData = {
                                    name: fileName,
                                    status: (job.status === "failed") ? "failed" :
                                        (job.finished || job.progress_number >= 100) ? "completed" :
                                            (job.progress_number > 0 && job.progress_number < 100) ? "restoring" :
                                                "pending",
                                    progress: Math.min(job.progress_number, 100), // Original progress 0-100
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
                            }
                            return newJobFiles;
                        });
                    });
                } catch (error) {
                    console.error("Error processing starting data for restore:", error);
                }
            });

            // Listener for continuous 'backup_data' updates (filtered for restore_flag)
            socket.current.on("backup_data", (data) => {
                if (!data) return;
                let payload;
                try {
                    payload = typeof data === "string" ? JSON.parse(data) : data;
                } catch {
                    return;
                }
                if (!payload.backup_jobs) return;

                try {
                    const fetchedData = Array.isArray(payload.backup_jobs) ? payload.backup_jobs : [payload.backup_jobs];
                    const restoreJobs = fetchedData.filter(job => job.restore_flag === true || job.restore_flag === 'true');

                    if (restoreJobs.length === 0) return; // Only process if there are restore jobs

                    const uniqueAgents = new Set();
                    const sortedData = restoreJobs.sort((a, b) => a.id - b.id); // Sort by job ID

                    sortedData.forEach(job => {
                        const agent = job.agent;
                        setRestoreLocationCache(prev => {
                            const newCache = { ...prev };
                            if (!newCache[job.id] && job.restore_location) {
                                newCache[job.id] = job.restore_location;
                            }
                            return newCache;
                        });
                        uniqueAgents.add(agent);

                        // Update agentData
                        setAgentData(prev => {
                            const newAgentData = { ...prev };
                            if (!newAgentData[agent]) newAgentData[agent] = [];

                            const existingIndex = newAgentData[agent].findIndex(j => String(j.id) === String(job.id));
                            if (existingIndex !== -1) {
                                newAgentData[agent][existingIndex] = job;
                            } else {
                                newAgentData[agent].push(job);
                            }

                            // Only save if status is not 'counting' (meaning it's active or finished)

                            localStorage.setItem("storedRestoreAgentData", encryptData(JSON.stringify(newAgentData)));

                            return newAgentData;
                        });

                        // Update animatedData (job-level progress)
                        setAnimatedData(prev => {
                            const newAnimatedData = { ...prev };
                            if (!newAnimatedData[agent]) newAnimatedData[agent] = [];

                            const existingIndex = newAnimatedData[agent].findIndex(j => String(j.id) === String(job.id));
                            const existingJob = existingIndex !== -1 ? prev[agent][existingIndex] : null;
                            const previousJob =
                                existingIndex !== -1 ? newAnimatedData[agent][existingIndex] : null;

                            const isFileLevel = job.status === "counting" && !!job.filename;
                            // UNC chunk-level: no restore_accuracy, file progress IS job progress – don't freeze
                            const hasJobLevelAggregation = job.restore_accuracy !== undefined && job.restore_accuracy !== null;
                            const shouldFreezeJobProgress = isFileLevel && hasJobLevelAggregation;
                            const restoreAccuracy = job.restore_accuracy !== undefined ? job.restore_accuracy : (previousJob?.restore_accuracy ?? existingJob?.restore_accuracy);
                            // RCA: Job not finished when restore_accuracy < 100 (cloud/UNC restore phase still ongoing)
                            const isRestorePhaseOngoing = restoreAccuracy != null && Number(restoreAccuracy) < 100;
                            const jobFinished = job.finished !== false && !isRestorePhaseOngoing && (job.finished === true || (job.progress_number != null && job.progress_number >= 100));
                            // Folder-wide restore: keep progress monotonic (never decrease)
                            const incomingProgress = Math.max(0, Math.min(100, job.progress_number ?? previousJob?.progress_number ?? 0));
                            const previousProgress = previousJob?.progress_number ?? 0;
                            const progressMonotonic = shouldFreezeJobProgress ? (previousJob?.progress_number ?? 0) : Math.max(previousProgress, incomingProgress);
                            const animatedJob = {
                                ...previousJob,
                                ...job,
                                progress_number_original: job.progress_number,

                                progress_number: Math.min(100, Math.max(0, progressMonotonic)),

                                restore_accuracy: job.restore_accuracy !== undefined ? job.restore_accuracy : (existingJob?.restore_accuracy),
                                restore_location: job.restore_location || existingJob?.restore_location,
                                finished: job.status === "failed" ? false
                                    : (job.finished === true || job.status === "finished") ? true
                                    : jobFinished,
                                accuracy: job.accuracy ?? 0,
                            };


                            if (existingIndex !== -1) {
                                newAnimatedData[agent][existingIndex] = animatedJob;
                            } else {
                                newAnimatedData[agent].push(animatedJob);
                            }


                            localStorage.setItem("storedRestoreAnimatedData", encryptData(JSON.stringify(newAnimatedData)));

                            return newAnimatedData;
                        });

                        const isLegacyCompleted = !job?.status && job.finished;
                        const isCompletedEvent = job?.status === "completed" || isLegacyCompleted;
                        if (job.restore_flag && isCompletedEvent && job?.status !== "counting") {
                            showToast(`${job?.name} is restored on ${job?.agent} at ${job?.restore_location}`, "success");
                        }


                        if (job.restore_flag && job?.status === "failed") {
                            showToast(`${job?.name} Failed on ${job?.agent} at ${job?.restore_location}`, "error");
                        }

                        // Update jobFiles when 'filename' is present (use String(job.id) for key)
                        setJobFiles(prev => {
                            const newJobFiles = { ...prev };
                            if (!newJobFiles[agent]) newJobFiles[agent] = {};
                            const jobKey = String(job.id);
                            if (!newJobFiles[agent][jobKey]) newJobFiles[agent][jobKey] = [];

                            if (job.status === "counting" && job.filename) {
                                const fileName = job.filename.split(/[\\/]/).pop();
                                const existingFileIndex = newJobFiles[agent][jobKey].findIndex(f => f.name === fileName);

                                const fileData = {
                                    name: fileName,
                                    status: (job.status === "failed") ? "failed" :
                                        (job.finished || job.progress_number >= 100) ? "completed" :
                                            (job.progress_number > 0 && job.progress_number < 100) ? "restoring" :
                                                "pending",
                                    progress: Math.min(job.progress_number, 100), // Original progress 0-100
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
                            }
                            localStorage.setItem("storedRestoreJobFiles", encryptData(JSON.stringify(newJobFiles)));
                            return newJobFiles;
                        });
                    });

                    setAgentCount(uniqueAgents.size); // Update total agent count
                } catch (error) {
                    console.error("Error processing WebSocket data for restore:", error);
                }
            });

            // Cleanup function for WebSocket
            return () => {
                if (socket.current) {
                    socket.current.disconnect();
                }
            };
        }
    }, []); // Empty dependency array means this effect runs once on mount


    const getStatusIcon = (progress, finished, status) => {
        if (status === "failed") {
            return <XCircle className="w-5 h-5 text-red-500" />;
        } else if (status === "completed" || finished) {
            return <CheckCircle className="w-5 h-5 text-green-500" />;
        } else if (progress > 0) {
            return <Download className="w-5 h-5 text-blue-500 animate-pulse" />;
        } else {
            return <Clock className="w-5 h-5 text-gray-400" />;
        }
    };


    const getStatusText = (progress, finished, status) => {
        if (status === "failed") {
            return 'Failed';
        } else if (status === "completed" || finished) {
            return 'Completed';
        } else if (progress > 0) {
            return 'Restoring';
        } else {
            return 'Pending';
        }
    };


    const getFileStatusIcon = (status) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case 'restoring':
                return <Download className="w-4 h-4 text-blue-500 animate-pulse" />;
            case 'pending':
                return <Clock className="w-4 h-4 text-gray-400" />;
            case 'failed':
                return <XCircle className="w-4 h-4 text-red-500" />;
            default:
                return <FileText className="w-4 h-4 text-gray-400" />;
        }
    };


    const hasFiles = (agent, jobId) => {
        const key = String(jobId);
        const agentFiles = jobFiles[agent] || {};
        const files = agentFiles[key];
        return files && files.length > 0;
    };

    const getJobFiles = (agent, jobId) => {
        const key = String(jobId);
        const agentFiles = jobFiles[agent] || {};
        const files = agentFiles[key] || [];
        return files.sort((a, b) => a.progress - b.progress);
    };

    const toggleRestoreExpansion = (agentId, restoreId) => {
        const key = `${agentId}-${restoreId}`;
        setExpandedRestores(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };


    const handlePlay = (agent) => {
        socket.current.emit('message', { agent, action: 'play_restore' }); // Changed action
        setPlayStatus(prev => {
            const newStatus = { ...prev, [agent]: true };
            return newStatus;
        });
    };


    const handlePause = (agent) => {
        socket.current.emit('message', { agent, action: 'pause_restore' }); // Changed action
        setPlayStatus(prev => ({ ...prev, [agent]: false }));
    };

    const handleStop = (agent) => {
        setPendingAgent(agent);
        setShowAlert(true);
    };


    const handleOk = () => {
        if (pendingAgent) {
            const agent = pendingAgent;
            const action = 'stop_restore'; // Changed action
            socket.current.emit('message', { agent, action });
            setPlayStatus(prev => ({ ...prev, [agent]: false }));
            setStopStatus(prev => ({ ...prev, [agent]: true }));
            setPendingAgent(null);
        }
        setShowAlert(false);
    };


    const handleCancel = () => {
        setPendingAgent(null);
        setShowAlert(false);
    };


    const getButtonClass = (agent, action) => {
        if (action === 'play') {
            return playStatus[agent] ? 'bg-green-500' : 'bg-green-600';
        } else if (action === 'pause') {
            return !playStatus[agent] && !stopStatus[agent] ? 'bg-yellow-500' : 'bg-gray-600';
        } else if (action === 'stop') {
            return stopStatus[agent] ? 'bg-red-600' : 'bg-red-600';
        }
        return 'bg-gray-600'; // Default
    };


    const handleMachineInfo = (agent) => {
        setSelectedMachineAgent(agent);
        setShowMachineInfo(true);
    };


    const closeMachineInfo = () => {
        setShowMachineInfo(false);
        setSelectedMachineAgent('');
    };

    return (
        <div className="w-full bg-gray-50">
            {/* Status Indicators */}
            <div className="bg-white border-b border-gray-200 p-4">
                <div>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                            <span className="text-sm text-gray-700">Restoring</span>
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
            <div className="pt-2 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 items-start">
                {/* Filter agents based on search query */}
                {Object.keys(agentData)
                    .filter(agent => agent.toLowerCase().includes(searchQuery.toLowerCase()))
                    .map(agent => {
                        // Filter for jobs with restore_flag true; hide old completed/failed (keep last 24h)
                        const restoreJobs = filterRecentRestoreJobs(
                            (agentData[agent] || []).filter(job => job.restore_flag === true || job.restore_flag === 'true'),
                            animatedData, agent
                        ).sort((a, b) => b.scheduled_time?.localeCompare(a.scheduled_time));

                        // Check if the machine is offline based on fetched IPs
                        const isOffline = ips.some(item => item.agent === agent && item.lastConnected !== "True");

                        // Only render agent card if there are active restore jobs
                        if (restoreJobs.length === 0) {
                            return null;
                        }

                        return (
                            <div
                                key={agent}
                                className={`bg-white rounded-lg shadow-lg border-2 transition-all duration-300 ${isOffline ? 'border-red-400 shadow-red-200' : 'border-gray-200'
                                    }`}
                            >
                                {/* Agent Header */}
                                <div className="bg-gradient-to-r from-green-600 to-green-600 text-white p-4 rounded-t-lg">
                                    <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-3 sm:space-y-0">
                                        <div className="flex items-center space-x-3">
                                            <Monitor className="w-6 h-6" />
                                            <div>
                                                <h3 className="text-lg font-semibold">{agent}</h3>
                                                {isOffline && (
                                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800 mt-1">
                                                        <XCircle className="w-3 h-3 mr-1" />
                                                        Offline
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                    </div>
                                </div>

                                {/* Restore Jobs Content */}
                                <div className='overflow-auto bgMaxH'>
                                    {restoreJobs.length > 0 ? (
                                        restoreJobs.map((job) => {
                                            // Use animatedData for job-level progress display
                                            const jobToDisplay = animatedData[agent]?.find(aJob => String(aJob.id) === String(job.id)) || job;
                                            const effectiveJobProgress = Number(jobToDisplay.progress_number ?? 0);
                                            const isFileLevel = jobToDisplay.status === "counting" && !!jobToDisplay.filename;

                                            const isFailed = jobToDisplay.status === 'failed';
                                            const isCompleted =
                                                jobToDisplay.status === 'completed' ||
                                                (jobToDisplay.finished && !jobToDisplay.status);
                                            const expansionKey = `${agent}-${job.id}`;
                                            const isExpanded = expandedRestores[expansionKey];
                                            const jobHasFiles = hasFiles(agent, job.id);
                                            const hasJobLevelProgress =
                                                jobToDisplay.restore_accuracy !== undefined &&
                                                jobToDisplay.restore_accuracy !== null;


                                            let displayProgressValue = 0;

                                            if (hasJobLevelProgress) {
                                                const accuracy = Number(jobToDisplay.restore_accuracy ?? 0);
                                                if (isFailed || isCompleted) {
                                                    displayProgressValue = Math.max(0, Math.min(100, accuracy));
                                                } else {
                                                    // RCA: Use min of progress_number and restore_accuracy - progress_number can hit 100 (download) before restore_accuracy (actual restore). Same fix for UNC/cloud restore.
                                                    displayProgressValue = Math.max(0, Math.min(100,
                                                        Math.min(effectiveJobProgress, isNaN(accuracy) ? effectiveJobProgress : accuracy)
                                                    ));
                                                }
                                            } else {
                                                // Use SAME value as status column: prefer file list, then raw job (same payload as file list)
                                                if (jobHasFiles) {
                                                    const files = getJobFiles(agent, job.id);
                                                    const statusProgressValue = files.length > 0
                                                        ? Math.max(...files.map(f => Number(f.progress ?? 0)))
                                                        : (jobToDisplay?.progress_number_file ?? job?.progress_number_file ?? jobToDisplay?.progress_number ?? job?.progress_number ?? 0);
                                                    displayProgressValue = Math.max(0, Math.min(100, statusProgressValue));
                                                } else {
                                                    displayProgressValue = Math.max(0, Math.min(100, Number(jobToDisplay?.progress_number_file ?? job?.progress_number_file ?? jobToDisplay?.progress_number ?? job?.progress_number ?? 0)));
                                                }
                                            }

                                            // Status and icon should follow the same progress (so "Restoring" when bar > 0)
                                            const isRestoring = !isFailed && !isCompleted && displayProgressValue > 0;


                                            return (
                                                <div key={job.id} className="border border-gray-200 overflow-hidden">
                                                    <div
                                                        className={`p-4 ${jobHasFiles ? 'cursor-pointer' : ''} transition-colors ${isCompleted ? 'bg-green-50 hover:bg-green-100' :
                                                            isRestoring ? 'bg-blue-50 hover:bg-blue-100' :
                                                                jobToDisplay.status === 'failed' ? 'bg-red-50 hover:bg-red-100' : 'bg-gray-50 hover:bg-gray-100'
                                                            }`}
                                                        onClick={jobHasFiles ? () => toggleRestoreExpansion(agent, job.id) : undefined}
                                                    >


                                                        <div className="flex items-start justify-between">
                                                            <div className="flex items-start space-x-3 flex-1">
                                                                {jobHasFiles && (
                                                                    <div className="mt-1">
                                                                        {isExpanded ? (
                                                                            <ChevronDown className="w-5 h-5 text-gray-500" />
                                                                        ) : (
                                                                            <ChevronRight className="w-5 h-5 text-gray-500" />
                                                                        )}
                                                                    </div>
                                                                )}
                                                                {/* <HardDrive className="w-6 h-6 text-blue-600" /> */}
                                                                <div className="flex-1">
                                                                    <div className="flex items-center space-x-2 mb-1">
                                                                        {getStatusIcon(displayProgressValue, jobToDisplay.finished, jobToDisplay.status)}
                                                                        <h4 className="text-sm font-semibold text-gray-900">
                                                                            {jobToDisplay.name}
                                                                        </h4>
                                                                    </div>
                                                                    <p className="text-xs text-gray-600 mb-1">
                                                                        Scheduled: {jobToDisplay.scheduled_time}
                                                                        <span className="ml-2">• Progress: {displayProgressValue}%</span>
                                                                    </p>
                                                                    <p className="text-xs text-gray-700 break-all">
                                                                        <span className="font-medium">Restore Location:</span> {restoreLocationCache[job.id] || jobToDisplay?.restore_location}
                                                                    </p>
                                                                </div>
                                                            </div>

                                                            <div className="flex items-center space-x-3 ml-4">
                                                                {/* Pass the calculated descending progress to the Doughnut Chart */}
                                                                <ProgressDoughnutChart progress={displayProgressValue} status={jobToDisplay.status} />
                                                                <p className={`text-xs whitespace-nowrap ${isCompleted ? 'text-green-600' :
                                                                    isRestoring ? 'text-blue-600' :
                                                                        jobToDisplay.status === 'failed' ? 'text-red-600' : 'text-gray-500'
                                                                    }`}>
                                                                    {getStatusText(displayProgressValue, jobToDisplay.finished, jobToDisplay.status)}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        {jobToDisplay.restore_accuracy !== undefined && jobToDisplay.restore_accuracy !== null && (
                                                            <>
                                                                <div className='flex item-center gap-2'>
                                                                    <AccuracyProgress
                                                                        accuracy={jobToDisplay.restore_accuracy}
                                                                    />
                                                                </div>
                                                            </>
                                                        )}
                                                    </div>

                                                    {/* Expanded Files Table View */}
                                                    {isExpanded && jobHasFiles && (
                                                        <div className="border-t border-gray-200 bg-gray-50">
                                                            <div className="p-4">
                                                                <div className="overflow-x-auto max-h-40">
                                                                    <table className="w-full bg-white border border-gray-200 rounded-lg overflow-hidden">
                                                                        <thead className="bg-gray-100">
                                                                            <tr>
                                                                                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase break-words whitespace-normal w-32">Status</th>
                                                                                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase break-words whitespace-normal">File Name</th>
                                                                                {/* <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th> */}
                                                                                {/* <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Remaining</th> */}
                                                                            </tr>
                                                                        </thead>
                                                                        <tbody className="divide-y divide-gray-200">
                                                                            {getJobFiles(agent, job.id).map((file, fileIndex) => {
                                                                                // Calculate descending progress for each file
                                                                                const fileDisplayProgressValue = Math.max(0, 100 - Math.min(100, file.progress));
                                                                                return (
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
                                                                                        {/* <td className="px-4 py-3">
                                                                                            <span className="text-xs text-gray-900">
                                                                                                {Math.min(100, Math.max(0, parseFloat(Number(file.progress).toFixed(1))))}%
                                                                                            </span>
                                                                                        </td> */}
                                                                                        {/* <td className="px-4 py-3">
                                                                                            <span className="text-xs text-gray-900">
                                                                                                {fileDisplayProgressValue}%
                                                                                            </span>
                                                                                        </td> */}
                                                                                    </tr>
                                                                                );
                                                                            })}
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
                                            <p className="text-gray-500">No restore jobs available for this agent</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
            </div>
        </div>
    );
};

export default Restorepp;