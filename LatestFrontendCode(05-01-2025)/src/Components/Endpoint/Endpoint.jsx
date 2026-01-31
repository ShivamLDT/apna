import { useState, useEffect } from "react";
import config from "../../config";
import { GlobeLock, Globe, AlarmClock, HardDriveUpload, HardDriveDownload, Cpu } from 'lucide-react';
import Scheduler from "./Scheduler";
import EndpointInfoPopup from "./EndpointInfoPopup";
import Popup from "./Popup";
import { useNavigate } from "react-router-dom";
import useClientData from "../../Hooks/useClientData";
import axios from "axios";
import axiosInstance from "../../axiosinstance";
import CryptoJS from "crypto-js";
import { useToast } from "../../ToastProvider";
import { useJobs } from "../Jobs/JobsContext";
import AlertComponent from "../../AlertComponent";
import useSaveLogs from "../../Hooks/useSaveLogs";
import LoadingComponent from "../../LoadingComponent";

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

const Endpoint = () => {
    const navigate = useNavigate();
    const { clientData, loading, error, refetch } = useClientData();
    const [showModal, setShowModal] = useState(false);
    const [selectedEndpoint, setSelectedEndpoint] = useState(null);
    const [jobsData, setJobsData] = useState([]);
    const [jobsLoading, setJobsLoading] = useState(false);
    const [showServerPopup, setShowServerPopup] = useState(false);
    const { showToast } = useToast();
    const { refreshClients } = useJobs();
    const [alert, setAlert] = useState(null);
    const [noSchedulerPermission, setNoSchedulerPermission] = useState(false);
    const { userRole } = useSaveLogs();
    const decryptedPrivileges = JSON.parse(decryptData(localStorage.getItem("user_privileges")) || "{}");

    const hasBackupPermission = () => {
        return userRole?.toLowerCase() !== "employee" || decryptedPrivileges?.backupReadWrite === true;
    };

    const hasRestorePermission = () => {
        return userRole?.toLowerCase() !== "employee" || decryptedPrivileges?.restoreReadWrite === true;
    };



    useEffect(() => {
        if (!selectedEndpoint && clientData?.result?.length > 0) {
            setSelectedEndpoint(clientData.result[0]);
        }
    }, [clientData, selectedEndpoint]);

    useEffect(() => {
        if (!clientData?.result) return;

        const updated = clientData.result.find(
            (e) => e.agent === selectedEndpoint?.agent
        );

        if (updated) {
            setSelectedEndpoint(updated);
        }
    }, [clientData]);


    // useEffect(() => {
    //     if (!showServerPopup) return;
    //     const intervalId = setInterval(() => {
    //         refetch(false);
    //     }, 10000);

    //     return () => clearInterval(intervalId);
    // }, [showServerPopup, refetch]);

    const refresh = async () => {
        refreshClients();
        refetch();
    }

    const fetchJobsData = async (ipAddress) => {
        setJobsLoading(true);
        try {
            const accessToken = localStorage.getItem('AccessToken');
            const response = await axiosInstance.post(`${config.API.Server_URL}/scheduler`, {
                ip: ipAddress
            }, {
                headers: {
                    "Content-Type": "application/json",
                    token: accessToken
                }
            });

            // If employee has no scheduler permissions
            if (response.data?.error === "Permission denied. Required one of: agentRead" || response.data?.status === false) {
                setNoSchedulerPermission(true);
                setJobsData([]);

                setAlert({
                    message: "You do not have permission to view scheduler.",
                    type: "error"
                });
                return false;
            }

            setJobsData(response.data.jobs || []);
            return true;

        } catch (error) {
            console.error("Error fetching jobs data:", error);
            setJobsData([]);

            setAlert({
                message: "Failed to load scheduler data. You may not have permission.",
                type: "error"
            });
            return false;
        } finally {
            setJobsLoading(false);
        }
    };



    const handleRowClick = (endpoint) => {
        setSelectedEndpoint(endpoint);
        setJobsLoading(false);
        setJobsData([]);
        setShowModal(false);
    };
    const handleShowServerInfo = () => setShowServerPopup(true);

    const openModal = async () => {
        if (selectedEndpoint) {
            const ok = await fetchJobsData(selectedEndpoint.ipAddress);
            if (!ok) return; // <--- STOP MODAL OPENING
            setShowModal(true);
        }
    };


    const handleClose = () => {
        setShowModal(false);
        setJobsData([]);
    };

    // if (loading) {
    //     return (
    //         <>
    //             <div className="flex items-center justify-center h-full">
    //                 <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
    //                     <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
    //                         style={{ animation: 'oceanSlide 3s infinite' }} />
    //                     <style>{`
    //   @keyframes oceanSlide {
    //     0% { transform: translateX(-150%); }
    //     66% { transform: translateX(0%); }
    //     100% { transform: translateX(150%); }
    //   }
    // `}</style>
    //                 </div>
    //             </div>
    //         </>
    //     );
    // }

    if (loading) {
        return <LoadingComponent />;
    }

    return (
        <div className="mx-auto h-full flex flex-col md:flex-row gap-4">
            {/* Endpoint List */}
            <div className="bg-white p-2 rounded-xl shadow-sm w-full md:w-2/3">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="p-1.5 flex rounded-lg bg-gray-100 text-sm font-medium">🖥️ Endpoint List</h3>

                    <div className={`px-3 py-1 flex items-center gap-2 rounded-full font-medium text-xs w-fit bg-gray-100 text-gray-700`}>
                        <span>🖥️</span>
                        <span>
                            Total: {clientData?.result?.length || 0}
                        </span>
                    </div>

                    <div className={`px-3 py-1 flex items-center gap-2 rounded-full font-medium text-xs w-fit bg-green-100 text-green-700`}>
                        <span
                            className={`h-2 w-2 rounded-full animate-pulse bg-green-500`}
                        ></span>
                        <span>
                            Online: {clientData?.result?.filter(item => item.lastConnected === "True").length || 0}
                        </span>
                    </div>

                    <div className={`px-3 py-1 flex items-center gap-2 rounded-full font-medium text-xs w-fit bg-red-100 text-red-700`}>
                        <span
                            className={`h-2 w-2 rounded-full animate-pulse bg-red-500`}
                        ></span>
                        <span>
                            Offline: {clientData?.result?.filter(item => item.lastConnected === "False").length || 0}
                        </span>
                    </div>

                    {selectedEndpoint && (
                        <button
                            type="button"
                            onClick={handleShowServerInfo}
                            className="px-3 py-1 flex items-center gap-2 rounded-lg font-medium text-xs w-fit bg-gray-100 text-black hover:bg-blue-100"
                        >
                            ℹ️ Info
                        </button>
                    )}
                    <button
                        type="button"
                        onClick={refresh}
                        className="px-3 py-1 flex items-center gap-2 rounded-lg font-medium text-xs w-fit bg-gray-100 text-black hover:bg-blue-100"
                    >
                        🔄️ Refresh
                    </button>
                </div>

                {error ? <p className="text-red-500">{error}</p> : (
                    <>
                        <div className="hidden h-5/6 md:block overflow-auto" style={{ height: "90%" }}>
                            <table className="w-full text-sm table-fixed">
                                <thead className="sticky top-0 bg-blue-500 z-10 text-white">
                                    <tr>
                                        <th className="px-6 py-3 text-left font-medium w-4/12">Device Name</th>
                                        <th className="px-6 py-3 text-left font-medium w-4/12">IP Address</th>
                                        <th className="px-6 py-3 text-left font-medium w-4/12">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {clientData?.result?.length === 0 ? (
                                        <tr>
                                            <td colSpan={3} className="text-center py-3 text-gray-500">
                                                No Endpoint Available
                                            </td>
                                        </tr>
                                    ) : (
                                        clientData?.result?.map((job, index) => {
                                            const serverVersion = decryptData(localStorage.getItem("serverVersion"));
                                            const isMismatch = serverVersion && job.data?.client_version !== serverVersion;

                                            return (
                                                <tr
                                                    key={index}
                                                    onClick={() => handleRowClick(job)}
                                                    className={`cursor-pointer border-b hover:bg-gray-100 ${selectedEndpoint?.agent === job.agent ? "bg-gray-100" : ""}`}
                                                >
                                                    <td className="w-4/12 px-6 py-3 truncate">{job.agent}</td>
                                                    <td className="w-4/12 px-6 py-3 truncate">{job.ip}</td>
                                                    <td className="w-4/12 px-6 py-3">
                                                        <div className="flex items-center gap-2">
                                                            <div className={`px-3 py-1 flex items-center gap-2 rounded-full font-medium text-xs w-fit ${job.lastConnected === "True"
                                                                ? "bg-green-100 text-green-700"
                                                                : "bg-red-100 text-red-700"
                                                                }`}>
                                                                <span
                                                                    className={`h-2 w-2 rounded-full animate-pulse ${job.lastConnected === "True"
                                                                        ? "bg-green-500"
                                                                        : "bg-red-500"
                                                                        }`}
                                                                ></span>
                                                                <span>
                                                                    {job.lastConnected === "True" ? "Online" : "Offline"}
                                                                </span>
                                                            </div>
                                                            {isMismatch && (
                                                                <div className="bg-red-600 text-white text-xs font-bold px-1 py-1 rounded-sm">
                                                                    Version Mismatch
                                                                </div>
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

                        {/* Mobile */}
                        <div className="md:hidden h-72 overflow-auto space-y-4">
                            {clientData.result?.map((job, index) => (
                                <div
                                    key={index}
                                    onClick={() => handleRowClick(job)}
                                    className={`cursor-pointer p-4 rounded border ${selectedEndpoint?.agent === job.agent ? "ring-2 ring-blue-400" : "bg-gray-50"}`}
                                >
                                    <div className="flex justify-between"><span className="font-medium">Device:</span> {job.agent}</div>
                                    <div className="flex justify-between"><span className="font-medium">Status:</span> <span className="text-green-600">{job.lastConnected ? "Online" : "Offline"}</span></div>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>

            {/* Endpoint Info */}
            <div className="bg-white p-2 rounded-xl shadow-sm w-full md:w-1/3 max-h-screen overflow-y-auto">
                {selectedEndpoint ? (
                    <div className="space-y-2">
                        <div className="flex flex-wrap justify-between">
                            <h4 className="p-1.5 flex rounded-lg bg-gray-100 text-sm font-medium break-all">🖥️{selectedEndpoint.agent}</h4>
                            <p className={`px-3 py-1 flex items-center gap-2 rounded-full font-medium text-xs w-fit ${selectedEndpoint.lastConnected === "True"
                                ? "bg-green-100 text-green-700"
                                : "bg-red-100 text-red-700"
                                }`}>
                                <span className={`h-2 w-2 rounded-full animate-pulse ${selectedEndpoint.lastConnected === "True" ? "bg-green-500" : "bg-red-500"}`}></span>
                                {selectedEndpoint.lastConnected === "True" ? "Online" : "Offline"}</p>

                            <p
                                className={`px-3 py-1 flex items-center gap-2 rounded-full font-medium text-xs w-fit ${selectedEndpoint.data?.client_version === decryptData(localStorage.getItem("serverVersion"))
                                    ? "bg-green-100 text-green-700"
                                    : "bg-red-100 text-red-700"
                                    }`}
                            >
                                {selectedEndpoint.data?.client_version}
                            </p>

                        </div>

                        <div className="flex flex-wrap gap-2">
                            <button className="flex items-center gap-2 bg-blue-500 text-white px-3 py-2 rounded hover:bg-blue-600" onClick={() => {
                                if (!hasBackupPermission()) {
                                    setAlert({ message: "You do not have permission to perform Backup.", type: "error" });
                                    return;
                                }
                                navigate("/backup");
                            }}>
                                <HardDriveUpload size={16} /> Backup
                            </button>
                            <button className="flex items-center gap-2 bg-green-500 text-white px-3 py-2 rounded hover:bg-green-600" onClick={() => {
                                if (!hasRestorePermission()) {
                                    setAlert({ message: "You do not have permission to perform Restore.", type: "error" });
                                    return;
                                }
                                navigate("/restore");
                            }}>
                                <HardDriveDownload size={16} /> Restore
                            </button>

                            {selectedEndpoint.lastConnected === "True" ? (
                                <button
                                    className="flex items-center gap-2 bg-purple-500 text-white px-3 py-2 rounded hover:bg-purple-600"
                                    onClick={openModal}
                                    disabled={jobsLoading}
                                >
                                    <AlarmClock size={16} /> {jobsLoading ? "Loading..." : "View Jobs"}
                                </button>
                            ) : <span className="bg-red-100 text-red-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-sm dark:bg-gray-700 dark:text-red-400 border border-red-400 whitespace-normal break-words">Last Connected Time: <br />{selectedEndpoint?.lastConnectedTime}</span>
                            }
                        </div>

                        <div className="flex flex-row gap-2">
                            <div className="flex items-start gap-2">
                                <GlobeLock />
                                <div>
                                    <p className="text-gray-600 text-sm">IP Address</p>
                                    <p className="text-green-600 text-sm">{selectedEndpoint.ip}</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-2">
                                <Globe />
                                <div>
                                    <p className="text-gray-600 text-sm">Mac Address</p>
                                    <p className="text-green-600 text-sm">{selectedEndpoint.data?.mac_addresses}</p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            {selectedEndpoint.data?.disk?.map((disk, index) => {
                                const usedPercentage = (parseFloat(disk.used) / parseFloat(disk.total)) * 100;
                                return (
                                    <div key={index}>
                                        <p className="text-sm text-gray-600">Storage {disk.device} - Total: {disk.total}</p>
                                        <div className="w-full bg-gray-200 rounded h-4">
                                            <div className="bg-blue-600 h-4 rounded" style={{ width: `${usedPercentage}%` }}></div>
                                        </div>
                                        <p className="text-xs text-gray-500">Used: {disk.used} / Free: {disk.free}</p>
                                    </div>
                                );
                            })}
                        </div>

                        <div className="flex flex-col md:flex-row gap-4 items-start">
                            <Cpu />
                            <div className="text-sm text-gray-700 space-y-1">
                                <p>OS: <span className="text-green-600">{selectedEndpoint.data?.os?.name}</span></p>
                                <p>CPU: <span className="text-green-600">{selectedEndpoint.data?.processor?.name}</span></p>
                                <p>RAM: <span className="text-green-600">{selectedEndpoint.data?.memory?.total}</span></p>
                            </div>
                        </div>
                    </div>
                ) : <p>No Endpoint Available</p>}
            </div>

            {showServerPopup && selectedEndpoint && (
                <EndpointInfoPopup
                    selectedEndpoint={clientData.result.find(e => e.agent === selectedEndpoint.agent)}
                    loading={loading}
                    onClose={() => setShowServerPopup(false)}
                />
            )}


            {showModal && (
                <div className="modal-overlayPop" onClick={handleClose}>
                    <div className="modal-contentPop" onClick={(e) => e.stopPropagation()} style={{ width: "92%", marginLeft: "50px" }}>
                        <div className="popup-reset-text-align">
                            <button className="modal-close-btnP" onClick={handleClose}></button>
                            <Scheduler
                                jobsData={jobsData}
                                onClose={handleClose}
                                agent={selectedEndpoint?.agent}
                                onJobActionSuccess={() => fetchJobsData(selectedEndpoint.ipAddress)}
                            />
                        </div>
                    </div>
                </div>
            )}
            {alert && (
                <AlertComponent
                    message={alert.message}
                    type={alert.type}
                    onClose={() => setAlert(null)}
                />
            )}

        </div>
    );
};

export default Endpoint;