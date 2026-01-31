import React, { useState, useMemo, useEffect, useContext } from 'react';
import { useLocation } from "react-router-dom";
import axios from "axios";
import config from '../../config';
import { Search, Check, RefreshCw, AlertCircle } from 'lucide-react';
import useSaveLogs from '../../Hooks/useSaveLogs';
import { ToastContainer, toast } from 'react-toastify';
import { useToast } from '../../ToastProvider';
import { Backupindex } from '../../Context/Backupindex';
import axiosInstance from '../../axiosinstance';
import { sendNotification } from '../../Hooks/useNotification';
import { NotificationContext } from "../../Context/NotificationContext";
import LoadingComponent from '../../LoadingComponent';

const Pairing = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [activeFilter, setActiveFilter] = useState('paired');
    const location = useLocation();

    // Force 'unpaired' tab when coming from StatsCards
    useEffect(() => {
        if (location.state?.tab === "unpaired") {
            setActiveFilter("unpaired");
        }
    }, [location.state]);

    const [allEndpoints, setAllEndpoints] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [pairingLoading, setPairingLoading] = useState(false);
    const [pairingError, setPairingError] = useState('');
    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();
    const { setNotificationData } = useContext(NotificationContext)
    const [unpairedAgentsData, setUnpairedAgentsData] = useState({});
    const [selectedToPair, setSelectedToPair] = useState(null);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const { showToast } = useToast();

    const accessToken = localStorage.getItem("AccessToken");

    const fetchPairData = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/pair`, {}, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken,
                },
            });

            const data = response.data;

            const paired = Object.values(data?.pairedAgents || {}).map((item, index) => ({
                id: index + 1,
                name: item.IPname || item.activationkey || 'Unnamed',
                status: 'paired',
            }));

            const awaited = Object.values(data?.awaited || {}).map((item, index) => ({
                id: index + 1000, // just offset to avoid clash
                name: item.IPname || item.activationkey || 'Unnamed',
                status: 'awaited',
            }));

            const unpairedRaw = data?.unpairedAgents || {};
            setUnpairedAgentsData(unpairedRaw);

            const unpaired = Object.entries(unpairedRaw).map(([key, item], index) => ({
                id: key,
                name: item.IPname || item.activationkey || 'Unnamed',
                status: 'unpaired',
            }));

            setAllEndpoints([...paired, ...awaited, ...unpaired]);
        } catch (error) {
            console.error('Error fetching endpoints:', error);
            setError(error?.message || error?.error);
        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        fetchPairData();
    }, []);

    useEffect(() => {
        if (location.state?.tab === "unpaired") return;

        if (allEndpoints.length > 0) {
            const hasUnpaired = allEndpoints.some(endpoint => endpoint.status === 'unpaired');

            if (hasUnpaired) {
                setActiveFilter("unpaired");
            } else {
                const hasAwaited = allEndpoints.some(endpoint => endpoint.status === 'awaited');
                setActiveFilter(hasAwaited ? "awaited" : "paired");
            }
        }
    }, [allEndpoints, location.state]);

    // Filter and search logic
    const filteredEndpoints = useMemo(() => {
        let filtered = allEndpoints;

        if (activeFilter !== 'all') {
            filtered = filtered.filter(endpoint => endpoint.status === activeFilter);
        }

        if (searchTerm) {
            filtered = filtered.filter(endpoint =>
                endpoint.name.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        return filtered;
    }, [searchTerm, activeFilter, allEndpoints])

    const getStatusBadge = (status) => {
        switch (status) {
            case 'paired':
                return (
                    <span className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-green-500 text-white">
                        Paired <Check className="ml-1 h-4 w-4" />
                    </span>
                );
            case 'awaited':
                return (
                    <span className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-yellow-500 text-white">
                        Awaited
                    </span>
                );
            case 'unpaired':
                return (
                    <span className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-red-500 text-white">
                        Unpaired
                    </span>
                );
            default:
                return null;
        }
    };

    const getFilterCount = (status) => {
        if (status === 'all') return allEndpoints.length;
        return allEndpoints.filter(endpoint => endpoint.status === status).length;
    };

    const handlePairClick = (id) => {
        const agentData = unpairedAgentsData[id];
        if (agentData) {
            setSelectedToPair(agentData);
            setShowConfirmModal(true);
        }
    };

    const handlePairConfirm = async () => {
        if (!selectedToPair) return;

        setPairingLoading(true);
        setPairingError('');

        try {
            const payload = {
                email: selectedToPair.email,
                IPname: selectedToPair.IPname,
                application: selectedToPair.application,
                activationkey: selectedToPair.activationkey,
                action: 'paired'
            };

            const response = await axiosInstance.post(`${config.API.FLASK_URL}/pair`, payload, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken,
                },
            });

            // Success handling (axios automatically handles 2xx status codes)
            setShowConfirmModal(false);
            setSelectedToPair(null);
            setPairingLoading(false);

            const Notification_local_Data = {
                id: Date.now(), // unique ID
                message: `✅ ${selectedToPair.IPname} New endpoint paired`,
                timestamp: new Date(),
                isRead: false,
            };

            sendNotification(`✅ ${selectedToPair.IPname} New endpoint paired`)

            // toast.success(`${selectedToPair.IPname} New endpoint paired`);
            showToast(`${selectedToPair.IPname} New endpoint paired`);
            setNotificationData((prev) => [...prev, Notification_local_Data]);

            const downloadEvent = `${selectedToPair.IPname} Endpoint is now Paired`;
            handleLogsSubmit(downloadEvent);
            fetchPairData();

        } catch (err) {
            // Handle both network errors and HTTP error responses
            const errorMessage = err.response?.data.message || err.message || 'Error during pairing. Please try again.';
            setPairingError(`Pairing failed: ${errorMessage}`);
            setPairingLoading(false);
        }
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

    if (error) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center p-8">
                    <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Error loading users</h3>
                    <p className="text-gray-500 dark:text-gray-400">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full mx-auto bg-gray-50">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-2">
                <div className="flex flex-wrap gap-2">
                    <button
                        onClick={() => setActiveFilter('paired')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeFilter === 'paired'
                            ? 'bg-green-500 text-white'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                            }`}
                    >
                        Paired ({getFilterCount('paired')})
                    </button>
                    <button
                        onClick={() => setActiveFilter('awaited')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeFilter === 'awaited'
                            ? 'bg-yellow-500 text-white'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                            }`}
                    >
                        Awaited ({getFilterCount('awaited')})
                    </button>
                    <button
                        onClick={() => setActiveFilter('unpaired')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeFilter === 'unpaired'
                            ? 'bg-red-500 text-white'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                            }`}
                    >
                        Unpaired ({getFilterCount('unpaired')})
                    </button>
                </div>

                <button
                    onClick={fetchPairData}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium transition-all duration-200"
                >
                    <RefreshCw className={`mr-2 h-4 w-4`} />
                    Refresh
                </button>

                {/* Search Bar - Right side */}
                <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                        type="text"
                        placeholder="Search endpoints..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm h-96 overflow-auto">

                <table className="w-full">
                    <thead className="sticky top-0 bg-blue-500 z-10">
                        <tr className="bg-blue-500 text-white">
                            <th className="px-2 py-2 text-left text-sm font-medium">Sr. No.</th>
                            <th className="px-2 py-2 text-left text-sm font-medium">Endpoints Name</th>
                            <th className="px-2 py-2 text-right text-sm font-medium">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {filteredEndpoints.length === 0 ? (
                            <tr>
                                <td colSpan="3" className="px-6 py-8 text-center text-gray-500">
                                    No endpoints found
                                </td>
                            </tr>
                        ) : (
                            filteredEndpoints.map((endpoint, index) => (
                                <tr key={endpoint.id} className="hover:bg-gray-50">
                                    <td className="px-2 py-2 text-sm text-gray-900">{index + 1}</td>
                                    <td className="px-2 py-2 text-sm text-gray-900">{endpoint.name}</td>
                                    <td className="px-2 py-2 text-right">
                                        {endpoint.status === 'unpaired' ? (
                                            <div className="flex justify-end gap-2">
                                                {getStatusBadge(endpoint.status)}
                                                <button
                                                    onClick={() => handlePairClick(endpoint.id)}
                                                    className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 text-sm"
                                                >
                                                    Pair
                                                </button>
                                            </div>
                                        ) : (
                                            getStatusBadge(endpoint.status)
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>

            </div>

            <div className="mt-4 text-sm text-gray-600">
                Showing {filteredEndpoints.length} of {allEndpoints.length} endpoints
            </div>

            {showConfirmModal && selectedToPair && (
                <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-lg p-6 w-80">
                        <h2 className="text-lg font-semibold mb-4">Confirm Pairing</h2>

                        <p className="mb-4">
                            Are you sure you want to pair <strong>{selectedToPair.IPname}</strong>?
                        </p>

                        {pairingError && (
                            <div className="mb-3 text-sm text-red-600 bg-red-100 p-2 rounded">
                                {pairingError}
                            </div>
                        )}

                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={() => {
                                    setShowConfirmModal(false);
                                    setPairingError('');
                                }}
                                className="px-4 py-2 bg-gray-300 rounded-md hover:bg-gray-400"
                                disabled={pairingLoading}
                            >
                                Cancel
                            </button>

                            <button
                                onClick={handlePairConfirm}
                                className={`px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center justify-center`}
                                disabled={pairingLoading}
                            >
                                {pairingLoading ? (
                                    <span className="flex items-center">
                                        <svg
                                            className="animate-spin h-4 w-4 mr-2 text-white"
                                            xmlns="http://www.w3.org/2000/svg"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                        >
                                            <circle
                                                className="opacity-25"
                                                cx="12"
                                                cy="12"
                                                r="10"
                                                stroke="currentColor"
                                                strokeWidth="4"
                                            ></circle>
                                            <path
                                                className="opacity-75"
                                                fill="currentColor"
                                                d="M4 12a8 8 0 018-8v8H4z"
                                            ></path>
                                        </svg>
                                        Pairing...
                                    </span>
                                ) : (
                                    'Confirm'
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {/* <ToastContainer position="top-right" autoClose={3000} /> */}

        </div>
    );
};

export default Pairing;