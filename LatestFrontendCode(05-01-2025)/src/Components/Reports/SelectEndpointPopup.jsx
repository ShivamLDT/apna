import { useState, useEffect, useContext } from 'react';
import useClientData from '../../Hooks/useClientData';
import './EndPointPopup.css'
import LoadingComponent from '../../LoadingComponent';

const SelectEndpointPopup = ({ setEndPointAgentName }) => {
    const { clientData, selectedEndpoint, loading, error, refetch } = useClientData();
    useEffect(() => {

    }, [selectedEndpoint])

    const [visible, setVisible] = useState(true);
    const [activeTab, setActiveTab] = useState('Name');
    const [searchTerm, setSearchTerm] = useState('');
    const [visibleBackupModel, setvisibleBackupModel] = useState(true)

    const handleClose = () => setVisible(false);

    const handleSelectEndpoint = (name) => {
        if (typeof setEndPointAgentName === 'function') {
            setEndPointAgentName(name);
        }
        setVisible(false);
    };


    useEffect(() => {
    }, [visibleBackupModel])

    const handleRefresh = (e) => {
        refetch();
    };

    const filteredEndpoints = Array.isArray(selectedEndpoint)
        ? selectedEndpoint.filter((ep) =>
            ep?.ip.includes(searchTerm) || ep?.agent?.toLowerCase().includes(searchTerm.toLowerCase())
        )
        : [];


    useEffect(() => {
        const escHandler = (e) => {
            if (e.key === 'Escape') handleClose();
        };
        document.addEventListener('keydown', escHandler);
        return () => document.removeEventListener('keydown', escHandler);
    }, []);

    if (!visible) return null;

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

    if (error) return <p>Error: {error}</p>;

    return (

        <>
            {visibleBackupModel ? <div className="full-wrapper_endpoint_data">
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

                        <div className="popup-content_endpoint_data">
                            {filteredEndpoints?.length === 0 ? (
                                <div className="text-center text-gray-500 dark:text-gray-300 py-8 col-span-full">
                                    No endpoints available
                                </div>
                            ) : activeTab === 'Name' ? (
                                <div className="endpoints-grid_endpoint_data">
                                    {filteredEndpoints.map((ep) => (
                                        <div
                                            key={ep.agent}
                                            className="endpoint-item_endpoint_data"
                                            onClick={() => handleSelectEndpoint(ep.agent)}
                                        >
                                            <div className={`endpoint-icon_endpoint_data ${ep.lastConnected !== "True" ? "offline-endpoint" : ""}`} />
                                            <div className="endpoint-name_endpoint_data">{ep.agent}</div>
                                        </div>
                                    ))}
                                </div>
                            ) : activeTab === 'IP Address' ? (
                                <div className="endpoints-grid_endpoint_data">
                                    {filteredEndpoints.map((ep) => (
                                        <div
                                            key={ep.agent}
                                            className="endpoint-item_endpoint_data"
                                            onClick={() => handleSelectEndpoint(ep.agent)}
                                        >
                                            <div className={`endpoint-icon_endpoint_data ${ep.lastConnected !== "True" ? "offline-endpoint" : ""}`} />
                                            <div className="endpoint-name_endpoint_data">{ep.ip || 'N/A'}</div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
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
                                            {filteredEndpoints.map((ep, index) => (
                                                <tr
                                                    key={ep.agent}
                                                    className="cursor-pointer hover:bg-blue-50"
                                                    onClick={() => handleSelectEndpoint(ep.agent)}
                                                >
                                                    <td className="px-4 py-2 border">{index + 1}</td>
                                                    <td className="px-4 py-2 border">{ep.agent}</td>
                                                    <td className="px-4 py-2 border">{ep.ip || 'N/A'}</td>
                                                    <td className={`px-4 py-2 border ${ep.lastConnected === "True" ? "text-green-600" : "text-red-600"}`}>{ep.lastConnected === "True" ? "Online" : "Offline" || 'N/A'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>

                    </div>
                </div>
            </div> : <Backupmodeldata />}
        </>
    );
};

export default SelectEndpointPopup;