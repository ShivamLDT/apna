import { useState, useContext, useEffect } from "react";
import { Backupindex } from "../../Context/Backupindex";
import { UIContext } from "../../Context/UIContext";
import "./Savendpointdatafile.css"
import Dialogbox from "./DialogBox";
const Savendpointdata = ({ agentname }) => {
    const { popupEnable, setPopupEnable, setShowEndpointBackup } = useContext(UIContext);
    const { sourceData, setSourceData, setGetRestoreData, endpointagentname, setEndpointagentname } = useContext(Backupindex);
    const [endpoints, setEndpoints] = useState([]);
    const [showAlertPopup, setShowAlertPopup] = useState(false);

    const removeEndpoint = (index) => {
        const updated = [...endpoints];
        updated.splice(index, 1);
        setEndpoints(updated);
    };

    useEffect(() => {

        if (sourceData.length && endpointagentname) {
            const cleanedPaths = sourceData.map(path => {
                // 1. Remove leading/trailing quotes if present
                let temp = path.replace(/^["']|["']$/g, '');

                // 2. Replace all forward slashes with backslashes
                temp = temp.replace(/\//g, "\\");

                // 3. Collapse any double backslashes into single ones
                temp = temp.replace(/\\\\+/g, "\\");

                return temp;
            });



            const isDifferent = cleanedPaths.some((path, i) => path !== sourceData[i]);

            if (isDifferent) {
                setSourceData(cleanedPaths);
                setGetRestoreData(cleanedPaths)
                return; // Wait for next render before updating endpoints
            }

            const updatedEndpoints = cleanedPaths.map(path => ({ path }));
            setEndpoints(updatedEndpoints);

        }
    }, [sourceData, endpointagentname]);

    const removePath = (path) => {
        // setPaths(updated);
        const deletedVal = sourceData.filter((item) => item !== path.path)
        setSourceData(deletedVal)
    };

    const changeEndpoint = () => {
        setShowAlertPopup(true);
    }
    const HandleLocationButton = () => {
        setPopupEnable(true);
        setShowEndpointBackup(true);
    }
    return (
        <>
            <div className="endpoint-container">
                <button
                    onClick={HandleLocationButton}
                    type="button"
                    className={`text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800 ${sourceData?.length === 0 ? 'add-location-btn-1' : 'add-location-btn'
                        }`}
                >
                    Add Location
                </button>

                <button
                    onClick={changeEndpoint}
                    className={`text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800 ${sourceData?.length === 0 ? 'endpoint-change-endpoint-btn-1' : 'endpoint-change-endpoint-btn'
                        }`}
                >
                    Change Endpoint
                </button>
                {sourceData?.length > 0 ? <div className="endpoint-table-container">
                    <table className="endpoint-compact-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Endpoint</th>
                                <th>Backup Path</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {endpointagentname?.length === 0 ? (
                                <tr>
                                    <td colSpan="4">
                                        <div className="endpoint-empty-state">
                                            <svg viewBox="0 0 24 24">
                                                <path d="M10 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
                                            </svg>
                                            <h4>No backup paths configured</h4>
                                            <p>All backup paths have been removed</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : (
                                endpoints.length > 0 && endpoints?.map((item, index) => (
                                    <tr key={item.id || index}>
                                        <td>
                                            <div className="endpoint-row-number">{index + 1}</div>
                                        </td>
                                        <td>
                                            <span
                                                className={`endpoint-path-type-badge ${item.type}`}
                                            >
                                                {endpointagentname}
                                            </span>
                                        </td>
                                        <td>
                                            <div className="endpoint-path-info">
                                                <svg className="endpoint-folder-icon" viewBox="0 0 24 24">
                                                    <path d="M10 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
                                                </svg>
                                                <div className="endpoint-path-details">
                                                    <div className="endpoint-path-text">{item.path}</div>

                                                </div>
                                            </div>
                                        </td>
                                        <td style={{ textAlign: "center" }}>
                                            <button
                                                className="endpoint-remove-btn"
                                                onClick={() => removePath(item)}>
                                                Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div> : ""}
            </div>
            <div className="alert-box-highlight">
                {showAlertPopup ? <Dialogbox setShowAlertPopup={setShowAlertPopup} /> : ""}
            </div>
        </>
    );
}
export default Savendpointdata