import React, {
    useEffect,
    useState,
    useRef,
    useMemo,
    useCallback,
    useContext
} from "react";
import {
    Search,
    Filter,
    Users,
    RefreshCw,
    FileText,
    X,
    CircleArrowRight,
    Download,
    Hand,
} from "lucide-react";
import config from "../../config";
import nasLogo from "../../Image/nas.png";
import localLogo from "../../Image/localdisk.png";
import gdriveLogo from "../../Image/googledrive.png";
import s3Logo from "../../Image/aws1.png";
import azureLogo from "../../Image/azure.png";
import dropboxLogo from "../../Image/dropbox.png";
import oneDriveLogo from "../../Image/OneDrive.png";
import { Backupindex } from "../../Context/Backupindex";
import RestoreBackupModel from './RestoreBackup/RestoreBackupModel';
import ProcessingUI from "./RestoreProgressBar/ProcessingUI";
import RepoIcon from "../Reports/Jobs/RepoIcon"
import PDF from '../../assets/pdf.png';
import XL from '../../assets/XLSD.png';
import ENP from "../../Image/computer.png";
import LOCATION from "../../Image/placeholder.png";
import "./Restore.css";
import Selective from "./Selective";
import RestoreProgressPopup from "./RestoreProgressPopup";
import './RestoreModal.css';
import { XAxis } from "recharts";
import SelectEndpointPopup from "./SelectEndpointPopup";
import FileExtensions from "../Backup/FileExtensions";
import RestoreData from "./RestoreData/RestoreData"
import { el } from "date-fns/locale/el";
import RestoreReportTable from "./TableView/RestoreReportTable";
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import FilterJson from "../Backup/FileExtensions.json";
import CryptoJS from "crypto-js";
// import { Backupindex } from "../../Context/Backupindex";
import { NotificationContext } from "../../Context/NotificationContext";
import { RestoreContext } from "../../Context/RestoreContext";
import { UIContext } from "../../Context/UIContext";
import pdfIcon from "./ExtensionIcon/pdf.png";
import excelIcon from "./ExtensionIcon/excel.png";
import docxIcon from "./ExtensionIcon/docx.png";
import pptIcon from "./ExtensionIcon/ppt.png";
import exeIcon from "./ExtensionIcon/exe.png";
import textIcon from "./ExtensionIcon/text.png";
import jpgIcon from "./ExtensionIcon/jpg.png";
import pngIcon from "./ExtensionIcon/png.png";
import jpegIcon from "./ExtensionIcon/jpeg.png";
import gifIcon from "./ExtensionIcon/gif.png";
import zipIcon from "./ExtensionIcon/zip.png";
import mp3Icon from "./ExtensionIcon/mp3.png";
import mp4Icon from "./ExtensionIcon/mp4.png";
import rarIcon from "./ExtensionIcon/rar.png";
import csvIcon from "./ExtensionIcon/csv.png";
import sqlIcon from "./ExtensionIcon/sql.png";
import emlIcon from "./ExtensionIcon/eml.png";
import aiIcon from "./ExtensionIcon/ai.png";
import xmlIcon from "./ExtensionIcon/xml.png";
import DeleteIcon from "../../assets/delete.png"

import useSaveLogs from "../../Hooks/useSaveLogs";
import axios from "axios";
import axiosInstance from "../../axiosinstance";
import { useJobs } from "../Jobs/JobsContext";

import AlertComponent from "../../AlertComponent";
import LoadingComponent from "../../LoadingComponent";

const iconMap = {
    "./ExtensionIcon/pdf.png": pdfIcon,
    "./ExtensionIcon/excel.png": excelIcon,
    "./ExtensionIcon/docx.png": docxIcon,
    "./ExtensionIcon/ppt.png": pptIcon,
    "./ExtensionIcon/exe.png": exeIcon,
    "./ExtensionIcon/text.png": textIcon,
    "./ExtensionIcon/jpg.png": jpgIcon,
    "./ExtensionIcon/png.png": pngIcon,
    "./ExtensionIcon/jpeg.png": jpegIcon,
    "./ExtensionIcon/gif.png": gifIcon,
    "./ExtensionIcon/zip.png": zipIcon,
    "./ExtensionIcon/mp3.png": mp3Icon,
    "./ExtensionIcon/mp4.png": mp4Icon,
    "./ExtensionIcon/rar.png": rarIcon,
    "./ExtensionIcon/csv.png": csvIcon,
    "./ExtensionIcon/sql.png": sqlIcon,
    "./ExtensionIcon/eml.png": emlIcon,
    "./ExtensionIcon/ai.png": aiIcon,
    "./ExtensionIcon/xml.png": xmlIcon,
};

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


function encryptData(data) {
    const encryptedData = CryptoJS.AES.encrypt(data, "1234567890").toString();

    return encryptedData;
}


const Restore = () => {
    const { refreshClients } = useJobs();

    const parseCustomDate = (dateString) => {
        if (!dateString) return null;

        try {
            // Parse format: "22/07/2025, 04:09:28 PM"
            const [datePart, timePart] = dateString.split(', ');
            const [day, month, year] = datePart.split('/');

            // Convert to standard format for Date constructor
            const standardFormat = `${month}/${day}/${year} ${timePart}`;
            return new Date(standardFormat);
        } catch (error) {
            console.error('Error parsing date:', dateString, error);
            return null;
        }
    };

    const [computerName, setComputerName] = useState();
    const [endpointLoading, setEndpointLoading] = useState(false);
    const [data, setData] = useState([]);
    const [searchQuery, setSearchQuery] = useState(".");
    const [filteredResults, setFilteredResults] = useState([]);
    const [selectedValue, setSelectedValue] = useState([]);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);
    const { setIsSechduler, sourceData, endPointAgentName, setEndPointAgentName, getRestoreData, setGetRestoreData, setfileExtensionData, fileExtensionData, isSechduler, itemToDeleteFileExtension, } = useContext(Backupindex)
    const [itemId, setItemId] = useState();
    const { setRestorePayload, restoreTotalData, setRestoreTotalDat, showRestoreReportTable, setShowRestoreReportTable, setReStoreTableData, setStoreMultipleRestoreName, ValdidateRestorePopup, setOpenRestorePopup, setRestoreTotalData } = useContext(RestoreContext);
    const { showLivePopup, setShowLivePopup, showTreePopup } = useContext(UIContext)
    const { setCheckApi } = useContext(NotificationContext);
    const [isEditing, setIsEditing] = useState(true);
    const [selectedRows, setSelectedRows] = useState([]);
    const [systemList, setSystemList] = useState([]);
    const [responseData, setResponseData] = useState([]); // Initialize as an empty array
    const [storageType, setStorageType] = useState(() => {
        return decryptData(localStorage.getItem("storageType")) || "LAN";
    });
    const [selectedSystemIPA, setSelectedSystemIPA] = useState(() => {
        return localStorage.getItem("endpoint") || null;
    });
    const [showpopup, setShowpopup] = useState(false);
    const [sourceCheck, setSourceCheck] = useState()
    const [fileNameSend, setFileNameSend] = useState('')
    const [startDate, setStartDate] = useState(() => {
        const savedDate = localStorage.getItem("startDate");
        return savedDate;
    });
    const [endDate, setEndDate] = useState(() => {
        const savedDate = localStorage.getItem("endDate");
        return savedDate;
    });

    const [selectedAgentForRestore, setSelectedAgentForRestore] = useState(null);
    const [showCalendar, setShowCalendar] = useState(false);
    const accessToken = localStorage.getItem("AccessToken");
    const [showContainer, setShowContainer] = useState(false);
    const inputRef = useRef(null);
    const inputReff = useRef(null);
    // const isDisabled = decryptData(localStorage.getItem("user_privileges")) !== null;
    const [showRestoreData, setShowRestoreData] = useState(false); // New state for conditional rendering
    const [loading, setLoading] = useState(false);
    const [selectedPathss, setSelectedPathss] = useState([]);
    const [showRestorePopup, setShowRestorePopup] = useState(false);
    const [selectedRestoreItem, setSelectedRestoreItem] = useState(null);
    const [selectedStorageType, setSelectedStorageType] = useState(null);
    const [renameTargetLocation, setRenameTargetLocation] = useState("");
    const [showTLocationPopup, setShowTLocationPopup] = useState(false);
    const [fileExtensions, setFileExtensions] = useState();
    const [showNumforPopup, setShowNumforPopup] = useState(false);
    const [defaultTargetLocation, setDefaultTargetLocation] = useState("");
    const [endPointListPopup, setEndPointListPopup] = useState(false)
    const [searchTerm, setSearchTerm] = useState("");
    const [filterDataRepo, setFilterDataRepo] = useState("");
    const [filterAccuracyMin, setFilterAccuracyMin] = useState("");
    const [filterAccuracyMax, setFilterAccuracyMax] = useState("");
    const [showFilterPopup, setShowFilterPopup] = useState(false);
    const filterRef = useRef(null);
    const [fromDateFilter, setFromDateFilter] = useState("");
    const [toDateFilter, setToDateFilter] = useState("");
    const [targetlocation, settargetlocation] = useState("");
    const [folderData, setFolderData] = useState('')
    const [agendId, setAgendId] = useState();
    const [showProgress, setShowProgress] = useState(false);
    const [progressPopupData, setProgressPopupData] = useState("");
    const [storedownloadData, setstoredownloadData] = useState(null)
    const [removeEndPointName, setRemoveEndPointName] = useState(false);
    const [showSearchListBar, setShowSearchListBar] = useState(false);
    const [showNotEndPointPopup, setShowNotEndPointPopup] = useState(false);
    const [reStoreDataValidata, setReStoreDataValidata] = useState([])
    const [reStoreName, setReStoreName] = useState('');
    const [popupTime, setPopupTime] = useState({ visible: false, message: "" });
    const [notOpen, setNotOpen] = useState(false)

    const { handleLogsSubmit, userRole, profilePic, userName } = useSaveLogs();

    const [tempStorageType, setTempStorageType] = useState("");
    const [tempStartDate, setTempStartDate] = useState("");
    const [tempEndDate, setTempEndDate] = useState("");
    const [alert, setAlert] = useState(null);
    const [useClientNodesApi, setUseClientNodesApi] = useState(false);

    // const [inputValue, setInputValue] = useState(
    //     folderData || selectedRestoreItem?.target_location || ''
    // );

    // useEffect(() => {
    //     setInputValue(folderData || selectedRestoreItem?.target_location || '');
    // }, [folderData, selectedRestoreItem]);







    const [inputValue, setInputValue] = useState(
        folderData || selectedRestoreItem?.target_location || ''
    );
    const [restoreLocationEdited, setRestoreLocationEdited] = useState(false);

    // Update value only when props change
    useEffect(() => {
        if (restoreLocationEdited) {
            return;
        }
        let value = '';

        if (Array.isArray(folderData)) {
            value = folderData[folderData.length - 1] || ''; // latest selection only
        } else {
            value = folderData || selectedRestoreItem?.target_location || '';
        }

        setInputValue(value);
    }, [folderData, selectedRestoreItem, restoreLocationEdited]);
    useEffect(() => {
        setRestoreLocationEdited(false);
    }, [selectedRestoreItem]);



    useEffect(() => {
        if (getRestoreData) {
            getRestoreData?.map((item) => {
                // Replace backslashes with forward slashes and clean up multiple slashes
                const cleanedPath = item.replace(/\\/g, '/').replace(/\/+/g, '\\');
                return setFolderData((prev) => [
                    ...prev,
                    cleanedPath
                ]);
            });
        }
    }, [getRestoreData]);


    useEffect(() => {
        const fetchData = async () => {
            const jsonData = FilterJson;
            setData(jsonData);
        };
        fetchData();
    }, []);



    const SelectValue = (item) => {
        if (item.fileExtensions === '.all') {
            const updatedSelectedValue = [item];
            setSelectedValue(updatedSelectedValue);
            localStorage.setItem("SelectedExtension", JSON.stringify(updatedSelectedValue));
        } else {
            if (selectedValue.some(selectedItem => selectedItem.fileExtensions === '.all')) {
                setAlert({
                    message: "Already Selected all File Extension, Please Remove this.",
                    type: 'error'
                });
            } else if (!selectedValue.some(selectedItem => selectedItem.fileExtensions === item.fileExtensions)) {
                const updatedSelectedValue = [...selectedValue, item];
                setSelectedValue(updatedSelectedValue);
                // Save the updated array to local storage
                localStorage.setItem("SelectedExtension", JSON.stringify(updatedSelectedValue));
                localStorage.setItem("SelectedExtensionss", JSON.stringify(updatedSelectedValue));

            }
        }

        setSearchQuery("");
        updateFilteredResults("");
        setHighlightedIndex(-1);
    };

    useEffect(() => {
        if (searchQuery === ".") {
            const results = data.filter(
                (item) =>
                    !selectedValue.some(
                        (selectedItem) => selectedItem.fileExtensions === item.fileExtensions
                    )
            );
            setFilteredResults(results);
            setHighlightedIndex(0);
        }
    }, [searchQuery, data, selectedValue]);

    useEffect(() => {
        if (selectedValue && selectedValue.length > 0) {
            // Get all selected names as an array
            const selectedNames = selectedValue.map(item => item.Name);

            // If you want them as a comma-separated string:
            const namesString = selectedNames.join(', ');

            setFileNameSend(namesString); // or selectedNames if you prefer an array
        } else {
            setFileNameSend(''); // Clear if nothing is selected
        }
    }, [selectedValue]);

    const SelectValueRemove = (item) => {
        setSelectedValue(prevValues => {
            const updatedValues = prevValues.filter(selectedItem => selectedItem.fileExtensions !== item.fileExtensions);
            localStorage.setItem("SelectedExtension", JSON.stringify(updatedValues));
            localStorage.removeItem("SelectedExtension");
            localStorage.removeItem("SelectedExtensionss");
            return updatedValues;
        });
    };

    function closePopupTime() {
        setPopupTime({ visible: false, message: "" })
    }


    useEffect(() => {
        // const isDuplicate = ValdidateRestorePopup.some(
        //     (item) => JSON.stringify(item) === JSON.stringify(reStoreDataValidata)
        // );
        const isDuplicate = ValdidateRestorePopup.some(
            (item) => JSON.stringify(item) === JSON.stringify(reStoreDataValidata)
        );
        if (isDuplicate) {
            console.error("Error: This restore data already exists!");
            // setPopupTime({ visible: true, message: "The Restore Only Already Runing" })
        } else {
        }
    }, [ValdidateRestorePopup, reStoreDataValidata])


    const handleSearch = (e) => {
        const query = e.target.value;
        setSearchQuery(query);
        setShowSearchListBar(query.trim() !== ""); // ✅ Boolean logic
        updateFilteredResults(query);
        setHighlightedIndex(0);
    };

    const updateFilteredResults = (query) => {
        if (query) {
            const queryParts = query.toLowerCase().split(',').map(part => part.trim());
            const results = data.filter(item =>
                queryParts.some(part =>
                    (item.Name.toLowerCase().includes(part) ||
                        item.fileExtensions.toLowerCase().includes(part.startsWith('.') ? part : `.${part}`)) &&
                    !selectedValue.some(selectedItem => selectedItem.fileExtensions === item.fileExtensions)
                )
            );

            // Add the query to results if it doesn't match known extensions
            queryParts.forEach(part => {
                const normalizedPart = part.startsWith('.') ? part : `.${part}`;
                if (!results.some(result => result.fileExtensions.toLowerCase() === normalizedPart)) {
                    results.push({ fileExtensions: normalizedPart });
                }
            });

            setFilteredResults(results);
        } else {
            setFilteredResults([]);
        }
    };



    const handleKeyDown = (e) => {
        if (filteredResults.length > 0) {
            if (e.key === 'ArrowDown') {
                setHighlightedIndex(prevIndex => (prevIndex + 1) % filteredResults.length);
            } else if (e.key === 'ArrowUp') {
                setHighlightedIndex(prevIndex => (prevIndex - 1 + filteredResults.length) % filteredResults.length);
            } else if (e.key === 'Enter') {
                SelectValue(filteredResults[highlightedIndex]);
            }
        }
    };

    function handleBackspace() {
        setSelectedValue(prev => {
            const newArr = [...prev];
            newArr.pop();
            return newArr;
        });
    }

    useEffect(() => {
        setfileExtensionData(selectedValue);

        const updatedSelected = selectedValue.filter(item => item?.fileExtensions !== itemToDeleteFileExtension?.fileExtensions);
        // setSelectedValue(updatedSelected);
    }, [selectedValue]);

    useEffect(() => {
        const updatedSelected = selectedValue.filter(item => item?.fileExtensions !== itemToDeleteFileExtension?.fileExtensions);
        setSelectedValue(updatedSelected);
    }, [itemToDeleteFileExtension]);



    const getIconPath = (iconPath) => {
        return iconMap[iconPath] || null;
    };

    const isAllSelected = selectedValue.some(item => item.fileExtensions === '.all');


    useEffect(() => {
        setEndPointAgentName('');
        setGetRestoreData('');
    }, []);
    useEffect(() => {
        if (endPointAgentName) {
            setRemoveEndPointName(false)
        }
    }, [endPointAgentName])

    function handleBackspace() {
        setSelectedValue(prev => {
            const newArr = [...prev];
            newArr.pop();
            return newArr;
        });
    }




    useEffect(() => {
        if (removeEndPointName) {
            setEndPointAgentName('');
            setGetRestoreData('');
            setFolderData('')
        } else if (!getRestoreData) {
            setEndPointAgentName('');
        }
    }, [showRestorePopup]);



    const [restoreSortConfig, setRestoreSortConfig] = useState({
        key: null,
        direction: "ascending",
    });
    const [endpointSortConfig, setEndpointSortConfig] = useState({
        key: null,
        direction: "ascending",
    });

    const handleClosePopup = () => {
        setShowCalendar(false);
        localStorage.removeItem("target_location");
        localStorage.removeItem("targetAgentName");
        localStorage.removeItem("SelectedExtension");
        localStorage.removeItem("SelectedExtensionss");
        localStorage.removeItem("selectedIP");
        localStorage.removeItem("selectedFiles");
    };

    const handleSearchClick = () => {
        // Update the local storage value and close the popup
        setShowNumforPopup(false);
        localStorage.setItem("showNumforPopup", false);

        setShowRestorePopup(false);
        // Update the value of showNumforPopup in local storage when the popup is closed
        localStorage.setItem("showRestorePopup", false);
    };

    const handleProceedClick = () => {
        setDefaultTargetLocation(selectedRestoreItem.location); // Update defaultLocation with the selected item's location
        setSelectedPathss([selectedRestoreItem.location]); // Assuming you want to keep this as the selected location
        setShowNumforPopup(true);
        localStorage.setItem("showNumforPopup", true);
        // Update selectedPathss with the renamed location
        const updatedSelectedPathss =
            isEditing || isRenameEnabled
                ? renameTargetLocation
                : selectedPathss.join(", ");
        // Save updated selectedPathss to localStorage
        localStorage.setItem("selectedPathss", updatedSelectedPathss);
    };

    useEffect(() => {
        if (selectedPathss.length > 0) {
            setRenameTargetLocation(selectedPathss.join(", "));
        } else if (selectedRestoreItem) {
            setRenameTargetLocation(selectedRestoreItem.target_location);
        }
    }, [selectedPathss, selectedRestoreItem]);

    useEffect(() => {
        if (selectedRestoreItem) {
            setRenameTargetLocation(selectedRestoreItem.target_location);

        }
    }, [selectedRestoreItem]);

    const handleClosePopupL = () => {
        setShowTLocationPopup(false);
        localStorage.removeItem("targetAgentName");
        localStorage.removeItem("selectedPathss");
        localStorage.setItem("showRestorePopup", false);

        // Directly set renameTargetLocation based on selectedRestoreItem
        if (selectedRestoreItem) {
            setRenameTargetLocation(selectedRestoreItem.target_location);
        }
    };

    const handleDSTStorage = () => {
        // setShowDSTPopup(true);
    };

    const handleCloseDSTPopup = () => {
        // setShowDSTPopup(false);
    };

    const handleRenameTargetLocation = (e) => {
        const newValue = e.target.value;
        setRenameTargetLocation(newValue);
    };

    const handleClosePopupp = () => {
        setShowNumforPopup(false);
        setShowRestorePopup(false); // Close restore popup as well
        setShowPopup(false);
        localStorage.removeItem("target_location");
        localStorage.removeItem("targetAgentName");
        localStorage.removeItem("SelectedExtension");
        localStorage.removeItem("SelectedExtensionss");
        localStorage.setItem("showNumforPopup", false);
    };

    const handleAddLocation = async (selectedIP) => {
        setShowAgentPopupb(true);
        fetchDataFromServerr();

        try {
            if (!selectedSystemIPB) {
                return;
            }

            if (
                selectedSystemIPB === undefined ||
                selectedSystemIPB === null ||
                selectedSystemIPB === ""
            ) {
                console.error("No IP address selected.");
                return;
            }

            const selectedPathss = [...selectedItems]; // Get the currently selected items
            localStorage.setItem("selectedPathss", JSON.stringify(selectedPathss));
            // localStorage.setItem("selectedIP", selectedIP);
            setIsRenameEnabled(false); // Corrected to set it to false, assuming you want to disable it

            // Call fetchData with the selected IP address
            await fetchData(selectedSystemIPB);

            // Toggle the state to show the source popup
            // setShowTLocationPopup(true);
            setShowRestorePopup(true);
            // Perform any additional actions after fetching data if needed
        } catch (error) {
            // Log any errors that occur during the fetch operation
            console.error("Error fetching data:", error);
        }
    };



    const handleRestore = (item) => {
        setEndPointAgentName('')
        setReStoreName(item?.name)
        // setReStoreTableData([])
        setShowNotEndPointPopup(false)
        if (item === undefined) return;
        if (item === null) return;
        setInputValue(item?.target_location || '');
        setFolderData(item?.target_location || '');
        setGetRestoreData('');
        setSelectedValue([]);
        setRestoreTotalData(item);
        setstoredownloadData(item);
        setSelectedRestoreItem(item);
        localStorage.setItem("jobName", encryptData(item.name));
        setShowRestorePopup(true);
        // postId(item);
        setAgendId(item?.id);
    };

    const [storageStates, setStorageStates] = useState({
        LocalStorage: false,
        GoogleDrive: false,
        AwsS3: false,
        Dropbox: false,
        Azure: false,
        Nas: false,
        UNC: false,
        // ApnaCloud: false
        OneDrive: false,
    });

    const storageOptions = [
        {
            value: "LAN",
            label: "On-Premise",
            icon: localLogo,
            key: "LocalStorage",
        },
        {
            value: "Google Drive",
            label: "Google Drive",
            icon: gdriveLogo,
            key: "GoogleDrive",
        },
        { value: "AWSS3", label: "S3 Bucket", icon: s3Logo, key: "AwsS3" },
        { value: "AZURE", label: "Azure", icon: azureLogo, key: "Azure" },
        //  { value: "Dropbox", label: "Dropbox", icon: dropboxLogo, key: "Dropbox" },
        { value: "UNC", label: "NAS/LAN", icon: nasLogo, key: "UNC" },
        // { value: "Apna Cloud", label: "Apna Cloud", icon: cloudStorageLogo, key: "ApnaCloud" },
        {
            value: "ONEDRIVE",
            label: "OneDrive",
            icon: oneDriveLogo,
            key: "OneDrive",
        },
    ];

    useEffect(() => {
        const intervalId = setInterval(() => {
            const savedStates = decryptData(localStorage.getItem("storageStates"));
            if (savedStates) {
                setStorageStates(JSON.parse(savedStates));
            }
        }, 1000); // 1000 milliseconds = 1 second

        // Clean up the interval on component unmount
        return () => clearInterval(intervalId);
    }, []);
    const [visibleLabel, setVisibleLabel] = useState("");

    useEffect(() => {
        localStorage.setItem("storageType", encryptData(storageType));
    }, [storageType]);

    const handleStorageType = (value, label) => {
        setStorageType(value);
        setVisibleLabel(label);
        localStorage.setItem("storageType", encryptData(value));
    };

    useEffect(() => {
        function handleClickOutside(event) {
            if (filterRef.current && !filterRef.current.contains(event.target)) {
                setShowFilterPopup(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);


    const fetchDataFromServer = async () => {
        setEndpointLoading(true);
        try {
            refreshClients();
            const response = await axiosInstance.get(`${config.API.Server_URL}/restore_nodes`, {}, {
                headers: {
                    "Content-Type": "application/json",
                    token: accessToken,
                },
            });

            const data = response.data;

            // Sort the fetched data alphabetically by 'agent' field
            const sortedData = data.result.sort((a, b) => {
                if (a.agent.toLowerCase() < b.agent.toLowerCase()) return -1;
                if (a.agent.toLowerCase() > b.agent.toLowerCase()) return 1;
                return 0;
            });

            // Store sorted data in localStorage
            const seenAgents = new Set();
            const uniqueSortedData = sortedData.filter((item) => {
                if (seenAgents.has(item.agent)) {
                    return false;
                } else {
                    seenAgents.add(item.agent);
                    return true;
                }
            });

            //localStorage.setItem('clientnodes', JSON.stringify(uniqueSortedData));

            setSystemList(uniqueSortedData);

        } catch (error) {
            console.error(error);
        } finally {
            setEndpointLoading(false);
        }
    };

    const handleStartDateChange = (event) => {
        const value = event.target.value;
        setStartDate(value);
        localStorage.setItem("startDate", value);
        inputReff.current.blur();
    };

    const handleEndDateChange = (event) => {
        const value = event.target.value;
        setEndDate(value);
        localStorage.setItem("endDate", value);
        inputRef.current.blur();
    };

    const handleOpenPopup = (agent) => {
        setSelectedAgentForRestore(agent.agent); // Assuming agent.agent is the agent name you want to send
        setSelectedSystemIPA(
            agent.ipAddress.replace("http://", "").replace(":7777", "")
        ); // This looks like it's already used for endpoint, keep it if needed elsewhere
        setShowCalendar(true);
        setShowRestoreData(false); // Ensure endpoint table is shown when opening popup
    };

    const todayDate = new Date().toISOString().slice(0, 16);

    useEffect(() => {
        fetchDataFromServer();
    }, []);
    const formatDate = (date) => {
        const options = {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: true, // 12-hour format with AM/PM
        };
        const formattedDate = new Date(date).toLocaleString("en-US", options);
        const [datePart, timePart] = formattedDate.split(", ");
        const [month, day, year] = datePart.split("/");
        return `${day}/${month}/${year}, ${timePart}`;
    }

    const handleDateRangeChange = () => {
        if (!storageType) {
            // Changed === null to !storageType for better check
            return;
        }

        if (!selectedAgentForRestore) {
            // Check if an agent has b
            return;
        }

        if (!startDate || !endDate) {
            return;
        }

        localStorage.setItem("storageType", encryptData(storageType));
        localStorage.setItem("endpoint", selectedSystemIPA); // Keep this if needed for endpoint display
        localStorage.setItem("startDate", startDate);
        localStorage.setItem("endDate", endDate);
        localStorage.setItem("selectedAgentForRestore", selectedAgentForRestore); // Store the selected agent name

        postData(); // Call postData
    };
    function HandleInputfunc(e) {
        setFileNameSend(e.target.value);
    }
    const postData = async (agentName) => {
        setTempStorageType("");
        setTempStartDate("");
        setTempEndDate("");
        setShowFilterPopup(false);
        setSelectedAgentForRestore(agentName);
        setLoading(true);
        try {
            // Ensure selectedAgentForRestore is available
            if (!agentName) {
                return;
            }

            // const newStartdate = formatDate(startDate);
            // const newEnddate = formatDate(endDate);

            const today = new Date();
            const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1, 0, 0, 0);
            const endDate = today;

            const response = await axiosInstance.post(`${config.API.Server_URL}/restore`, {
                storageType: "",
                action: "fetchAll",
                startDate: formatDate(startOfMonth),
                endDate: formatDate(endDate),
                agentName: agentName, // Use the selected agent's name
            }, {
                headers: {
                    "Content-Type": "application/json",
                    token: accessToken,
                },
            });

            const data = response.data;

            // Assuming the backend now returns an array of restore objects
            setResponseData(Array.isArray(data) ? data : [data]); // Ensure data is an array
            setShowRestoreData(true); // Set to true to show restore data table
            setShowCalendar(false); // Close the calendar popup
            setLoading(false); // Assuming you have a setLoading state

            if (data.length === 0) {
                setShowRestoreData(true); // keep restore area open so alert can show
                setResponseData([]);
                setAlert({
                    message: `No restore data available for ${agentName} between ${formatDate(startOfMonth)} - ${formatDate(endDate)}.`,
                    type: 'error'
                });
                return;
            }

        } catch (error) {
            console.error("Error posting data:", error);
            setResponseData([]); // Set to empty array on error
            setShowRestoreData(true); // Keep restore area open so alert can show
            setLoading(false);
            const message = error.response?.data?.message
                || error.response?.data?.error
                || (typeof error.response?.data === 'string' ? error.response.data : null)
                || (error.response?.status === 500 ? 'Restore fetch failed: Internal Server Error. Check server logs.' : null)
                || error.message
                || 'Failed to load restore data.';
            setAlert({
                message,
                type: 'error'
            });
        }
    };

    const getProgressColorByPercentage = (percentage) => {
        if (percentage >= 100) return "bg-green-500";
        if (percentage >= 75) return "bg-blue-500";
        if (percentage >= 50) return "bg-yellow-500";
        if (percentage >= 25) return "bg-purple-500";
        return "bg-red-500";
    };

    const postId = async (item) => {
        try {
            localStorage.setItem("id", item.id);
            localStorage.setItem("agentName", encryptData(item.from_computer));
            const targetLocationToStore = renameTargetLocation || item.target_location;
            localStorage.setItem("target_location", encryptData(targetLocationToStore));

            const response = await axiosInstance.post(`${config.API.Server_URL}/restore`, {
                id: item.id,
                agentName: selectedRestoreItem?.from_computer,
                action: "browse",
                target_location: targetLocationToStore,
            }, {
                headers: {
                    "Content-Type": "application/json",
                    token: accessToken,
                },
            });

            // handle response
            // You can access response data with: response.data

        } catch (error) {
            console.error("Error posting data:", error);
        }
    };

    const sortData = useCallback((items, sortConfig) => {
        if (!sortConfig.key) {
            return items;
        }

        return [...items].sort((a, b) => {
            let aValue = a[sortConfig.key];
            let bValue = b[sortConfig.key];

            if (sortConfig.key === "last_modified") {
                const dateA = parseCustomDate(aValue);
                const dateB = parseCustomDate(bValue);
                if (!dateA || !dateB) return 0;
                return sortConfig.direction === "ascending"
                    ? dateA - dateB
                    : dateB - dateA;
            }

            // Handle other types
            if (sortConfig.key === "lastConnected") {
                aValue = a.lastConnected === "True" ? 1 : 0;
                bValue = b.lastConnected === "True" ? 1 : 0;
            } else if (typeof aValue === "string") {
                aValue = aValue.toLowerCase();
                bValue = bValue.toLowerCase();
            } else if (typeof aValue === "number") {
                // numbers fine
            } else if (sortConfig.key === "data_repo") {
                aValue = a.data_repo.toLowerCase();
                bValue = b.data_repo.toLowerCase();
            } else if (sortConfig.key === "wdone") {
                aValue = a.wdone || 0;
                bValue = b.wdone || 0;
            }

            if (aValue < bValue) {
                return sortConfig.direction === "ascending" ? -1 : 1;
            }
            if (aValue > bValue) {
                return sortConfig.direction === "ascending" ? 1 : -1;
            }
            return 0;
        });
    }, []);
    ;

    // Filtered and Sorted data for Restore Data Table
    const filteredRestoreData = useMemo(() => {
        let currentItems = [...responseData];

        // Apply search term filter (Name, Location)
        if (searchTerm) {
            currentItems = currentItems.filter(
                (item) =>
                    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    item.location.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Apply data repo filter
        if (filterDataRepo) {
            currentItems = currentItems.filter(
                (item) => item.data_repo.toLowerCase() === filterDataRepo.toLowerCase()
            );
        }

        // Apply accuracy filter
        if (filterAccuracyMin !== "") {
            currentItems = currentItems.filter(
                (item) => (item.wdone || 0) >= parseInt(filterAccuracyMin)
            );
        }
        if (filterAccuracyMax !== "") {
            currentItems = currentItems.filter(
                (item) => (item.wdone || 0) <= parseInt(filterAccuracyMax)
            );
        }

        // UPDATED: Date filtering with custom date format
        if (fromDateFilter) {
            const fromDate = new Date(fromDateFilter);
            currentItems = currentItems.filter((item) => {
                const itemDate = parseCustomDate(item.last_modified);
                return itemDate && itemDate >= fromDate;
            });
        }

        if (toDateFilter) {
            const toDate = new Date(toDateFilter);
            currentItems = currentItems.filter((item) => {
                const itemDate = parseCustomDate(item.last_modified);
                return itemDate && itemDate <= toDate;
            });
        }

        return currentItems;
    }, [
        responseData,
        searchTerm,
        filterDataRepo,
        filterAccuracyMin,
        filterAccuracyMax,
        fromDateFilter,
        toDateFilter,
    ]);

    // 3. Add clear filter function
    const clearDateFilters = () => {
        setTempStartDate("");
        setTempEndDate("");
    };

    const clearAllFilters = () => {
        postData(selectedAgentForRestore);
        // setSearchTerm("");
        setTempStorageType("");
        setFilterDataRepo("");
        setFilterAccuracyMin("");
        setFilterAccuracyMax("");
        setTempStartDate("");
        setTempEndDate("");
    };


    const sortedFilteredRestoreData = useMemo(() => {
        return sortData(filteredRestoreData, restoreSortConfig);
    }, [filteredRestoreData, restoreSortConfig, sortData]);

    // Filtered and Sorted data for Endpoint Table
    const filteredSystemList = useMemo(() => {
        let currentItems = [...systemList];

        // Apply search term filter (Endpoint Name, IP Address)
        if (searchTerm) {
            currentItems = currentItems.filter(
                (agent) =>
                    agent.agent.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    agent.ipAddress.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        // You can add other filters specific to the endpoint table here if needed

        return currentItems;
    }, [systemList, searchTerm]);

    const sortedFilteredSystemList = useMemo(() => {
        return sortData(filteredSystemList, endpointSortConfig);
    }, [filteredSystemList, endpointSortConfig, sortData]);

    // Functions to handle sort requests
    const handleRestoreSort = (key) => {
        let direction = "ascending";
        if (
            restoreSortConfig.key === key &&
            restoreSortConfig.direction === "ascending"
        ) {
            direction = "descending";
        }
        setRestoreSortConfig({ key, direction });
    };

    const handleEndpointSort = (key) => {
        let direction = "ascending";
        if (
            endpointSortConfig.key === key &&
            endpointSortConfig.direction === "ascending"
        ) {
            direction = "descending";
        }
        setEndpointSortConfig({ key, direction });
    };

    const handleDeleteCross = (index, fileName) => {
        const upDateFileVal = selectedValue.filter((item) => item?.fileExtensions !== fileName);
        setSelectedValue(upDateFileVal);
    }

    // if (loading) {
    //     return (
    //         <>
    //             <div className="flex items-center justify-center h-full">
    //                 <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
    //                     <div
    //                         className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
    //                         style={{ animation: "oceanSlide 3s infinite" }}
    //                     />
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

    function HandleOnSource() {
        setIsSechduler(true);
        setUseClientNodesApi(true);
        setEndPointListPopup(true);
        setShowRestorePopup(false);
    }
    const handleCloseRestorePopup = () => {
        setIsSechduler(false);
        setRemoveEndPointName(true);
        setShowRestorePopup(false);
        setInputValue('');
        setFolderData('');
        setGetRestoreData('');
        setEndPointAgentName('');
        setSelectedValue([]);
        setSelectedRestoreItem(null);
    }
    const HandleShowEndPointPopup = () => {
        setCheckApi(true);
        setUseClientNodesApi(false);
        setEndPointListPopup(true);
        setShowNotEndPointPopup(true);
    }


    const HandleProceed = async () => {
        setOpenRestorePopup(false);
        const action = "browse";

        // const agentName = endPointAgentName || selectedRestoreItem?.from_computer;
        const agentName = selectedRestoreItem?.from_computer;
        const Data = [reStoreName, inputValue, agentName];
        // const isDuplicate = ValdidateRestorePopup.some(item =>
        //     (item[1] === inputValue && item[2].toLowerCase() === agentName.toLowerCase()) ||
        //     (item[2].toLowerCase() === agentName.toLowerCase() && item[1] === inputValue)
        // );

        // if (isDuplicate) {
        //     setPopupTime({ visible: true, message: "The Restore Already Running" });
        //     return "";
        // }

        setShowProgress(true);
        setShowRestorePopup(false);
        // setInputValue('');
        // setFolderData('');
        // setGetRestoreData('');
        // setSelectedValue([]);

        const JsonObj = {
            action,
            agentName,
            id: agendId,
            storageType: storedownloadData?.data_repo,
            selectedExtensions: selectedValue.map(ext => ext.fileExtensions)
            // selectedPaths: [],
        }; //Third Line Payload

        let input_val;

        if (Array.isArray(inputValue) && inputValue.join(' ') !== "C:\\small deta mb") {
            input_val = inputValue.join(' ').replace(/\//g, '\\');
        } else {
            input_val = (inputValue || '').replace(/\//g, '\\');
        }
        if (!input_val) {
            input_val = selectedRestoreItem?.target_location || '';
        }

        const data = endPointAgentName ? endPointAgentName : selectedRestoreItem?.from_computer;

        const Payloadobj = {
            RestoreLocation: input_val,
            action: "restore",
            agentName: selectedRestoreItem?.from_computer,
            id: agendId,
            selectedExtensions: selectedValue.map(ext => ext.fileExtensions),
            sourceLocation: selectedRestoreItem?.location,
            storageType: storedownloadData?.data_repo,
            targetAgentName: data,
            targetLocation: selectedRestoreItem?.target_location
        };

        setRestorePayload(Payloadobj);

        try {
            const response = await axiosInstance.post(`${config.API.Server_URL}/restore`, JsonObj, {
                headers: {
                    "Content-Type": "application/json",
                    token: accessToken,
                },
            });

            const res = response.data;
            setProgressPopupData(res);

        } catch (error) {
            // Handle both network errors and HTTP error responses
            console.error("Request failed:", error);

            // If there's a response from the server (HTTP error)
            if (error.response) {
                console.error("Server responded with error:", error.response.status, error.response.data);
                setProgressPopupData(error.response.data);
            }

            setShowProgress(true);
            setShowRestorePopup(false);
        }
    };

    const handleDownloadExcel = () => {
        if (responseData && responseData.length > 0) {
            const fileName = "BackupLogs_report.xlsx";

            // Prepare data in Excel format
            const dataForExcel = responseData.map((item) => ({
                "Endpoint": item.from_computer,
                Destination: item.data_repo === "LAN" ? "On-Premise" : item.data_repo === "UNC" ? "NAS/LAN" : item.data_repo,
                Type: item.type === "file" ? "File" : "Folder",
                Name: item.name,
                Date: item.last_modified,
                "Target Location": item.target_location,
                Accuracy: item.wdone,

                // "Location Restore": item.location,
            }));

            // Convert data to Excel workbook
            const workbook = XLSX.utils.book_new();
            const worksheet = XLSX.utils.json_to_sheet(dataForExcel);

            /*change by ankita*/
            const headerStyle = { font: { bold: true }, alignment: { horizontal: "center" } };

            // Apply style to the header row
            for (let col = 0; col < dataForExcel[0].length; col++) {
                const cell = worksheet[XLSX.utils.encode_cell({ r: 0, c: col })];
                if (cell) {
                    cell.s = headerStyle;
                }
            }

            // Set column widths (example: for 4 columns)
            worksheet["!cols"] = [
                { wpx: 100 }, // Job Name column width
                { wpx: 100 }, // Created Time column width
                { wpx: 200 }, // Executed Time column width
                { wpx: 100 }, // Endpoint column width
                { wpx: 90 }, // Job Name column width



            ];

            XLSX.utils.book_append_sheet(workbook, worksheet, "Data");
            const downloadEvent = "Restore Report Excel Download";
            handleLogsSubmit(downloadEvent);
            // Generate and download Excel file
            XLSX.writeFile(workbook, fileName);
        } else {
            console.error("No data available to export");
        }
    };

    const MyUsers = ({ users }) => {
        const currentDate = new Date().toLocaleString(); // Get the current date
        const from_computer = Array.isArray(users) && users.length > 0 ? users[0].from_computer : 'Unknown Computer';
        const data_repo = Array.isArray(users) && users.length > 0 ? users[0].data_repo : 'Unknown';



        return (
            <Document>
                <Page size="A4" style={styles.page}>
                    <Image src="./apnalogo.png" style={styles.centeredLogo} />
                    <Text style={styles.sectionHeader}>Restore Data Report of {from_computer}</Text>
                    <Text style={styles.date}>Generated As On: {currentDate}</Text>

                    <View style={styles.table}>
                        {/* Table Headers */}
                        <View style={styles.tableHeaderRow}>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Sr. No.</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Destination</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Type</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Name</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Date</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Target Location</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Accuracy</Text>

                        </View>

                        {/* User Data */}
                        {Array.isArray(users) && users.length > 0 ? (
                            users.map((item, index) => {
                                const isEvenRow = index % 2 === 0;
                                return (
                                    <View
                                        key={index}
                                        style={[
                                            styles.tableRow,
                                            { backgroundColor: isEvenRow ? "#f5f7fc" : "#ffffff" },
                                        ]}
                                    >
                                        <Text style={[styles.tableCell, styles.borderRight]}>{index + 1}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{item.data_repo === "LAN" ? "On-Premise" : item.data_repo === "UNC" ? "NAS/LAN" : item.data_repo}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{item.type === "file" ? "File" : "Folder"}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{item.name}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>
                                            {item.last_modified}
                                        </Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{item.target_location}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>
                                            {item.wdone}
                                        </Text>

                                    </View>
                                );
                            })
                        ) : (
                            <Text style={{ padding: 5 }}>No restore data available</Text>
                        )}
                    </View>
                </Page>
            </Document>
        );
    };
    const styles = StyleSheet.create({
        page: {
            flexDirection: 'column',
            backgroundColor: '#FFFFFF',
            padding: 10,

        },
        sectionContainer: {
            marginBottom: 40,
            padding: 10,
            borderBottomWidth: 1,
            borderBottomColor: '#E4E4E4',
        },
        centeredLogo: {
            width: 100,
            height: 'auto',
            display: 'block',
            marginLeft: 'auto',
            marginRight: 'auto',
            marginBottom: 10,
        },


        sectionHeader: {
            fontSize: 16,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#007bff',
            marginBottom: 2,
            borderBottomWidth: 2,
            borderBottomColor: '#007bff',
            marginTop: -5,
            paddingBottom: 5,
        },

        table: {
            display: 'table',
            width: '100%',
            borderWidth: 1,
            borderColor: '#e9f0f9',
        },
        tableHeaderRow: {
            flexDirection: 'row',
            backgroundColor: '#FFFFFF',
            borderBottomWidth: 1,
            borderBottomColor: '#E4E4E4',
        },
        tableHeader: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 10,
            alignItems: 'center',
        },
        tableRow: {
            flexDirection: 'row',
        },
        tableCell: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 8,
            wordWrap: 'break-word',
            overflowWrap: 'break-word',
            whiteSpace: 'normal',
            verticalAlign: 'top',
            display: 'flex',
            flexDirection: 'column',
            height: '50px',
            alignItems: 'center',
        },
        date: {
            textAlign: 'center',
            fontSize: 12,
            color: '#777',
            marginTop: 2,
            marginBottom: 5,
            marginTop: 5,
        },
        repoImage: {
            maxWidth: '18%',
            height: 'auto',
        },
        jobNameCell: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 8,
            wordWrap: 'break-word',
            overflowWrap: 'break-word',
            whiteSpace: 'normal',
            verticalAlign: 'top',
            display: 'flex',
            flexDirection: 'column',
        },
        locationCell: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 8,
            wordWrap: 'break-word',
            overflowWrap: 'break-word',
            whiteSpace: 'normal',
            verticalAlign: 'top',
            display: 'flex',
            flexDirection: 'column',
        },
        text: {
            marginTop: '-8%',
        },
        textl: {
            marginLeft: '8%',
        },

    });


    const handleDownloadPDF = async () => {
        const pdfBlob = await pdf(<MyUsers users={responseData} />).toBlob();
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'restore_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = "Restore Report PDF Download";
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }


    const handleApplyFilters = async () => {
        // if (!tempStartDate || !tempEndDate) {
        //     alert("Please select a date range.");
        //     return;
        // }

        const start = tempStartDate
            ? new Date(tempStartDate)
            : new Date(new Date().getFullYear(), new Date().getMonth(), 1);

        const end = tempEndDate
            ? new Date(tempEndDate)
            : new Date();

        const isAllRepo = tempStorageType === "" || tempStorageType === "All Repositories";

        const payload = {
            storageType: isAllRepo ? "" : tempStorageType,
            ...(isAllRepo && { action: "fetchAll" }),
            startDate: formatDate(new Date(start)),
            endDate: formatDate(new Date(end)),
            agentName: selectedAgentForRestore,
        };


        setLoading(true);

        try {
            const response = await axiosInstance.post(
                `${config.API.Server_URL}/restore`,
                payload,
                {
                    headers: {
                        "Content-Type": "application/json",
                        token: accessToken,
                    },
                }
            );

            const data = response.data;

            if (!data || data.length === 0) {
                setShowRestoreData(true);
                setShowFilterPopup(false);
                setAlert({
                    message: `No restore data available for ${selectedAgentForRestore} between ${formatDate(new Date(tempStartDate))} - ${formatDate(new Date(tempEndDate))}.`,
                    type: 'error'
                });
                setTempStorageType("");
                setTempStartDate("");
                setTempEndDate("");
            } else {
                setResponseData(Array.isArray(data) ? data : [data]);
                setShowRestoreData(true);
                setShowFilterPopup(false);
            }

            // setTempStorageType("");
            // setTempStartDate("");
            // setTempEndDate("");

            setShowFilterPopup(false);
        } catch (error) {
            console.error("Error fetching restore data:", error);
            setResponseData([]);
            setShowRestoreData(false);
        } finally {
            setLoading(false);
        }
    };





    return (
        <>
            {alert && (
                <AlertComponent
                    message={alert.message}
                    type={alert.type}
                    onClose={() => setAlert(null)}
                />
            )}
            <div className="bg-white min-h-screen">
                {/* Header */}
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between px-4 md:px-6 py-4 border-b border-gray-200 gap-4">
                    <div className="flex items-center space-x-4 w-full md:w-auto">
                        <div className="relative w-full md:w-auto">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="Search for clients, agents or organizations"
                                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full md:w-80 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        {/* <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm flex items-center space-x-2">
                            <Search className="w-4 h-4" />
                            <span>Search</span>
                        </button> */}
                    </div>

                    <div className="flex flex-wrap items-center gap-2 md:space-x-3 w-full md:w-auto">
                        {showRestoreData && (
                            <>
                                <p className="flex items-center space-x-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white whitespace-nowrap">
                                    <span>🖥️ {selectedAgentForRestore}</span>
                                </p>

                                <button
                                    className="flex items-center space-x-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white hover:bg-gray-50"
                                    onClick={() => setShowFilterPopup(prev => !prev)}
                                >
                                    <Filter className="w-4 h-4" />
                                    <span>Filter</span>
                                </button>


                                <button className="flex items-center space-x-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white hover:bg-gray-50 whitespace-nowrap" onClick={HandleShowEndPointPopup}>
                                    <Users className="w-4 h-4" />
                                    <span>Select Endpoint</span>
                                    {/* <span className="bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center">
                                6
                            </span> */}
                                </button>

                            </>
                        )}

                        {showRestoreData && (
                            <div className="flex items-center gap-2">
                                <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                                <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />
                            </div>
                        )}

                        <button
                            className="flex items-center space-x-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white hover:bg-gray-50"
                            onClick={() =>
                                showRestoreData
                                    ? postData(selectedAgentForRestore)
                                    : fetchDataFromServer()
                            }
                        >
                            <RefreshCw className="w-4 h-4" />
                            <span>Refresh</span>
                        </button>

                    </div>

                    {/* Moved logic inside the flex container above for better wrapping
                   <div className="flex items-center space-x-3">
                        
                    </div>

                    <div className="flex items-center space-x-3">
                        

                    </div> */}

                </div>


                <div className="flex flex-col md:flex-row items-start md:items-center justify-between px-4 md:px-6 py-3 bg-gray-50 border-b border-gray-200 gap-2">
                    <div className="flex flex-wrap items-center gap-4">
                        <span className="text-sm text-gray-600">
                            Number of records:{" "}
                            {showRestoreData && responseData
                                ? `${sortedFilteredRestoreData.length} of ${responseData.length}`
                                : systemList.length}
                        </span>

                        {/* NEW: Active Filters Indicator */}
                        {showRestoreData && (filterDataRepo || filterAccuracyMin || filterAccuracyMax || fromDateFilter || toDateFilter) && (
                            <div className="flex items-center space-x-2">
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                    Filters Active
                                </span>
                                <button
                                    onClick={clearAllFilters}
                                    className="text-xs text-blue-600 hover:underline"
                                >
                                    Clear All
                                </button>
                            </div>
                        )}
                    </div>
                </div>


                {showRestoreData && responseData.length > 0 ? (
                    // Restore Data Table
                    <div className="overflow-x-auto w-full">
                        {/* Use inline style for min-width because Tailwind v2 doesn't support arbitrary min-w-[...] by default */}
                        <table className="w-full table-fixed border-collapse border border-green-800" style={{ minWidth: '1000px' }}>
                            <thead className="bg-gray-50 border-b border-gray-200 ">
                                <tr>
                                    <th
                                        className="border-collapse border border-green-800 w-1/12 px-6 py-3 text-center text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                        onClick={() => handleRestoreSort("data_repo")}
                                    >
                                        Repo
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "data_repo" &&
                                                restoreSortConfig.direction === "ascending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▲
                                        </span>
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "data_repo" &&
                                                restoreSortConfig.direction === "descending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▼
                                        </span>
                                    </th>
                                    <th
                                        className="border-collapse border border-green-800 w-1/5 px-6 py-3 text-center text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                        onClick={() => handleRestoreSort("name")}
                                    >
                                        Name
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "name" &&
                                                restoreSortConfig.direction === "ascending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▲
                                        </span>
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "name" &&
                                                restoreSortConfig.direction === "descending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▼
                                        </span>
                                    </th>
                                    <th
                                        className="border-collapse border border-green-800 w-1/5 px-6 py-3 text-center text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                        onClick={() => handleRestoreSort("last_modified")}
                                    >
                                        Date
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "last_modified" &&
                                                restoreSortConfig.direction === "ascending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▲
                                        </span>
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "last_modified" &&
                                                restoreSortConfig.direction === "descending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▼
                                        </span>
                                    </th>
                                    <th
                                        className="border-collapse border border-green-800 w-1/5 px-6 py-3 text-center text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                        onClick={() => handleRestoreSort("location")}
                                    >
                                        Location
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "location" &&
                                                restoreSortConfig.direction === "ascending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▲
                                        </span>
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "location" &&
                                                restoreSortConfig.direction === "descending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▼
                                        </span>
                                    </th>
                                    <th
                                        className="border-collapse border border-green-800 w-1/5 px-6 py-3 text-center text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                        onClick={() => handleRestoreSort("wdone")}
                                    >
                                        Accuracy
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "wdone" &&
                                                restoreSortConfig.direction === "ascending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▲
                                        </span>
                                        <span
                                            className={`ml-1 ${restoreSortConfig.key === "wdone" &&
                                                restoreSortConfig.direction === "descending"
                                                ? "text-gray-900 font-bold"
                                                : "text-gray-400"
                                                }`}
                                        >
                                            ▼
                                        </span>
                                    </th>
                                    <th className="border-collapse border border-green-800 w-1/12 px-6 py-3 text-center text-xs font-medium text-gray-500 tracking-wider">
                                        Restore
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {sortedFilteredRestoreData.map((item, index) => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 text-sm text-gray-900 border-collapse border border-green-800 text-center">
                                            <RepoIcon repo={item.data_repo} />
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900 border-collapse border border-green-800 rstTable break-all">
                                            {item.name}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900 border-collapse border border-green-800 rstTable">
                                            {item.last_modified}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900 border-collapse border border-green-800 rstTable break-all">
                                            {item.location}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900 border-collapse border border-green-800 rstTable">
                                            <div className="flex items-center gap-3">
                                                {/* Inline style for min-width since min-w-[50px] is JIT */}
                                                <div className="flex-1 bg-gray-100 rounded-full h-4" style={{ minWidth: '50px' }}>
                                                    <div
                                                        className={`h-4 font-bold text-white text-center text-xs rounded-full transition-all duration-300 ${getProgressColorByPercentage(
                                                            item.wdone
                                                        )}`}
                                                        style={{
                                                            width: `${Math.max(
                                                                0,
                                                                Math.min(item.wdone || 0, 100)
                                                            )}%`,
                                                        }}
                                                    >
                                                        {item.wdone}%
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-yellow-600 border-collapse border border-green-800 items-center">
                                            <Download
                                                className="cursor-pointer item-center mx-auto"
                                                onClick={() => {
                                                    handleRestore(item);
                                                }}
                                            />
                                        </td>

                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : showRestoreData && sortedFilteredRestoreData.length === 0 ? (
                    <>
                        <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                            <p className="text-lg font-medium">No restore data found</p>
                            <p className="text-sm mt-1">Try adjusting filters.</p>
                        </div>

                    </>
                ) : (

                    <>
                        {!showRestoreData && endpointLoading && (
                            <div className="flex items-center mt-40 justify-center h-full">
                                {/* <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
                                    <div
                                        className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
                                        style={{ animation: "oceanSlide 3s infinite" }}
                                    />
                                    <style>{`
      @keyframes oceanSlide {
        0% { transform: translateX(-150%); }
        66% { transform: translateX(0%); }
        100% { transform: translateX(150%); }
      }
    `}</style>
                                </div> */}
                                <LoadingComponent />;
                            </div>
                        )}

                        {!endpointLoading && (
                            // Endpoint Table
                            <div className="overflow-x-auto w-full">
                                <table className="w-full" style={{ minWidth: '800px' }}>
                                    <thead className="bg-gray-50 border-b border-gray-200">
                                        <tr>
                                            <th
                                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                                onClick={() => handleEndpointSort("idx")}
                                            >
                                                SR
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "idx" &&
                                                        endpointSortConfig.direction === "ascending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▲
                                                </span>
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "idx" &&
                                                        endpointSortConfig.direction === "descending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▼
                                                </span>
                                            </th>
                                            <th
                                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                                onClick={() => handleEndpointSort("agent")}
                                            >
                                                Endpoint Name
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "agent" &&
                                                        endpointSortConfig.direction === "ascending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▲
                                                </span>
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "agent" &&
                                                        endpointSortConfig.direction === "descending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▼
                                                </span>
                                            </th>
                                            <th
                                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                                onClick={() => handleEndpointSort("ipAddress")}
                                            >
                                                IP Address
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "ipAddress" &&
                                                        endpointSortConfig.direction === "ascending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▲
                                                </span>
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "ipAddress" &&
                                                        endpointSortConfig.direction === "descending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▼
                                                </span>
                                            </th>
                                            <th
                                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider cursor-pointer"
                                                onClick={() => handleEndpointSort("lastConnected")}
                                            >
                                                Last Connected
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "lastConnected" &&
                                                        endpointSortConfig.direction === "ascending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▲
                                                </span>
                                                <span
                                                    className={`ml-1 ${endpointSortConfig.key === "lastConnected" &&
                                                        endpointSortConfig.direction === "descending"
                                                        ? "text-gray-900 font-bold"
                                                        : "text-gray-400"
                                                        }`}
                                                >
                                                    ▼
                                                </span>
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                                                Action
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {sortedFilteredSystemList.map((agent, index) => (
                                            <tr
                                                key={agent.idx}
                                                className="hover:bg-gray-50"
                                            // onClick={() => postData(agent.agent)}
                                            >
                                                <td className="px-6 py-4 text-sm text-gray-900">
                                                    {index + 1}
                                                </td>
                                                <td className="px-6 py-4 text-sm text-blue-600 cursor-pointer">
                                                    {agent.agent}
                                                </td>

                                                <td className="px-6 py-4 text-sm text-gray-900">
                                                    {agent.ipAddress.length > 30 ? "NO IP" : agent.ipAddress
                                                        .replace("http://", "")
                                                        .replace(":7777", "")}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span
                                                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full
                                        ${agent.lastConnected == "True"
                                                                ? "bg-green-100 text-green-800"
                                                                : "bg-red-100 text-red-800"
                                                            }`}
                                                    >
                                                        {agent.lastConnected == "True" ? "Online" : "Offline"}
                                                    </span>
                                                </td>

                                                <td className="px-6 py-4 text-sm text-yellow-600">
                                                    <CircleArrowRight
                                                        onClick={() => postData(agent.agent)}
                                                        className="cursor-pointer"
                                                    />
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </>
                )}

                {showFilterPopup && showRestoreData && (
                    <div
                        // ref={filterRef}
                        className="absolute z-10 top-40 right-0 left-80 bg-white border border-gray-300 rounded-md shadow-lg p-4 space-y-3 w-72"
                    >
                        <div className="border-t pt-3 flex justify-end space-x-2">
                            <button
                                onClick={() => setShowFilterPopup(false)}
                                className="text-xs text-gray-600 hover:underline"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleApplyFilters}
                                className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                            >
                                Apply
                            </button>
                        </div>


                        {/* Repository Filter */}
                        <select
                            className="border border-gray-300 rounded px-2 py-1 text-sm w-full"
                            value={tempStorageType}
                            onChange={(e) => setTempStorageType(e.target.value)}
                        >
                            <option value="">All Repositories</option>
                            <option value="LAN">On-Premise</option>
                            <option value="Google Drive">Google Drive</option>
                            <option value="AWSS3">S3 Bucket</option>
                            <option value="AZURE">Azure</option>
                            <option value="UNC">NAS/LAN</option>
                            <option value="ONEDRIVE">OneDrive</option>
                        </select>


                        {/* Accuracy Filters 
                        <div className="flex space-x-2">
                            <input
                                type="number"
                                placeholder="Min Acc. %"
                                className="border border-gray-300 rounded px-2 py-1 text-sm w-1/2"
                                value={filterAccuracyMin}
                                onChange={(e) => setFilterAccuracyMin(e.target.value)}
                                min="0"
                                max="100"
                            />
                            <input
                                type="number"
                                placeholder="Max Acc. %"
                                className="border border-gray-300 rounded px-2 py-1 text-sm w-1/2"
                                value={filterAccuracyMax}
                                onChange={(e) => setFilterAccuracyMax(e.target.value)}
                                min="0"
                                max="100"
                            />
                        </div>
                        */}

                        {/* NEW: Date Range Filters */}
                        <div className="border-t pt-3">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium text-gray-600">Date Range</span>
                                {(fromDateFilter || toDateFilter) && (
                                    <button
                                        onClick={clearDateFilters}
                                        className="text-xs text-blue-500 hover:underline flex items-center"
                                    >
                                        <X className="w-3 h-3 mr-1" />
                                        Clear
                                    </button>
                                )}
                            </div>

                            <div className="space-y-2">
                                <div>
                                    <label className="text-xs text-gray-500 block mb-1">From Date:</label>
                                    <input
                                        type="datetime-local"
                                        value={tempStartDate}
                                        onChange={(e) => setTempStartDate(e.target.value)}
                                        max={new Date().toISOString().slice(0, 16)}
                                    />
                                </div>

                                <div>
                                    <label className="text-xs text-gray-500 block mb-1">To Date:</label>
                                    <input
                                        type="datetime-local"
                                        value={tempEndDate}
                                        onChange={(e) => setTempEndDate(e.target.value)}
                                        min={tempStartDate || ""}
                                        max={new Date().toISOString().slice(0, 16)}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Clear All Filters Button */}
                        <div className="border-t pt-3">
                            <button
                                onClick={clearAllFilters}
                                className="w-full text-xs text-red-500 hover:bg-red-50 py-2 rounded border border-red-200"
                            >
                                Clear All Filters
                            </button>
                        </div>
                    </div>
                )}


                {showCalendar && (
                    <div className="popup-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="popup-card bg-white rounded-lg p-6 max-h-screen overflow-y-auto" style={{ width: '95%', maxWidth: '600px' }}>
                            <h2 className="text-blue-500 popup-title text-xl font-bold mb-4">Data Restore {reStoreName}</h2>

                            <div className="storage-buttons flex flex-wrap gap-2 mb-4 justify-center">
                                {storageOptions
                                    .filter((option) => storageStates[option.key])
                                    .map((option) => (
                                        <button
                                            key={option.value}
                                            className={`storage-btn flex flex-col items-center justify-center p-2 border rounded hover:bg-blue-50 ${storageType === option.value ? "active bg-blue-100 border-blue-500" : "border-gray-200"
                                                }`}
                                            onClick={() =>
                                                handleStorageType(option.value, option.label)
                                            }
                                            data-tooltip={option.label}
                                            required
                                        >
                                            <img src={option.icon} alt={option.label} className="w-8 h-8 mb-1" />
                                            {storageType === option.value && (
                                                <span className="text-xs">{option.label}</span>
                                            )}
                                        </button>
                                    ))}
                            </div>

                            <div className="agent-input mb-4">
                                <input
                                    type="text"
                                    readOnly
                                    className="w-full p-2 border rounded bg-gray-100"
                                    value={selectedAgentForRestore}
                                    placeholder="Agent Name"
                                />

                                {visibleLabel === "Google Drive" && (
                                    // <div className="blur-background">
                                    //   <Gdrive onClose={handleClose} />
                                    // </div>
                                    <div></div>
                                )}
                                {visibleLabel === "Dropbox" && (
                                    // <div className="blur-background">
                                    //   <Dropbox onClose={handleClose} />
                                    // </div>
                                    <div></div>
                                )}
                                {visibleLabel === "Azure" && (
                                    // <div className="blur-background">
                                    //   <Azure onClose={handleClose} />
                                    // </div>
                                    <div></div>
                                )}
                                {/* {visibleLabel === "NAS/LAN" && (
                  <div className="blur-background">
                    <Lan onClose={handleClose} />
                  </div>
                )} */}
                                {visibleLabel === "NAS" && (
                                    <div className="blur-background">
                                        {/* <Nas onClose={handleClose} /> */}
                                    </div>
                                )}
                                {/* {visibleLabel === "LAN" && (
                  <div className="blur-background">
                    <UNC onClose={handleClose} />
                  </div>
                )} */}

                                {visibleLabel === "OneDrive" && (
                                    // <div className="blur-background">
                                    //   <OneDrive onClose={handleClose} />
                                    // </div>
                                    <div></div>
                                )}
                            </div>

                            <div className="date-range flex flex-col md:flex-row gap-4 mb-6">
                                <label className="flex-1">
                                    <span className="block text-sm text-gray-600 mb-1">From:</span>
                                    <input
                                        ref={inputReff}
                                        type="datetime-local"
                                        className="w-full border rounded p-2"
                                        value={startDate || ""}
                                        max={todayDate}
                                        onChange={handleStartDateChange}
                                    />
                                </label>
                                <label className="flex-1">
                                    <span className="block text-sm text-gray-600 mb-1">To:</span>
                                    <input
                                        ref={inputRef}
                                        type="datetime-local"
                                        className="w-full border rounded p-2"
                                        value={endDate || ""}
                                        min={startDate || todayDate}
                                        max={todayDate}
                                        onChange={handleEndDateChange}
                                    />
                                </label>
                            </div>

                            <div className="action-buttons flex justify-end gap-3">
                                <button className="btn cancel px-4 py-2 border rounded text-gray-600 hover:bg-gray-50" onClick={handleClosePopup}>
                                    Cancel
                                </button>
                                <button className="btn search px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" onClick={handleDateRangeChange}>
                                    Search
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Popup for restoring files */}

            </div>
            {showRestorePopup && (

                <div>
                    {/* <RestoreProgressPopup /> */}

                    <div className="restore-popup-model-overlay-container">
                        <div className="restore-popup-model-overlay-background-particles">
                            {/* Particles */}
                        </div>
                        <div className="restore-popup-model-overlay-background-blur"></div>

                        <div className="restore-popup-model-overlay-modal">
                            {/* Modal Content */}
                            <div className="restore-popup-model-overlay-modal">
                                <div className="restore-popup-model-overlay-modal-header">
                                    <h2 className="restore-popup-model-overlay-modal-title text-medium break-all">Restore: {reStoreName}</h2>
                                    <button onClick={handleCloseRestorePopup} className="restore-popup-model-overlay-close-btn">×</button>
                                </div>

                                <div className="restore-popup-model-overlay-modal-body">
                                    <div className="restore-popup-model-overlay-backup-info">
                                        <div className="restore-popup-model-overlay-backup-date">Backup Taken On</div>
                                        <div className="restore-popup-model-overlay-backup-time">{selectedRestoreItem?.last_modified}</div>
                                        <div className="restore-popup-model-overlay-status-badge">
                                            <div className="restore-popup-model-overlay-pulse"></div>
                                            Ready
                                        </div>
                                    </div>


                                    <div className="bg-white rounded-lg p-3 w-full shadow-sm border border-gray-200 mb-4 ">
                                        <div className="space-y-2">
                                            {/* Local Storage Item */}
                                            <div className="flex items-center space-x-2 p-3 bg-white rounded border border-gray-200 w-full">
                                                {/* <div className="flex-shrink-0 repoicon">
                                                    <RepoIcon  repo={selectedRestoreItem?.data_repo}/>
                                                </div> */}
                                                <div className="repoicon">
                                                    <RepoIcon repo={selectedRestoreItem?.data_repo} className="m-0 p-0" />
                                                </div>
                                                <div className="flex-1 min-w-0" style={{ marginLeft: "-70px" }}>
                                                    <div className="text-gray-900 font-medium text-sm">
                                                        {selectedRestoreItem?.data_repo === "LAN" ? "On-Premise" : selectedRestoreItem?.data_repo === "UNC" ? "NAS/UNC" : selectedRestoreItem?.data_repo}
                                                    </div>
                                                    <div className="text-gray-600 text-xs truncate">
                                                        {selectedRestoreItem?.location}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Source Data Item */}
                                            <div className="flex items-center space-x-3 p-3 bg-white rounded border border-gray-200 w-full">
                                                <div className="text-lg flex-shrink-0">
                                                    🖥️
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="text-gray-900 font-medium text-sm">
                                                        Endpoint
                                                    </div>
                                                    <div className="text-gray-600 text-xs">
                                                        {selectedRestoreItem?.from_computer}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="restore-popup-model-overlay-section" >
                                        <div className="restore-popup-model-overlay-section-title">🎯 Target Endpoint</div>
                                        <div className="restore-popup-model-overlay-target-endpoint">
                                            <input type="text" value={endPointAgentName ? endPointAgentName : selectedRestoreItem?.from_computer} className="restore-popup-model-overlay-endpoint-input" placeholder="Please select target endpoint" readOnly />
                                            <button className="restore-popup-model-overlay-select-btn" onClick={HandleOnSource}  ><span>🖥️</span> Change Endpoint</button>
                                        </div>
                                    </div>

                                    <div className="restore-popup-model-overlay-section">
                                        <div className="restore-popup-model-overlay-section-title">📍 Target Location</div>
                                        <div className="restore-popup-model-overlay-target-location">

                                            <input type="text"
                                                value={inputValue}
                                                onChange={(e) => {
                                                    setInputValue(e.target.value);
                                                    setRestoreLocationEdited(true);
                                                }}
                                                className="restore-popup-model-overlay-location-input" />
                                        </div>
                                    </div>

                                    <div className="restore-popup-model-overlay-section">
                                        <div className="restore-popup-model-overlay-section-title">🔍 File Extensions</div>
                                        <div className="fileExtension_Container">
                                            {fileExtensionData.map((item, index) => (
                                                <div className="SelectedData" key={index}>
                                                    <img src={getIconPath(item.fileIcon)} className="SelectIcon" />
                                                    <h5 className="Filter-h5">{item.fileExtensions}</h5>
                                                    <span onClick={() => SelectValueRemove(item)} className="closebtn">
                                                        {/* <IoCloseSharp /> */}
                                                    </span>
                                                    <img onClick={() => handleDeleteCross(index, item?.fileExtensions)} src={DeleteIcon} className="delete_icon" alt="" srcset="" />
                                                </div>
                                            ))}

                                        </div>
                                        <input type="text" value={searchQuery}
                                            onChange={handleSearch}
                                            onKeyDown={(e) => {
                                                if (e.key === "Backspace") {
                                                    handleBackspace();
                                                }
                                            }} className="restore-popup-model-overlay-extension-input" placeholder="Search Extensions (leave blank for all files)" />
                                        {showSearchListBar && filteredResults.length > 0 && (
                                            <div className="SearchList">
                                                {filteredResults.map((item, index) => (
                                                    (isAllSelected && item.fileExtensions !== '.all') ? null : (
                                                        <button
                                                            onClick={() => SelectValue(item)}
                                                            key={index}
                                                            className={highlightedIndex === index ? 'highlighted' : ''}
                                                        >
                                                            <img src={getIconPath(item.fileIcon)} className="Selectfile-icon" />
                                                            <p>{item.fileExtensions}</p>
                                                            <p>{item.Name}</p>
                                                        </button>
                                                    )
                                                ))}
                                            </div>
                                        )}

                                    </div>
                                </div>

                                <div className="restore-popup-model-overlay-modal-footer">
                                    <button className="restore-popup-model-overlay-proceed-btn" onClick={HandleProceed} >
                                        <span className="btn-text">Proceed</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {endPointListPopup && <SelectEndpointPopup setEndPointListPopup={setEndPointListPopup} setShowRestorePopup={setShowRestorePopup} showNotEndPointPopup={showNotEndPointPopup} setShowNotEndPointPopup={setShowNotEndPointPopup} postData={postData} forceClientNodes={useClientNodesApi} />}
            {showProgress && <RestoreData reStoreName={reStoreName} setShowProgress={setShowProgress} progressPopupData={progressPopupData} setShowRestorePopup={setShowRestorePopup} />}
            {showTreePopup && <RestoreBackupModel setShowRestorePopup={setShowRestorePopup} setEndPointListPopup={setEndPointListPopup} setShowpopup={setShowpopup} setSourceCheck={setSourceCheck} />}
            {showLivePopup && <ProcessingUI showProgress={showProgress} setShowProgress={setShowProgress} setShowRestorePopup={setShowRestorePopup} />}
            {showRestoreReportTable && <RestoreReportTable setShowRestorePopup={setShowRestorePopup} setShowProgress={setShowProgress} />}


            {popupTime.visible && (
                <div className="fixed inset-0 visible-popup flex items-center justify-center z-[100000]">
                    <div className="fixed inset-0 bg-black bg-opacity-30"></div>
                    <div className="bg-white rounded-lg p-6 shadow-xl text-center relative z-10 m-4" style={{ marginTop: "85px" }}>
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

        </>
    );
};

export default Restore;