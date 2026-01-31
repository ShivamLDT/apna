import React, { useContext, useEffect, useState } from "react";
import { ChevronRight, ChevronDown, HardDrive, CheckCircle, AlertCircle, Clock, Database, Monitor, FolderOpen, RefreshCw } from "lucide-react";
import config from "../../config";
import RepoIcon from "./Jobs/RepoIcon";
import './Server.css';
import SelectEndpointPopup from "../Restore/SelectEndpointPopup";
import JobFilterPopup from "./Jobs/JobFilterPopup";
import { Backupindex } from "../../Context/Backupindex";
import * as XLSX from "xlsx";
import PDF from '../../assets/pdf.png';
import XL from '../../assets/XLSD.png';
import useSaveLogs from "../../Hooks/useSaveLogs";
import axios from "axios";
import axiosInstance from "../../axiosinstance";
import pdfMake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';
import { NotificationContext } from "../../Context/NotificationContext";
import { RestoreContext } from "../../Context/RestoreContext";
import AlertComponent from "../../AlertComponent";
import CryptoJS from "crypto-js";
import { UIContext } from '../../Context/UIContext';
import LoadingComponent from "../../LoadingComponent";
// Set fonts for pdfMake
// pdfMake.vfs = pdfFonts.pdfMake.vfs;


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

const BackupLogs = () => {
    const [expandedMain, setExpandedMain] = useState({});
    const [expandedLogs, setExpandedLogs] = useState({});
    const [restoreData, setRestoreData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [agentName, setAgentName] = useState(null);
    const [filters, setFilters] = useState({ name: '', repo: '', status: '', fromDate: '', toDate: '' });
    const [showFilterPopup, setShowFilterPopup] = useState(false);
    const [showSelectEndpointCode, setShowSelectEndpointCode] = useState(false)
    const { showRestoreReportEndPoint, setShowRestoreReportEndPoint } = useContext(RestoreContext);
    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();
    const { checkApi, setCheckApi, } = useContext(NotificationContext);
    const [applyFilterTrigger, setApplyFilterTrigger] = useState(0);
    const [alert, setAlert] = useState(null);
    const { setShowTreePopup, showBackuplog, setShowBackuplog } = useContext(UIContext);
    const parseLastModified = (str) => {
        if (!str) return null;

        // Example input: "04/07/2025, 07:38:34 PM"
        const [datePart, timePart] = str.split(", ");
        const [day, month, year] = datePart.split("/").map(Number);

        // Ensure 24-hour format
        const [time, period] = timePart.split(" ");
        let [hours, minutes, seconds] = time.split(":").map(Number);
        if (period === "PM" && hours < 12) hours += 12;
        if (period === "AM" && hours === 12) hours = 0;

        return new Date(year, month - 1, day, hours, minutes, seconds);
    };

    useEffect(() => {
        if (!agentName && checkApi) {
            setShowSelectEndpointCode(true);
        }
    }, [checkApi])

    const normalizedData = restoreData.map(item => ({
        ...item,
        job_repo: item.data_repo,
        computerName: item.from_computer,
        done_time: item.last_modified,
        status: item.wdone <= 50 ? 'failed' : 'success'
    }));

    const filteredData = normalizedData.filter(item => {
        const name = item.computerName || item.nodeName || '';
        const nameMatch = !filters.name || name === filters.name;
        const repoMatch = !filters.repo || item.job_repo === filters.repo;
        const statusMatch = !filters.status || item.status === filters.status;

        const jobDate = parseLastModified(item.done_time);
        const from = filters.fromDate ? new Date(filters.fromDate) : null;
        const to = filters.toDate ? new Date(filters.toDate) : null;

        const dateMatch =
            (!from || (jobDate && jobDate >= from)) &&
            (!to || (jobDate && jobDate <= new Date(to.getTime() + 86400000 - 1)));
        return nameMatch && repoMatch && statusMatch && dateMatch;
    });

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

    const fetchRestoreData = async (selectedAgent) => {
        setShowFilterPopup(false);

        const userPrivileges = JSON.parse(decryptData(localStorage.getItem("user_privileges")) || "{}");
        if (userRole === "Employee" && !userPrivileges.restoreReadWrite) {
            setAlert({
                message: "You do not have permission to access this section.",
                type: 'error'
            });
            return;
        }

        if (!selectedAgent) return;
        const today = new Date();
        const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1, 0, 0, 0);
        const endDate = today;
        setLoading(true);
        try {
            const response = await axiosInstance.post(`${config.API.Server_URL}/restore`, {
                action: "fetchAll",
                agentName: selectedAgent,
                startDate: formatDate(startOfMonth),
                endDate: formatDate(endDate),
            }, {
                headers: {
                    "Content-Type": "application/json",
                },
            });

            setRestoreData(response.data);
        } catch (error) {
            console.error("Restore fetch error:", error);
        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        if (showSelectEndpointCode) return;         // popup is open → don't fetch
        if (!showRestoreReportEndPoint) return;     // no endpoint selected yet → don't fetch
        fetchRestoreData(showRestoreReportEndPoint); // fetch only after choosing endpoint
    }, [showRestoreReportEndPoint, showSelectEndpointCode]);



    const toggleMainRow = (id) => {
        setExpandedMain((prev) => ({ ...prev, [id]: !prev[id] }));
    };

    const toggleLogRow = (id) => {
        setExpandedLogs((prev) => ({ ...prev, [id]: !prev[id] }));
    };

    useEffect(() => {
        // Prevent this from running on the very first render
        if (applyFilterTrigger === 0) {
            return;
        }

        const handleApplyFilters = async () => {
            // if (!filters.fromDate || !filters.toDate) {
            //     alert("Please select a date range.");
            //     return;
            // }

            const start = filters.fromDate
                ? new Date(filters.fromDate)
                : new Date(new Date().getFullYear(), new Date().getMonth(), 1);

            start.setHours(0, 0, 0, 0);

            const end = filters.toDate
                ? new Date(filters.toDate)
                : new Date();

            end.setHours(23, 59, 59, 999);

            const formatWithTime = (date) =>
                date.toLocaleString("en-GB", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true,
                });

            const isAllRepo = filters.repo === "" || filters.repo === "All Repositories";
            const agentName = showRestoreReportEndPoint || "";

            const payload = {
                storageType: isAllRepo ? "" : filters.repo,
                ...(isAllRepo && { action: "fetchAll" }),
                startDate: formatWithTime(start),
                endDate: formatWithTime(end),
                agentName: agentName,
            };

            setLoading(true);
            try {
                const response = await axiosInstance.post(
                    `${config.API.Server_URL}/restore`,
                    payload,
                    {
                        headers: {
                            "Content-Type": "application/json",
                        },
                    }
                );

                const data = response.data;

                if (!data || data.length === 0) {
                    setRestoreData([]);
                } else {
                    setRestoreData(Array.isArray(data) ? data : [data]);
                }

                // setFilters({ name: "", repo: "", status: "", fromDate: "", toDate: "" });
                setShowFilterPopup(false);
            } catch (error) {
                console.error("Error fetching restore data:", error);
                setRestoreData([]);
            } finally {
                setLoading(false);
            }
        };
        handleApplyFilters();

    }, [applyFilterTrigger]);


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

    const getProgressColorByPercentage = (percentage) => {
        if (percentage >= 100) return "bg-green-500";
        if (percentage >= 75) return "bg-blue-500";
        if (percentage >= 50) return "bg-yellow-500";
        if (percentage >= 25) return "bg-purple-500";
        return "bg-red-500";
    };

    const getStorageLabel = (storageType) => {
        const labels = {
            'LAN': 'On-Premise',
            'GDRIVE': 'Google Drive',
            'UNC': 'NAS',
            'AWSS3': 'AWS S3',
            'DROPBOX': 'Dropbox',
            'AZURE': 'Azure',
            'ONEDRIVE': 'OneDrive'
        };
        return labels[storageType] || storageType || '';
    };

    const generatePDFContent = () => {
        const computerName = restoreData[0]?.from_computer || 'Unknown';
        const currentDate = new Date().toLocaleString();

        const styles = {
            // Header styles with professional color scheme
            header: {
                fontSize: 24,
                bold: true,
                alignment: 'center',
                color: '#1a365d', // Dark blue
                margin: [0, 5, 0, 5]
            },
            title: {
                fontSize: 15,
                bold: true,
                alignment: 'center',
                color: '#2d3748', // Dark gray
                margin: [0, 65, 80, 0]
            },
            date: {
                fontSize: 11,
                alignment: 'center',
                italics: true,
                color: '#718096', // Medium gray
                margin: [20, 0, 0, 5]
            },

            // Summary section
            summaryTitle: {
                fontSize: 16,
                bold: true,
                color: '#1a365d',
                margin: [0, 0, 0, 10],
                decoration: 'underline',
                decorationColor: '#4299e1'
            },
            summaryText: {
                fontSize: 11,
                color: '#4a5568',
                margin: [0, 5, 0, 5]
            },

            // Section dividers
            sectionBreak: {
                fontSize: 1,
                color: '#e2e8f0',
                margin: [0, 20, 0, 20]
            },

            // Job section styles with professional blue theme
            jobSectionTitle: {
                fontSize: 14,
                bold: true,
                color: '#1a365d',
                margin: [0, 25, 0, 12],
                decoration: 'underline',
                decorationColor: '#4299e1'
            },

            // Level 1: Job Information (Professional Blue Theme)
            jobHeader: {
                fontSize: 10,
                bold: true,
                color: '#ffffff',
                fillColor: '#2b6cb0', // Professional blue
                margin: [8, 8, 8, 8],
                alignment: 'center'
            },
            jobCell: {
                fontSize: 9,
                color: '#2d3748',
                fillColor: '#ebf8ff', // Light blue
                margin: [6, 6, 6, 6]
            },

            // Level 2: Backup/Restore Information (Professional Teal Theme)
            backupSectionTitle: {
                fontSize: 12,
                bold: true,
                color: '#1a365d',
                margin: [15, 18, 0, 10]
            },
            backupHeader: {
                fontSize: 10,
                bold: true,
                color: '#ffffff',
                fillColor: '#2c7a7b', // Professional teal
                margin: [6, 6, 6, 6],
                alignment: 'center'
            },
            backupCell: {
                fontSize: 9,
                color: '#2d3748',
                fillColor: '#e6fffa', // Light teal
                margin: [5, 5, 5, 5]
            },

            // Level 3: File Details (Professional Gray Theme)
            fileSectionTitle: {
                fontSize: 11,
                bold: true,
                color: '#1a365d',
                margin: [30, 15, 0, 8]
            },
            fileHeader: {
                fontSize: 9,
                bold: true,
                color: '#ffffff',
                fillColor: '#4a5568', // Professional gray
                margin: [4, 4, 4, 4],
                alignment: 'center'
            },
            fileCell: {
                fontSize: 8,
                color: '#2d3748',
                fillColor: '#f7fafc', // Very light gray
                margin: [3, 3, 3, 3]
            },

            // Fixed status styles - Green for success, Red for errors
            statusSuccess: {
                fontSize: 8,
                color: '#22543d', // Dark green text
                fillColor: '#c6f6d5', // Light green background
                margin: [3, 3, 3, 3],
                bold: true
            },
            statusError: {
                fontSize: 8,
                color: '#c53030', // Dark red text
                fillColor: '#fed7d7', // Light red background
                margin: [3, 3, 3, 3],
                bold: true
            },
            statusWarning: {
                fontSize: 8,
                color: '#d69e2e', // Dark yellow text
                fillColor: '#fef5e7', // Light yellow background
                margin: [3, 3, 3, 3],
                bold: true
            }
        };

        const docDefinition = {
            content: [
                // Header section with logo placeholder and better styling
                {
                    columns: [
                        {
                            // Logo placeholder - replace with actual logo
                            image: 'data:image/png;base64,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',
                            width: 120,
                            height: 60,
                            margin: [250, 0, 0, 0]
                        },
                        {
                            stack: [
                                {
                                    text: `Restore Report - ${computerName}`,
                                    style: 'title'
                                }
                            ],
                            width: '*'
                        }
                    ],
                    margin: [0, 0, 0, 10]
                },
                {
                    text: `Generated: ${currentDate}`,
                    style: 'date'
                },
            ],
            styles,
            pageSize: 'A4',
            pageOrientation: 'portrait',
            pageMargins: [5, 5, 5, 5], // Professional margins

            // Professional header and footer
            footer: function (currentPage, pageCount) {
                return {
                    table: {
                        widths: ['*', 'auto', '*'],
                        body: [[
                            { text: '', border: [false, false, false, false] },
                            {
                                text: `Page ${currentPage} of ${pageCount}`,
                                alignment: 'center',
                                fontSize: 9,
                                color: '#718096',
                                border: [false, false, false, false]
                            },
                            { text: '', border: [false, false, false, false] }
                        ]]
                    },
                    layout: 'noBorders',
                    margin: [40, 0, 40, 20]
                };
            }
        };

        restoreData.forEach((job, jobIndex) => {
            // Add job section title

            // Level 1: Job Information Table with professional styling
            const jobTable = {
                table: {
                    widths: ['15%', '15%', '20%', '20%', '15%', '15%'],
                    body: [
                        // Job Header Row
                        [
                            { text: 'Repository', style: 'jobHeader' },
                            { text: 'Type', style: 'jobHeader' },
                            { text: 'Job Name', style: 'jobHeader' },
                            { text: 'Location', style: 'jobHeader' },
                            { text: 'Start Time', style: 'jobHeader' },
                            { text: 'Accuracy', style: 'jobHeader' }
                        ],
                        // Job Data Row
                        [
                            { text: getStorageLabel(job.data_repo), style: 'jobCell' },
                            { text: job.type || 'file', style: 'jobCell' },
                            { text: job.name || 'N/A', style: 'jobCell' },
                            { text: job.location || 'N/A', style: 'jobCell' },
                            { text: job.last_modified || 'N/A', style: 'jobCell' },
                            { text: `${job.wdone || 0}%`, style: 'jobCell' }
                        ]
                    ]
                },
                layout: {
                    borderWidth: 1,
                    borderColor: '#cbd5e0',
                    paddingLeft: function (i, node) { return 8; },
                    paddingRight: function (i, node) { return 8; },
                    paddingTop: function (i, node) { return 6; },
                    paddingBottom: function (i, node) { return 6; }
                },
                margin: [0, 0, 0, 15]
            };

            docDefinition.content.push(jobTable);

            // Level 2: Process restore logs
            if (job.restore_logs && job.restore_logs.length > 0) {
                job.restore_logs.forEach((restoreLog, restoreIndex) => {
                    const backupRestoreTable = {
                        table: {
                            widths: ['13%', '18%', '18%', '18%', '15%', '18%'],
                            body: [
                                // Backup/Restore Header Row
                                [
                                    { text: 'Repository', style: 'backupHeader' },
                                    { text: 'Job Name', style: 'backupHeader' },
                                    { text: 'Backup Endpoint', style: 'backupHeader' },
                                    { text: 'Backup Location', style: 'backupHeader' },
                                    { text: 'Restore Endpoint', style: 'backupHeader' },
                                    { text: 'Restore Location', style: 'backupHeader' }
                                ],
                                // Backup/Restore Data Row
                                [
                                    { text: getStorageLabel(restoreLog.storage_type), style: 'backupCell' },
                                    { text: restoreLog.backup_name || 'N/A', style: 'backupCell' },
                                    { text: restoreLog.from_backup_pc || 'N/A', style: 'backupCell' },
                                    { text: restoreLog.targetlocation || 'N/A', style: 'backupCell' },
                                    { text: restoreLog.torestore_pc || 'N/A', style: 'backupCell' },
                                    { text: restoreLog.RestoreLocation || 'N/A', style: 'backupCell' }
                                ]
                            ]
                        },
                        layout: {
                            borderWidth: 1,
                            borderColor: '#81e6d9',
                            paddingLeft: function (i, node) { return 6; },
                            paddingRight: function (i, node) { return 6; },
                            paddingTop: function (i, node) { return 5; },
                            paddingBottom: function (i, node) { return 5; }
                        },
                        margin: [15, 0, 0, 12]
                    };

                    docDefinition.content.push(backupRestoreTable);

                    // Level 3: File Details
                    if (restoreLog.restore_files && restoreLog.restore_files.length > 0) {
                        const includeReason = restoreLog.restore_files.some(file => file.reason);
                        const fileDetailsBody = [
                            // File Details Header
                            [
                                { text: 'File Name', style: 'fileHeader' },
                                { text: 'Start Time', style: 'fileHeader' },
                                { text: 'End Time', style: 'fileHeader' },
                                { text: 'Duration', style: 'fileHeader' },
                                ...(includeReason ? [{ text: 'Reason', style: 'fileHeader' }] : []),
                                { text: 'Status', style: 'fileHeader' }
                            ]
                        ];

                        // Remove duplicates and add file data
                        const uniqueFiles = restoreLog.restore_files.filter((file, index, self) =>
                            index === self.findIndex(f =>
                                f.backup_name === file.backup_name &&
                                f.file === file.file &&
                                f.file_start === file.file_start
                            )
                        );

                        uniqueFiles.forEach((file) => {
                            // Fixed status determination
                            let statusStyle = 'statusWarning'; // default
                            const status = file.restore?.toLowerCase() || '';

                            if (status === 'success' || status === 'completed') {
                                statusStyle = 'statusSuccess';
                            } else if (status === 'failed' || status === 'error' || status.includes('fail')) {
                                statusStyle = 'statusError';
                            }

                            fileDetailsBody.push([
                                { text: file.file || 'Unknown file', style: 'fileCell' },
                                { text: file.file_start || '-', style: 'fileCell' },
                                { text: file.file_end || '-', style: 'fileCell' },
                                { text: file.file_restore_time + 's' || '-', style: 'fileCell' },
                                ...(includeReason ? [{ text: file.reason || '-', style: 'fileCell' }] : []),
                                { text: file.restore || 'Unknown', style: statusStyle }
                            ]);
                        });

                        const fileTable = {
                            table: {
                                widths: ['25%', '15%', '15%', '15%', '15%', '15%'],
                                body: fileDetailsBody
                            },
                            layout: {
                                borderWidth: 1,
                                borderColor: '#a0aec0',
                                paddingLeft: function (i, node) { return 4; },
                                paddingRight: function (i, node) { return 4; },
                                paddingTop: function (i, node) { return 4; },
                                paddingBottom: function (i, node) { return 4; }
                            },
                            margin: [30, 0, 0, 20]
                        };

                        docDefinition.content.push(fileTable);
                    }
                });
            }

            // Add section divider between jobs (except for last job)
            if (jobIndex < restoreData.length - 1) {
                docDefinition.content.push({
                    table: {
                        widths: ['*'],
                        body: [[{
                            text: '',
                            fillColor: '#e2e8f0',
                            margin: [0, 0, 0, 0]
                        }]]
                    },
                    layout: 'noBorders',
                    margin: [0, 25, 0, 0]
                });

                // Page break for new job
                docDefinition.content.push({ text: '', pageBreak: 'before' });
            }
        });

        return docDefinition;
    };

    const handleDownloadPDF = async () => {
        try {
            if (!restoreData || restoreData.length === 0) {
                setAlert({
                    message: "No data available to generate PDF report.",
                    type: 'error'
                });
                return;
            }

            const docDefinition = generatePDFContent();

            const computerName = restoreData[0]?.from_computer || 'Unknown';
            const dateString = new Date().toISOString().split('T')[0];
            const filename = `restore-report-${computerName}-${dateString}.pdf`;

            // Create and download PDF
            pdfMake.createPdf(docDefinition).download(filename);

            // Log the download event
            const downloadEvent = `Restore Report PDF Download for ${computerName}`;
            if (handleLogsSubmit) {
                handleLogsSubmit(downloadEvent);
            }

        } catch (error) {
            console.error('Error generating PDF report:', error);
            setAlert({
                message: "Error generating report. Please try again.",
                type: 'error'
            });
        }
    };


    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();

        // Check if restoreData is empty or undefined
        if (!restoreData || restoreData.length === 0) {
            return;
        }

        // Group the jobs by 'data_repo'
        const groupedByRepo = restoreData.reduce((acc, job) => {
            if (!acc[job.data_repo]) {
                acc[job.data_repo] = [];
            }
            acc[job.data_repo].push(job);
            return acc;
        }, {});

        // Group the jobs by 'from_computer'
        const groupedByComputer = restoreData.reduce((acc, job) => {
            if (!acc[job.from_computer]) {
                acc[job.from_computer] = [];
            }
            acc[job.from_computer].push(job);
            return acc;
        }, {});

        const computerName = Object.keys(groupedByComputer)[0]; // Get the first computer name
        const currentDate = new Date().toLocaleString();

        // Helper function to check if job has restore or file details
        const hasRestoreOrFileDetails = (job) => {
            return job.restore_logs && job.restore_logs.length > 0 &&
                job.restore_logs.some(log =>
                    (log.restore_files && log.restore_files.length > 0) ||
                    log.backup_name || log.from_backup_pc || log.targetlocation
                );
        };

        // Create a flat array of jobs in original order with their repo keys
        const allJobsInOrder = [];
        Object.keys(groupedByRepo).forEach((repoKey) => {
            groupedByRepo[repoKey].forEach((job) => {
                allJobsInOrder.push({ job, repoKey, hasDetails: hasRestoreOrFileDetails(job) });
            });
        });

        // Helper function to get storage type label
        const getStorageTypeLabel = (repoKey) => {
            const storageConfigs = {
                "LAN": "On-Premise",
                "GDRIVE": "Google Drive",
                "UNC": "LAN/NAS",
                "AWSS3": "AWS S3",
                "DROPBOX": "Dropbox",
                "AZURE": "Azure",
                "ONEDRIVE": "OneDrive"
            };
            return storageConfigs[repoKey] || repoKey;
        };

        // Start building the Excel data
        const wsData = [];
        let currentRow = 0;

        // Add header section
        wsData[currentRow++] = [`Restore Report of ${computerName}`];
        wsData[currentRow++] = [`Generated As On: ${currentDate}`];
        wsData[currentRow++] = ['']; // Empty row for spacing

        // Track merge ranges and styles
        const merges = [];
        const styles = {};

        // Header styling
        styles['A1'] = {
            font: { bold: true, sz: 14, color: { rgb: "FF000000" } },
            alignment: { horizontal: "center", vertical: "center", wrapText: true },
            fill: { fgColor: { rgb: "FFE6F3FF" } },
            border: {
                top: { style: "medium", color: { rgb: "FF000000" } },
                bottom: { style: "medium", color: { rgb: "FF000000" } },
                left: { style: "medium", color: { rgb: "FF000000" } },
                right: { style: "medium", color: { rgb: "FF000000" } }
            }
        };

        // Date styling
        styles['A2'] = {
            font: { sz: 11, color: { rgb: "FF000000" } },
            alignment: { horizontal: "center", vertical: "center", wrapText: true },
            border: {
                top: { style: "thin", color: { rgb: "FF000000" } },
                bottom: { style: "thin", color: { rgb: "FF000000" } },
                left: { style: "medium", color: { rgb: "FF000000" } },
                right: { style: "medium", color: { rgb: "FF000000" } }
            }
        };

        // Add merge for header - spanning across all columns
        merges.push({ s: { c: 0, r: 0 }, e: { c: 6, r: 0 } });
        merges.push({ s: { c: 0, r: 1 }, e: { c: 6, r: 1 } });

        let hasAddedNormalHeader = false;

        // Process each job
        allJobsInOrder.forEach((jobData, index) => {
            const { job, repoKey, hasDetails } = jobData;

            if (!hasDetails) {
                // Normal job without details
                if (!hasAddedNormalHeader) {
                    // Add main table header
                    wsData[currentRow] = [
                        "Storage Type", "Job Name", "Start Time", "Type", "Location", "Progress"
                    ];

                    // Style the header row
                    for (let col = 0; col < 6; col++) {
                        const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                        styles[cellRef] = {
                            font: { bold: true, sz: 11, color: { rgb: "FFFFFFFF" } },
                            fill: { fgColor: { rgb: "FF4472C4" } },
                            alignment: { horizontal: "center", vertical: "center", wrapText: true },
                            border: {
                                top: { style: "medium", color: { rgb: "FF000000" } },
                                bottom: { style: "medium", color: { rgb: "FF000000" } },
                                left: { style: "medium", color: { rgb: "FF000000" } },
                                right: { style: "medium", color: { rgb: "FF000000" } }
                            }
                        };
                    }
                    currentRow++;
                    hasAddedNormalHeader = true;
                }

                // Add job data row
                wsData[currentRow] = [
                    getStorageTypeLabel(repoKey),
                    job.name,
                    job.last_modified,
                    job.type,
                    job.location,
                    `${job.wdone}%`
                ];

                // Style the data row
                for (let col = 0; col < 6; col++) {
                    const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                    styles[cellRef] = {
                        font: { sz: 10, color: { rgb: "FF000000" } },
                        alignment: { horizontal: "center", vertical: "center", wrapText: true },
                        border: {
                            top: { style: "thin", color: { rgb: "FF000000" } },
                            bottom: { style: "thin", color: { rgb: "FF000000" } },
                            left: { style: "medium", color: { rgb: "FF000000" } },
                            right: { style: "medium", color: { rgb: "FF000000" } }
                        }
                    };
                }
                currentRow++;

            } else {
                // Job with detailed restore information
                currentRow++; // Add spacing

                // Add main job header
                wsData[currentRow] = [
                    "Storage Type", "Job Name", "Start Time", "Type", "Location", "Progress"
                ];

                // Style the header row
                for (let col = 0; col < 6; col++) {
                    const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                    styles[cellRef] = {
                        font: { bold: true, sz: 11, color: { rgb: "FFFFFFFF" } },
                        fill: { fgColor: { rgb: "FF4472C4" } },
                        alignment: { horizontal: "center", vertical: "center", wrapText: true },
                        border: {
                            top: { style: "medium", color: { rgb: "FF000000" } },
                            bottom: { style: "medium", color: { rgb: "FF000000" } },
                            left: { style: "medium", color: { rgb: "FF000000" } },
                            right: { style: "medium", color: { rgb: "FF000000" } }
                        }
                    };
                }
                currentRow++;

                // Add main job data
                wsData[currentRow] = [
                    getStorageTypeLabel(repoKey),
                    job.name,
                    job.last_modified,
                    job.type,
                    job.location,
                    `${job.wdone}%`
                ];

                // Style the main job data row
                for (let col = 0; col < 6; col++) {
                    const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                    styles[cellRef] = {
                        font: { sz: 10, color: { rgb: "FF000000" } },
                        alignment: { horizontal: "center", vertical: "center", wrapText: true },
                        border: {
                            top: { style: "thin", color: { rgb: "FF000000" } },
                            bottom: { style: "medium", color: { rgb: "FF000000" } },
                            left: { style: "medium", color: { rgb: "FF000000" } },
                            right: { style: "medium", color: { rgb: "FF000000" } }
                        }
                    };
                }
                currentRow++;

                // Add restore details if they exist
                if (job.restore_logs && job.restore_logs.length > 0) {
                    currentRow++; // Spacing

                    // Restore Details section title
                    wsData[currentRow] = ["Restore Details"];
                    styles[XLSX.utils.encode_cell({ r: currentRow, c: 0 })] = {
                        font: { bold: true, sz: 12, color: { rgb: "FF000000" } },
                        fill: { fgColor: { rgb: "FFF2F2F2" } },
                        alignment: { horizontal: "center", vertical: "center", wrapText: true },
                        border: {
                            top: { style: "medium", color: { rgb: "FF000000" } },
                            bottom: { style: "medium", color: { rgb: "FF000000" } },
                            left: { style: "medium", color: { rgb: "FF000000" } },
                            right: { style: "medium", color: { rgb: "FF000000" } }
                        }
                    };
                    merges.push({ s: { c: 0, r: currentRow }, e: { c: 5, r: currentRow } });
                    currentRow++;

                    // Restore details header
                    wsData[currentRow] = [
                        "Destination", "Job Name", "Backup Endpoint", "Backup Location", "Restore Endpoint", "Restore Location"
                    ];

                    // Style restore details header
                    for (let col = 0; col < 6; col++) {
                        const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                        styles[cellRef] = {
                            font: { bold: true, sz: 10, color: { rgb: "FF000000" } },
                            fill: { fgColor: { rgb: "FFFFFF00" } },
                            alignment: { horizontal: "center", vertical: "center", wrapText: true },
                            border: {
                                top: { style: "medium", color: { rgb: "FF000000" } },
                                bottom: { style: "medium", color: { rgb: "FF000000" } },
                                left: { style: "medium", color: { rgb: "FF000000" } },
                                right: { style: "medium", color: { rgb: "FF000000" } }
                            }
                        };
                    }
                    currentRow++;

                    // Add restore log data
                    job.restore_logs.forEach((restoreLog) => {
                        wsData[currentRow] = [
                            getStorageTypeLabel(restoreLog.storage_type),
                            restoreLog.backup_name,
                            restoreLog.from_backup_pc,
                            restoreLog.targetlocation,
                            restoreLog.torestore_pc,
                            restoreLog.RestoreLocation,
                        ];

                        // Style restore log data
                        for (let col = 0; col < 6; col++) {
                            const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                            styles[cellRef] = {
                                font: { sz: 10, color: { rgb: "FF000000" } },
                                alignment: { horizontal: "center", vertical: "center", wrapText: true },
                                border: {
                                    top: { style: "thin", color: { rgb: "FF000000" } },
                                    bottom: { style: "thin", color: { rgb: "FF000000" } },
                                    left: { style: "medium", color: { rgb: "FF000000" } },
                                    right: { style: "medium", color: { rgb: "FF000000" } }
                                }
                            };
                        }
                        currentRow++;

                        // Add file details if they exist
                        if (restoreLog.restore_files && restoreLog.restore_files.length > 0) {
                            currentRow++; // Spacing

                            // File Details section title
                            wsData[currentRow] = ["File Details"];
                            styles[XLSX.utils.encode_cell({ r: currentRow, c: 0 })] = {
                                font: { bold: true, sz: 11, color: { rgb: "FF000000" } },
                                fill: { fgColor: { rgb: "FFF2F2F2" } },
                                alignment: { horizontal: "center", vertical: "center", wrapText: true },
                                border: {
                                    top: { style: "medium", color: { rgb: "FF000000" } },
                                    bottom: { style: "medium", color: { rgb: "FF000000" } },
                                    left: { style: "medium", color: { rgb: "FF000000" } },
                                    right: { style: "medium", color: { rgb: "FF000000" } }
                                }
                            };
                            merges.push({ s: { c: 0, r: currentRow }, e: { c: 6, r: currentRow } });
                            currentRow++;

                            // File details header
                            const hasReasonColumn = restoreLog.restore_files.some(file => file.reason);
                            const fileHeaders = ["Job Name", "File Name", "Start Time", "End Time", "Duration", "Status"];
                            if (hasReasonColumn) {
                                fileHeaders.push("Reason");
                            }
                            wsData[currentRow] = fileHeaders;

                            // Style file details header
                            for (let col = 0; col < fileHeaders.length; col++) {
                                const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                                styles[cellRef] = {
                                    font: { bold: true, sz: 10, color: { rgb: "FFFFFFFF" } },
                                    fill: { fgColor: { rgb: "FF548235" } },
                                    alignment: { horizontal: "center", vertical: "center", wrapText: true },
                                    border: {
                                        top: { style: "medium", color: { rgb: "FF000000" } },
                                        bottom: { style: "medium", color: { rgb: "FF000000" } },
                                        left: { style: "medium", color: { rgb: "FF000000" } },
                                        right: { style: "medium", color: { rgb: "FF000000" } }
                                    }
                                };
                            }
                            currentRow++;

                            // Filter and add unique file details
                            const uniqueFiles = restoreLog.restore_files.filter((file, index, self) =>
                                index === self.findIndex(f =>
                                    f.backup_name === file.backup_name &&
                                    f.file === file.file &&
                                    f.file_start === file.file_start &&
                                    f.file_end === file.file_end &&
                                    f.file_restore_time === file.file_restore_time &&
                                    f.reason === file.reason &&
                                    f.restore === file.restore
                                )
                            );

                            uniqueFiles.forEach((restoreFile) => {
                                const fileRow = [
                                    restoreFile.backup_name,
                                    restoreFile.file,
                                    restoreFile.file_start,
                                    restoreFile.file_end,
                                    restoreFile.file_restore_time,
                                    restoreFile.restore
                                ];

                                if (hasReasonColumn) {
                                    fileRow.push(
                                        restoreFile.restore && restoreFile.restore.toLowerCase() === 'failed' && restoreFile.reason
                                            ? restoreFile.reason
                                            : '-'
                                    );
                                }

                                wsData[currentRow] = fileRow;

                                // Style file data rows
                                for (let col = 0; col < fileRow.length; col++) {
                                    const cellRef = XLSX.utils.encode_cell({ r: currentRow, c: col });
                                    let cellStyle = {
                                        font: { sz: 10, color: { rgb: "FF000000" } },
                                        alignment: { horizontal: "center", vertical: "center", wrapText: true },
                                        border: {
                                            top: { style: "thin", color: { rgb: "FF000000" } },
                                            bottom: { style: "thin", color: { rgb: "FF000000" } },
                                            left: { style: "medium", color: { rgb: "FF000000" } },
                                            right: { style: "medium", color: { rgb: "FF000000" } }
                                        }
                                    };

                                    // Special styling for status column
                                    if (col === 5) { // Status column
                                        if (restoreFile.restore && restoreFile.restore.toLowerCase() === 'success') {
                                            cellStyle.font = { bold: true, sz: 10, color: { rgb: "FF008000" } };
                                            cellStyle.fill = { fgColor: { rgb: "FFE6FFE6" } };
                                        } else if (restoreFile.restore && restoreFile.restore.toLowerCase() === 'failed') {
                                            cellStyle.font = { bold: true, sz: 10, color: { rgb: "FFFF0000" } };
                                            cellStyle.fill = { fgColor: { rgb: "FFFFE6E6" } };
                                        }
                                    }

                                    // Special styling for reason column if it has error info
                                    if (hasReasonColumn && col === 6 && restoreFile.restore && restoreFile.restore.toLowerCase() === 'failed') {
                                        cellStyle.font = { sz: 9, color: { rgb: "FFCC0000" } };
                                        cellStyle.fill = { fgColor: { rgb: "FFFFF0F0" } };
                                    }

                                    styles[cellRef] = cellStyle;
                                }
                                currentRow++;
                            });
                        }
                    });
                }
                currentRow++; // Add spacing after detailed job
            }
        });

        // Create the worksheet
        const ws = XLSX.utils.aoa_to_sheet(wsData);

        // Set column widths
        ws["!cols"] = [
            { wpx: 110 },
            { wpx: 140 },
            { wpx: 130 },
            { wpx: 110 },
            { wpx: 180 },
            { wpx: 100 },
            { wpx: 150 }
        ];

        // Apply merges
        ws["!merges"] = merges;

        // Apply styles to all cells
        Object.keys(styles).forEach(cellRef => {
            if (!ws[cellRef]) ws[cellRef] = { v: '', t: 's' };
            ws[cellRef].s = styles[cellRef];
        });

        // Apply default styling to cells that don't have custom styles
        const range = XLSX.utils.decode_range(ws['!ref']);
        for (let R = range.s.r; R <= range.e.r; ++R) {
            for (let C = range.s.c; C <= range.e.c; ++C) {
                const cellRef = XLSX.utils.encode_cell({ r: R, c: C });
                if (!ws[cellRef]) ws[cellRef] = { v: '', t: 's' };

                // If cell doesn't have existing style, apply default
                if (!ws[cellRef].s) {
                    ws[cellRef].s = {
                        font: { sz: 10, color: { rgb: "FF000000" } },
                        alignment: {
                            horizontal: "center",
                            vertical: "center",
                            wrapText: true
                        },
                        border: {
                            top: { style: "thin", color: { rgb: "FF000000" } },
                            bottom: { style: "thin", color: { rgb: "FF000000" } },
                            left: { style: "medium", color: { rgb: "FF000000" } },
                            right: { style: "medium", color: { rgb: "FF000000" } }
                        }
                    };
                } else {
                    // Ensure existing styles have word wrap
                    if (!ws[cellRef].s.alignment) {
                        ws[cellRef].s.alignment = {};
                    }
                    ws[cellRef].s.alignment.wrapText = true;
                    ws[cellRef].s.alignment.horizontal = ws[cellRef].s.alignment.horizontal || "center";
                    ws[cellRef].s.alignment.vertical = ws[cellRef].s.alignment.vertical || "center";
                }
            }
        }

        // Set row heights for better visibility
        ws["!rows"] = [];
        for (let i = 0; i < currentRow; i++) {
            if (i === 0) {
                ws["!rows"][i] = { hpt: 25 };
            } else if (i === 1) {
                ws["!rows"][i] = { hpt: 20 };
            } else {
                ws["!rows"][i] = { hpt: 22 };
            }
        }

        // Append the worksheet to the workbook
        XLSX.utils.book_append_sheet(wb, ws, "Restore_Report");

        // Generate and trigger download
        const wbout = XLSX.write(wb, {
            bookType: "xlsx",
            type: "binary",
            cellStyles: true,
            bookSST: false
        });

        // Helper function to convert string to array buffer
        function s2ab(s) {
            const buf = new ArrayBuffer(s.length);
            const view = new Uint8Array(buf);
            for (let i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
            return buf;
        }

        const blob = new Blob([s2ab(wbout)], {
            type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Restore_Report_${computerName}.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = `Backuplogs Report of ${computerName} Excel Download`;
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleEndpoint = () => {
        setShowRestoreReportEndPoint(null);
        setShowBackuplog(false);
        setAgentName(null)
        setFilters({ name: "", repo: "", status: "", fromDate: "", toDate: "" });
        setShowFilterPopup(false);
        setShowSelectEndpointCode(true);
        setTimeout(() => {
            setShowBackuplog(true); // Set it true for BackupLog mode
            setShowSelectEndpointCode(true);
        }, 0);
    }

    const conversionInMinutes = (seconds) => {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hrs > 0) {
            return `${hrs}h ${mins}min ${secs}sec`;
        } else if (mins > 0) {
            return `${mins}min ${secs}sec`;
        } else {
            return `${secs}sec`;
        }
    };

    return (
        <>
            <div className="tableHt overflow-y-auto">
                <div className="flex justify-between items-center sticky top-0 z-10 bg-white">
                    <span className="bg-yellow-200 text-black-100 px-2 py-1 rounded-lg text-sm ml-1">
                        🖥️ {showRestoreReportEndPoint}
                    </span>
                    <div className="flex items-center space-x-2">
                        <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                        <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />

                        <button title="Refresh" className="p-2 rounded hover:bg-gray-200 transition" onClick={() => fetchRestoreData(showRestoreReportEndPoint)}>
                            <RefreshCw size={20} />
                        </button>

                        <button onClick={() => setShowFilterPopup(true)} className="bg-gray-200 px-3 py-1 rounded text-sm">
                            Filter
                        </button>
                        <button
                            onClick={handleEndpoint}
                            className="text-white bg-blue-600 px-3 py-1 rounded text-sm"
                        >
                            Change Endpoint
                        </button>
                    </div>
                </div>

                <table className="w-full bg-white border-collapse shadow-2xl rounded-lg">
                    <thead className="bg-blue-600 text-white sticky top-9 z-10">
                        <tr>
                            <th className="text-left text-sm font-semibold  tracking-wider border-b border-gray-600">
                                <span className="flex items-center ">
                                    <span className=""></span>
                                    <span>+ -</span>
                                </span>
                            </th>
                            <th className="w-1 text-left text-sm font-semibold  border-b border-gray-600">
                                Repository
                            </th>
                            <th className="px-2 py-2 text-left text-sm font-semibold  tracking-wider border-b border-gray-600">
                                <span className="flex items-center space-x-2">
                                    <FolderOpen className="w-4 h-4" />
                                    <span>Type</span>
                                </span>
                            </th>
                            <th className="px-2 py-2 text-left text-sm font-semibold  tracking-wider border-b border-gray-600">
                                Job Name
                            </th>
                            <th className="px-2 py-2 text-left text-sm font-semibold  tracking-wider border-b border-gray-600">
                                Location
                            </th>
                            <th className="px-2 py-2 text-left text-sm font-semibold  tracking-wider border-b border-gray-600">
                                <span className="flex items-center space-x-2">
                                    <Clock className="w-4 h-4" />
                                    <span>Start Time</span>
                                </span>
                            </th>
                            <th className="px-6 py-4 text-left text-sm font-semibold  tracking-wider border-b border-gray-600">
                                <span className="flex items-center space-x-2">
                                    <CheckCircle className="w-4 h-4" />
                                    <span>Accuracy</span>
                                </span>
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white">
                        {filteredData.length === 0 ? (
                            <tr>
                                <td colSpan="7" className="px-6 py-12 text-center h-full">
                                    <div className="flex flex-col items-center space-y-3">
                                        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                                            <FolderOpen className="w-8 h-8 text-gray-400" />
                                        </div>
                                        <div className="text-gray-500">
                                            <p className="text-lg font-medium">No data available</p>
                                            <p className="text-sm text-gray-400 mt-1">There are no restore jobs to display at the moment.</p>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        ) : filteredData.map((item, index) => (
                            <React.Fragment key={item.id}>
                                {/* Main Row */}
                                <tr className={`border-b border-gray-200 hover:bg-blue-50 transition-colors duration-200 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                                    <td className="whitespace-nowrap">
                                        <span className="flex items-center">
                                            {item.restore_logs?.length > 0 && (
                                                <button
                                                    onClick={() => toggleMainRow(item.id)}
                                                    className="rounded-full hover:bg-gray-200 transition-colors"
                                                >
                                                    {expandedMain[item.id] ? (
                                                        <ChevronDown className="text-gray-600" />
                                                    ) : (
                                                        <ChevronRight className="text-gray-600" />
                                                    )}
                                                </button>
                                            )}
                                        </span>
                                    </td>
                                    <td className="whitespace-whitespace-normal" style={{ maxWidth: '12rem' }}>
                                        <RepoIcon repo={item.data_repo} />
                                    </td>
                                    <td className="px-2 py-2 whitespace-nowrap">
                                        <span className="flex items-center space-x-2">
                                            <FolderOpen className="w-4 h-4 text-yellow-500" />
                                            <span className="text-sm text-gray-600 capitalize">{item.type}</span>
                                        </span>
                                    </td>
                                    <td className="px-2 py-2 text-sm text-gray-900 break-words whitespace-normal" style={{ maxWidth: '12rem' }}>{item.name}</td>
                                    <td className="px-2 py-2 text-sm text-gray-600 break-words whitespace-normal" style={{ maxWidth: '12rem' }} title={item.location}>
                                        {item.location}
                                    </td>
                                    <td className="px-2 py-2 whitespace-nowrap text-sm text-gray-600">{item.last_modified}</td>
                                    <td className="px-2 py-2 whitespace-nowrap">
                                        <div className="flex items-center gap-3">
                                            <div className="flex-1 bg-gray-100 rounded-full h-4">
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
                                </tr>

                                {/* Restore Logs Level */}
                                {expandedMain[item.id] && item.restore_logs.map((log) => (
                                    <tr key={`log-${log.id}`} className="bg-yellow-50">
                                        <td colSpan="7" className="px-4 py-1">
                                            <table className="w-full border-l-4 border-yellow-300 rounded-r-lg overflow-hidden shadow-sm">
                                                <thead className="bg-yellow-400 text-white">
                                                    <tr>
                                                        <th className="text-left text-sm font-semibold">
                                                            + -
                                                        </th>
                                                        <th className="w-1 text-left text-sm font-semibold">
                                                            Repository
                                                        </th>
                                                        <th className="px-2 py-2 text-left text-sm font-semibold">Job Name</th>
                                                        <th className="px-2 py-2 text-left text-sm font-semibold">
                                                            <span className="flex items-center space-x-2">
                                                                <Monitor className="w-4 h-4" />
                                                                <span>Backup Endpoint</span>
                                                            </span>
                                                        </th>
                                                        <th className="px-2 py-2 text-left text-sm font-semibold">Backup Location</th>
                                                        <th className="px-2 py-2 text-left text-sm font-semibold">
                                                            <span className="flex items-center space-x-2">
                                                                <Monitor className="w-4 h-4" />
                                                                <span>Restore Endpoint</span>
                                                            </span>
                                                        </th>
                                                        <th className="px-2 py-2 text-left text-sm font-semibold">Restore Location</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="bg-white">
                                                    <tr className="border-b border-yellow-200">
                                                        <td className="">
                                                            <span className="flex items-center space-x-3">
                                                                {log.restore_files?.length > 0 && (
                                                                    <button
                                                                        onClick={() => toggleLogRow(log.id)}
                                                                        className="p-1 rounded-full hover:bg-yellow-200 transition-colors"
                                                                    >
                                                                        {expandedLogs[log.id] ? (
                                                                            <ChevronDown className="w-4 h-4 text-yellow-600" />
                                                                        ) : (
                                                                            <ChevronRight className="w-4 h-4 text-yellow-600" />
                                                                        )}
                                                                    </button>
                                                                )}
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <RepoIcon repo={item.data_repo} />
                                                        </td>
                                                        <td className="px-2 py-2 text-sm text-gray-900 break-words whitespace-normal" style={{ maxWidth: '12rem' }}>{log.backup_name}</td>
                                                        <td className="px-2 py-2 text-sm text-gray-600 break-words whitespace-normal" style={{ maxWidth: '12rem' }}>{log.from_backup_pc}</td>
                                                        <td className="px-2 py-2 text-sm text-gray-600 break-words whitespace-normal" style={{ maxWidth: '12rem' }} title={log.targetlocation}>
                                                            {log.targetlocation}
                                                        </td>
                                                        <td className="px-2 py-2 text-sm text-gray-600">{log.torestore_pc}</td>
                                                        <td className="px-2 py-2 text-sm text-gray-600 break-words whitespace-normal" style={{ maxWidth: '12rem' }} title={log.RestoreLocation}>
                                                            {log.RestoreLocation}
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>

                                            {/* Restore Files Level */}
                                            {expandedLogs[log.id] && (
                                                <table className="w-full mt-4 rounded-lg border border-gray-200 overflow-hidden">
                                                    <thead className="bg-gray-100">
                                                        <tr>
                                                            <th className="px-2 py-2 text-left text-xs font-semibold text-gray-700  tracking-wider">
                                                                Job Name
                                                            </th>
                                                            <th className="px-2 py-2 text-left text-xs font-semibold text-gray-700  tracking-wider">
                                                                File Name
                                                            </th>
                                                            <th className="px-2 py-2 text-left text-xs font-semibold text-gray-700  tracking-wider">
                                                                Start Time
                                                            </th>
                                                            <th className="px-2 py-2 text-left text-xs font-semibold text-gray-700  tracking-wider">
                                                                End Time
                                                            </th>
                                                            <th className="px-2 py-2 text-left text-xs font-semibold text-gray-700  tracking-wider">
                                                                Duration
                                                            </th>
                                                            {log.restore_files?.some(file => file.reason) &&
                                                                <th className="px-2 py-2 text-left text-xs font-semibold text-gray-700  tracking-wider">
                                                                    Reason
                                                                </th>
                                                            }
                                                            <th className="px-2 py-2 text-left text-xs font-semibold text-gray-700  tracking-wider">
                                                                Status
                                                            </th>
                                                        </tr>
                                                    </thead>
                                                    <tbody className="bg-white">
                                                        {log.restore_files.map((file, fileIndex) => (
                                                            <tr key={file.id} className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${fileIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                                                                <td className="px-2 py-2 text-sm text-gray-900 break-words whitespace-normal" style={{ maxWidth: "12rem" }}>{file.backup_name}</td>
                                                                <td className="px-2 py-2 text-sm text-gray-600 break-words whitespace-normal" style={{ maxWidth: '12rem' }} title={file.file}>
                                                                    {file.file}
                                                                </td>
                                                                <td className="px-2 py-2 text-sm text-gray-600">{file.file_start.replace(' ', '/').replace(' ', '/')}</td>
                                                                <td className="px-2 py-2 text-sm text-gray-600">{file.file_end.replace(' ', '/').replace(' ', '/')}</td>
                                                                <td className="px-2 py-2 text-sm text-gray-600">
                                                                    <span className="flex items-center space-x-2">
                                                                        <Clock className="w-3 h-3 text-gray-400" />
                                                                        <span>{conversionInMinutes(file.file_restore_time)}</span>
                                                                    </span>
                                                                </td>
                                                                {log.restore_files?.some(file => file.reason) ? (
                                                                    <td className="px-2 py-2 text-sm text-gray-600 break-words whitespace-normal" style={{ maxWidth: '12rem' }} title={file.file}>
                                                                        {file.reason}
                                                                    </td>
                                                                ) : null}
                                                                <td className="px-2 py-2 text-sm">
                                                                    <span className="flex items-center space-x-2">
                                                                        {file.restore === "success" ? (
                                                                            <>
                                                                                <CheckCircle className="w-4 h-4 text-green-500" />
                                                                                <span className="text-green-700 font-semibold">Success</span>
                                                                            </>
                                                                        ) : (
                                                                            <>
                                                                                <AlertCircle className="w-4 h-4 text-red-500" />
                                                                                <span className="text-red-700 font-semibold">Failed</span>
                                                                            </>
                                                                        )}
                                                                    </span>
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </React.Fragment>
                        ))}
                    </tbody>
                </table>


                <JobFilterPopup
                    visible={showFilterPopup}
                    filters={filters}
                    setFilters={setFilters}
                    onApply={() => setApplyFilterTrigger(c => c + 1)}
                    onClose={() => fetchRestoreData(showRestoreReportEndPoint)}
                    nameOptions={[...new Set(normalizedData.map(item => item.computerName))]}
                    showEndpoint={false}
                    showStatus={false}
                />
                {alert && (
                    <AlertComponent
                        message={alert.message}
                        type={alert.type}
                        onClose={() => setAlert(null)}
                    />
                )}
            </div>
            {showSelectEndpointCode && <SelectEndpointPopup
                setEndPointListPopup={() => { }}
                setEndPointAgentName={setAgentName}
                setShowSelectEndpointCode={setShowSelectEndpointCode}
            />}
        </>
    );
};

export default BackupLogs;