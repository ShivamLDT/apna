import { useState, useEffect, useContext } from 'react';
import './EndPointPopup.css';
import useServerData from '../../Hooks/useServerData';
import Backupmodeldata from '../Backup/Backupmodeldata';
import { Backupindex } from '../../Context/Backupindex';
import RestoreBackupModel from './RestoreBackup/RestoreBackupModel';
import { NotificationContext } from "../../Context/NotificationContext";
import { RestoreContext } from '../../Context/RestoreContext';
import { UIContext } from '../../Context/UIContext';
import LoadingComponent from '../../LoadingComponent';
// setEndPointAgentName
const SelectEndpointPopup = ({
    setShowSelectEndpointCode = () => { },
    setEndPointListPopup = () => { },
    setShowRestorePopup = () => { },
    applyOnSameProfile = false,
    showNotEndPointPopup = false,
    setShowNotEndPointPopup = () => { },
    postData = () => { },
    notOpen = false,
    setApplyOnSameProfile = () => { },
    forceClientNodes = false,
    // selectedEndpointName,
    // setSelectedEndpointName,
}) => {
    const { serverData, selectedEndpoint, loading, error, refetch } = useServerData({
        forceClientNodes: forceClientNodes || applyOnSameProfile
    });
    const { endPointAgentName, setEndPointAgentName, selectedEndpointName, isSechduler, setIsSechduler, setSelectedEndpointName, isBackup, } = useContext(Backupindex);
    const { setShowRestoreReportEndPoint } = useContext(RestoreContext);
    const { setShowTreePopup, showBackuplog, setShowBackuplog } = useContext(UIContext);
    const { checkApi, setCheckApi, } = useContext(NotificationContext);
    const [storeEndPointName, setStoreEndPointName] = useState([]);
    const [selectedAgents, setSelectedAgents] = useState([]);
    const [popupMode, setPopupMode] = useState(null);

    useEffect(() => {
        if (showBackuplog) {
            setPopupMode('backuplog');
        } else if (applyOnSameProfile) {
            setPopupMode('applyProfile');
        } else {
            setPopupMode('normal');
        }
    }, [showBackuplog, applyOnSameProfile]);

    useEffect(() => {
        if (applyOnSameProfile) {
            if (Array.isArray(selectedEndpointName) && selectedEndpointName.length > 0) {
                setSelectedAgents([...selectedEndpointName]);
            } else {
                setSelectedAgents([]);
            }
        }
    }, [applyOnSameProfile, selectedEndpointName]);


    useEffect(() => {
        if (selectedEndpoint) {
            const filteredEndpoints = selectedEndpoint?.filter((item) => {
                return item?.agent !== endPointAgentName
            });
            setStoreEndPointName(filteredEndpoints)
        }
    }, [selectedEndpoint, endPointAgentName]);



    // const filteredEndpoints = Array.isArray(selectedEndpoint)
    //     ? selectedEndpoint.filter((ep) =>
    //         ep?.agent?.toLowerCase().includes(searchTerm.toLowerCase())
    //     )
    //     : [];

    const [visible, setVisible] = useState(true);
    const [activeTab, setActiveTab] = useState('Name');
    const [searchTerm, setSearchTerm] = useState('');
    const [visibleBackupModel, setvisibleBackupModel] = useState(true)


    const handleClose = () => {
        setVisible(false);

        setTimeout(() => {
            if (popupMode === 'backuplog') {
                setShowBackuplog(false);
                setShowSelectEndpointCode(false);
            } else if (popupMode === 'applyProfile') {
                setApplyOnSameProfile(false);
                setEndPointListPopup(false);
            } else {
                setShowSelectEndpointCode(false);
                setEndPointListPopup(false);
            }

            setIsSechduler(false);
        }, 100);
    };

    const closePopup = () => {
        if (typeof setShowSelectEndpointCode === "function") setShowSelectEndpointCode(false);
        if (typeof setvisibleBackupModel === "function") setvisibleBackupModel(false);
        if (typeof setEndPointListPopup === "function") setEndPointListPopup(false);
        if (typeof setApplyOnSameProfile === "function") setApplyOnSameProfile(false);
    };


    const HandleSaveBtn = () => {
        // ✅ Merge newly selected endpoints with existing ones
        if (typeof setSelectedEndpointName === "function") {
            setSelectedEndpointName((prev) => {
                const current = Array.isArray(prev)
                    ? prev
                    : Array.isArray(selectedEndpointName)
                        ? selectedEndpointName
                        : [];
                const merged = [...current];
                (selectedAgents || []).forEach((agent) => {
                    if (!merged.includes(agent)) merged.push(agent);
                });
                return merged;
            });
        } else if (typeof postData === "function") {
            const base = Array.isArray(selectedEndpointName)
                ? selectedEndpointName
                : [];
            const merged = Array.from(new Set([...base, ...(selectedAgents || [])]));
            postData(merged);
        }
        // ✅ Always close popup after save
        closePopup();
    };

    const handleSelectEndpoint = (name) => {
        // BackupLog mode
        if (popupMode === 'backuplog') {
            setShowRestoreReportEndPoint(name);
            setVisible(false);
            setTimeout(() => {
                setShowBackuplog(false);
                setShowSelectEndpointCode(false);
            }, 100);
            return;
        }

        // Apply Same Profile mode
        if (popupMode === 'applyProfile') {
            setSelectedAgents((prev) => {
                if (!Array.isArray(prev)) prev = [];
                if (prev.includes(name)) {
                    return prev.filter((a) => a !== name);
                }
                return [...prev, name];
            });
            return;
        }

        // Normal mode
        setCheckApi(false);

        if (!isSechduler && !applyOnSameProfile && typeof postData === "function") {
            postData(name);
        }

        if (!showNotEndPointPopup) {
            setEndPointAgentName(name);
            closePopup();

            setTimeout(() => {
                setEndPointAgentName(name);
                setShowTreePopup(true);
            }, 0);
        } else {
            setEndPointAgentName(name);
            setEndPointListPopup(false);
        }
    };


    const handleRefresh = (e) => {
        refetch();
    };
    useEffect(() => {
        const escHandler = (e) => {
            if (e.key === 'Escape') handleClose();
        };
        document.addEventListener('keydown', escHandler);
        return () => document.removeEventListener('keydown', escHandler);
    }, []);
    useEffect(() => {
        if (!visible) {
            const timer = setTimeout(() => {
                if (popupMode === 'backuplog') {
                    setShowBackuplog(false);
                }
            }, 200);
            return () => clearTimeout(timer);
        }
    }, [visible, popupMode]);
    if (!visible) return null;

    return (
        <>
            <div className="full-wrapper_endpoint_data">
                <div className="popup-overlay_endpoint_data" onClick={(e) => e.target.classList.contains('popup-overlay_endpoint_data') && handleClose()}>
                    <div className="popup-container_endpoint_data">
                        <button className="close-button_endpoint_data" onClick={handleClose}>&times;</button>

                        <div className="popup-header_endpoint_data">
                            <h2 className="popup-title_endpoint_data">
                                {/* <div className="monitor-icon_endpoint_data" /> */}
                                🖥️ Select Your Online Endpoint
                            </h2>

                            <div className="search-container_endpoint_data">
                                <input
                                    type="text"
                                    className="search-input_endpoint_data"
                                    placeholder="Search agent here"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                                <svg className="search-icon_endpoint_data" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="2"
                                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                                    />
                                </svg>
                            </div>

                            <div className="filter-tabs_endpoint_data">
                                {['Name', 'List', 'IP Address'].map((tab) => (
                                    <button
                                        key={tab}
                                        className={`tab-button_endpoint_data ${activeTab === tab ? 'active' : ''}`}
                                        onClick={() => setActiveTab(tab)}
                                    >
                                        {tab}
                                    </button>
                                ))}
                                <div className="endpoint-status-container">
                                    <div className="endpoint-status">
                                        <div className="endpoint-icon online">🖥️</div>
                                        <span>Online</span>
                                    </div>

                                    <div className="endpoint-status">
                                        <div className="endpoint-icon offline">🖥️</div>
                                        <span>Offline</span>
                                    </div>

                                    <div className="endpoint-status">
                                        <div className="endpoint-icon lost">🖥️</div>
                                        <span>Lost</span>
                                    </div>
                                </div>

                                <div className="action-buttons_endpoint_data">
                                    <button className="icon-button_endpoint_data" onClick={handleRefresh} title="Refresh">
                                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth="2"
                                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>


                        {!loading ? <div className="popup-content_endpoint_data">
                            {(() => {
                                const isEmpty = isBackup ? storeEndPointName?.length === 0 : selectedEndpoint.length === 0;

                                if (isEmpty) {
                                    return (
                                        <div className="text-center text-gray-500 dark:text-gray-300 py-8 col-span-full">
                                            No endpoints available
                                        </div>
                                    );
                                }

                                if (activeTab === 'Name') {
                                    return (
                                        <div className="endpoints-grid_endpoint_data">
                                            {(
                                                Array.isArray(isBackup ? storeEndPointName : selectedEndpoint)
                                                    ? (isBackup ? storeEndPointName : selectedEndpoint)
                                                    : []
                                            ).filter(ep =>
                                                ep?.ip?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                                ep?.agent?.toLowerCase().includes(searchTerm.toLowerCase())
                                            ).map((ep) => (
                                                <div
                                                    key={ep.agent}
                                                    className={`endpoint-item_endpoint_data ${isBackup && selectedAgents.includes(ep.agent) ? 'selected' : ''}`}
                                                    onClick={() => handleSelectEndpoint(ep.agent)}
                                                >
                                                    {/* ${((checkApi && ep.lastConnected === "True") || !checkApi && ep.lastConnected !== "True") ? "offline-endpoint" : ""} */}
                                                    <div
                                                        className={`endpoint-icon_endpoint_data
                                                        ${(ep.ip?.length > 30 || ep.ipAddress?.length > 30) ? "lostendpoint" : ""}
                                                        ${ep.lastConnected !== "True" ? "offline-endpoint" : ""}`}
                                                    />
                                                    <div className="endpoint-name_endpoint_data">{ep.agent}</div>
                                                </div>
                                            ))}
                                        </div>
                                    );
                                }

                                if (activeTab === 'IP Address') {
                                    return (
                                        <div className="endpoints-grid_endpoint_data">
                                            {(
                                                Array.isArray(isBackup ? storeEndPointName : selectedEndpoint)
                                                    ? (isBackup ? storeEndPointName : selectedEndpoint)
                                                    : []
                                            ).filter(ep =>
                                                ep?.ip?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                                ep?.agent?.toLowerCase().includes(searchTerm.toLowerCase())
                                            ).map((ep) => (
                                                <div
                                                    key={ep.agent}
                                                    className={`endpoint-item_endpoint_data ${isBackup && selectedAgents.includes(ep.agent) ? 'selected' : ''}`}
                                                    onClick={() => handleSelectEndpoint(ep.agent)}
                                                >
                                                    {/* ${((checkApi && ep.lastConnected === "True") || !checkApi && ep.lastConnected !== "True") ? "offline-endpoint" : ""}`} */}
                                                    <div
                                                        className={`endpoint-icon_endpoint_data
                                                        ${(ep.ip?.length > 30 || ep.ipAddress?.length > 30) ? "lostendpoint" : ""}
                                                        ${ep.lastConnected !== "True" ? "offline-endpoint" : ""}`}

                                                    />
                                                    <div className="endpoint-name_endpoint_data">  {
                                                        /^[a-f0-9]{64}$/i.test(ep.ip || ep.ipAddress || '')
                                                            ? 'No IP'
                                                            : (ep.ip || ep.ipAddress || '').match(/https?:\/\/([\d.]+):\d+/)?.[1]
                                                            || ep.ip
                                                            || ep.ipAddress
                                                            || 'N/A'
                                                    }</div>
                                                </div>
                                            ))}
                                        </div>
                                    );
                                }

                                // Default case: Table view
                                return (
                                    <div className="overflow-auto max-h-64">
                                        <table className="min-w-full text-sm text-left border border-collapse border-gray-200">
                                            <thead className="bg-gray-100 text-gray-700 sticky top-0">
                                                <tr>
                                                    <th className="px-4 py-2 border">Sr No</th>
                                                    <th className="px-4 py-2 border">Name</th>
                                                    <th className="px-4 py-2 border">IP Address</th>
                                                    <th className="px-4 py-2 border">Last Connected</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {(
                                                    Array.isArray(isBackup ? storeEndPointName : selectedEndpoint)
                                                        ? (isBackup ? storeEndPointName : selectedEndpoint)
                                                        : []
                                                )
                                                    .filter(ep => {
                                                        const ip = (ep.ip || ep.ipAddress || '').toLowerCase();
                                                        const agent = (ep.agent || '').toLowerCase();
                                                        const search = searchTerm.toLowerCase();

                                                        return ip.includes(search) || agent.includes(search);
                                                    })
                                                    .map((ep, index) => (
                                                        <tr
                                                            key={ep.agent || index}
                                                            className="cursor-pointer hover:bg-blue-50"
                                                            onClick={() => handleSelectEndpoint(ep.agent)}
                                                        >
                                                            <td className="px-4 py-2 border">{index + 1}</td>
                                                            <td className="px-4 py-2 border">{ep.agent}</td>
                                                            <td className="px-4 py-2 border">
                                                                {
                                                                    /^[a-f0-9]{64}$/i.test(ep.ip || ep.ipAddress || '')
                                                                        ? 'No IP'
                                                                        : (ep.ip || ep.ipAddress || '').match(/https?:\/\/([\d.]+):\d+/)?.[1]
                                                                        || ep.ip
                                                                        || ep.ipAddress
                                                                        || 'N/A'
                                                                }
                                                            </td>
                                                            {/* <td
                                                                className={`px-4 py-2 border ${(checkApi && ep.lastConnected === "False") || (!checkApi && ep.lastConnected === "True") ? 'text-green-600' : 'text-red-600'}`}
                                                            >
                                                                {(checkApi && ep.lastConnected === "False") || (!checkApi && ep.lastConnected === "True") ? "Online" : "Offline"}
                                                            </td> */}

                                                            <td
                                                                className={`px-4 py-2 border ${ep.lastConnected === "True"
                                                                    ? 'text-green-600'
                                                                    : 'text-red-600'
                                                                    }`}
                                                            >
                                                                {ep.lastConnected === "True" ? "Online" : "Offline"}
                                                            </td>
                                                        </tr>
                                                    ))}

                                            </tbody>
                                        </table>
                                    </div>
                                );
                            })()}
                        </div> : <div className="flex items-center justify-center h-1/2">
                            {/* <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
                                <div
                                    className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
                                    style={{ animation: 'oceanSlide 3s infinite' }}
                                />
                                <style>{`
              @keyframes oceanSlide {
                0% { transform: translateX(-150%); }
                66% { transform: translateX(0%); }
                100% { transform: translateX(150%); }
              }
            `}</style>
                            </div> */}
                            <LoadingComponent/>
                        </div>}


                        {storeEndPointName.length > 0 && applyOnSameProfile ? <div className="endpoint-save-btn">
                            <button type='button' onClick={HandleSaveBtn} className='endpoint-save-btn-button'>Save</button>
                        </div> : ""}

                    </div>
                </div>
            </div>
        </>
    );
};

export default SelectEndpointPopup;

