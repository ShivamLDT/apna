import { useState, useEffect, useContext } from "react"
import config from "../../config";
import axios from 'axios';
import Desktop from "../../../src/assets/ActiveEnp.png";
import drive from "../../assets/drive.png";
import Backupmodeldata from "./Backupmodeldata";
import Savendpointdata from "./Savendpointdata";
import { Backupindex } from "../../Context/Backupindex";
import RestoreBackupModel from "../Restore/RestoreBackup/RestoreBackupModel";
import axiosInstance from "../../axiosinstance";
import { UIContext } from "../../Context/UIContext";
import { useJobs } from "../Jobs/JobsContext";
import LoadingComponent from "../../LoadingComponent";

const Endpoint = ({ setEndPoint, setSourceCheck }) => {
    const [serverData, setServerData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedEndpoint, setSelectedEndpoint] = useState(null);
    const [agentname, setAgentname] = useState();
    const [showpopup, setShowpopup] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const [visibleBackupModel, setvisibleBackupModel] = useState(true)
    const [endPointListPopup, setEndPointListPopup] = useState();
    const [showRestorePopup, setShowRestorePopup] = useState();
    const [popupTime, setPopupTime] = useState({ visible: false, message: "" });
    const [hasDataFromContext, setHasDataFromContext] = useState(false);

    const { popupEnable, setPopupEnable, DialogBox, folderlist, onechecktable, setonechecktable, onecheckendpointlisttable, setonecheckendpointlisttable, showEndpointBackup, setShowEndpointBackup } = useContext(UIContext);
    const { refreshClients } = useJobs();

    const { agentNameTable, setAgentNameTable, setSelectedEndpointName, sourceData, endpointagentname, setEndpointagentname, endPointAgentName, setEndPointAgentName } = useContext(Backupindex);

    const fetchServerData = async () => {

        if (!hasDataFromContext) {
            setLoading(true);
        }
        setError(null);
        try {
            const response = await axiosInstance.get(`${config.API.Server_URL}/clientnodes`, {
                headers: {
                    "Content-Type": "application/json",
                },
            });

            setServerData(response.data);
            if (response.data.result?.length > 0) {
                setSelectedEndpoint(response.data.result[0]);
            }
        } catch (error) {
            console.error("Error fetching server data:", error);
            setError(error.response?.data?.message || error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {

        if (sourceData && sourceData.length > 0 && endpointagentname) {
            setHasDataFromContext(true);
            setShowEndpointBackup(true);
            setonechecktable(false);
            setonecheckendpointlisttable(false);

            setAgentname(endpointagentname);
        } else {
            setHasDataFromContext(false);
            setonechecktable(true);
            setonecheckendpointlisttable(false);
        }

        refreshClients();
        fetchServerData();
    }, []);

    const handleGetAgentName = (username) => {
        const endpoint = serverData?.result?.find(item => item.agent === username);

        if (endpoint && endpoint.lastConnected === "False") {
            setPopupTime({ visible: true, message: "Your Endpoint Offline" });
            return
        }
        let arr = [username];
        setSelectedEndpointName(arr);
        setEndPointAgentName(username);
        setAgentname(username);
        setEndPoint(username);
        setShowpopup(true);
        setAgentNameTable(username)
        setPopupEnable(true)
        setEndpointagentname(username);
    }

    function HandleClickLocation() {
        setShowTable(true);
        setonechecktable(false);
        setonecheckendpointlisttable(true);
    }

    const closePopupTime = () => {
        setPopupTime({ visible: false, message: "" });
    };

    const handleRefresh = () => {
        fetchServerData();
    };

    const onlineEndpoints = serverData.result?.filter(job => job.lastConnected === "True") || [];
    // const hasNoEndpoints = !loading && !error && (!serverData.result || serverData.result.length === 0);
    const hasNoEndpoints = !loading && !error && onlineEndpoints.length === 0;

    return <div className={`bg-white p-6 rounded-xl shadow-sm w-full md:w-2/3 flex ${onechecktable ? 'endpointlistLocation' : 'endpointlist'}`}>

        {showEndpointBackup && hasDataFromContext ? (
            <Savendpointdata agentname={agentname} />
        ) : loading ? (
            // <div className="flex items-center justify-center h-full w-full">
            //     <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
            //         <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
            //             style={{ animation: 'oceanSlide 3s infinite' }} />
            //         <style>{`
            //                   @keyframes oceanSlide {
            //                          0% { transform: translateX(-150%); }
            //                          66% { transform: translateX(0%); }
            //                          100% { transform: translateX(150%); }
            //                   }                          
            //                 `}</style>
            //     </div>
            // </div>

            <LoadingComponent />
        ) : error ? (
            <div className="flex flex-col items-center justify-center h-full w-full gap-4">
                <p className="text-red-500 text-center">{error}</p>
                <button
                    onClick={handleRefresh}
                    className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 focus:outline-none"
                >
                    Refresh
                </button>
            </div>
        ) : hasNoEndpoints ? (
            <div className="flex flex-col items-center justify-center h-full w-full gap-4">
                <div className="text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <p className="text-gray-600 text-lg font-medium mb-2">No Endpoints Available</p>
                    <p className="text-gray-500 text-sm mb-4">There are currently no endpoints to display</p>
                </div>
                <button
                    onClick={handleRefresh}
                    className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 focus:outline-none"
                >
                    Refresh
                </button>
            </div>
        ) : (
            <>
                {onechecktable && !showEndpointBackup ? (
                    <>
                        <div className="btn-container">
                            <button
                                className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
                                onClick={HandleClickLocation}
                            >
                                Add Location
                            </button>
                        </div>
                    </>
                ) : null}

                {onecheckendpointlisttable ? (
                    serverData.result?.filter(job => job.lastConnected === "True").map((job, index) => (
                        <div className="show-enpoint-list" key={index} onClick={() => handleGetAgentName(job.agent)}>
                            <div className="show-endpoint">
                                <div className="show-endpoint-img">
                                    <span className="show-endpoint-emoji">🖥️</span>
                                </div>
                                <div className="show-endpoint-name">
                                    <h5 className="jobAgent-heading">
                                        {job.agent}
                                    </h5>
                                </div>
                            </div>
                        </div>
                    ))
                ) : null}


                {showEndpointBackup && !hasDataFromContext ? <Savendpointdata agentname={agentname} /> : null}
            </>
        )}

        {popupEnable && (
            <RestoreBackupModel
                setShowpopup={setShowpopup}
                setSourceCheck={setSourceCheck}
                setShowRestorePopup={setShowRestorePopup}
                setEndPointListPopup={setEndPointListPopup}
            />
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
    </div>
}

export default Endpoint