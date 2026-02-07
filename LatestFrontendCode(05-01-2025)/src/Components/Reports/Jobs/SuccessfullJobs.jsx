import React, { useState, useEffect, useRef, useContext } from 'react';
import { BadgeCheck, CircleX, RefreshCw } from "lucide-react";
import config from '../../../config';
import JobCard from './JobCard';
import JobTable from './JobTable';
import RepoIcon from './RepoIcon';
import JobFilterPopup from './JobFilterPopup';
import SuccessFailurePanel from './SuccessFailurePanel';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import '../../Restore/Restore.css';
import { Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../../assets/pdf.png';
import XL from '../../../assets/XLSD.png';
import html2canvas from 'html2canvas';
import CryptoJS from "crypto-js"
import useSaveLogs from '../../../Hooks/useSaveLogs';
import axiosInstance from '../../../axiosinstance';
import { RestoreContext } from '../../../Context/RestoreContext';
 
import AlertComponent from '../../../AlertComponent';
import LoadingComponent from '../../../LoadingComponent';

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

export default function SuccessfullJobs() {
    const columns = [
        { title: 'Repo', width: '12%' },
        { title: 'Name', width: '25%' },
        { title: 'Date', width: '20%' },
        { title: 'Location', width: '25%' },
        { title: 'Accuracy', width: '20%' },
        // { title: 'Restore', width: '20%' },
    ];

    const getProgressColorByPercentage = (percentage) => {
        if (percentage >= 100) return "bg-green-500";
        if (percentage >= 75) return "bg-blue-500";
        if (percentage >= 50) return "bg-yellow-500";
        if (percentage >= 25) return "bg-purple-500";
        return "bg-red-500";
    };

    const renderRow = (item, index) => [
        <td key="repo" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal text-center">
            <RepoIcon repo={item.data_repo} />
        </td>,
        <td key="name" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {item.name}
        </td>,
        <td key="jobname" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {item.last_modified}
        </td>,
        <td key="location" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {item.location}
        </td>,
        <td key="create" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
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
        </td>,
        // <td key="done" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
        //     {item.last_modified}
        // </td>,

    ];
    const accessJob = localStorage.getItem("AccessJob");
    const [imageData, setImageData] = useState(null)
    const [successData, setSuccessData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [counts, setCounts] = useState({ total: 0, success: 0, failed: 0 });
    const [showFilter, setShowFilter] = useState(false);
    const [filters, setFilters] = useState({ name: '', repo: '', location: '', fromDate: '', toDate: '' });
    const navigate = useNavigate();
    const uniqueNames = [...new Set(successData.map(item => item.computerName || item.nodeName))];
    const location = useLocation();
    const { setOpenSuccessful } = useContext(RestoreContext);
    const [applyFilterTrigger, setApplyFilterTrigger] = useState(0);
    const [restoreData, setRestoreData] = useState([]);
    const [alert, setAlert] = useState(null);


    const parseJobDate = (dateStr) => {
        if (!dateStr) return null;

        const cleaned = dateStr.replace('IST', 'GMT+0530');
        const parsedDate = new Date(cleaned);
        return isNaN(parsedDate) ? null : parsedDate;
    };

    const parseLastModified = (str) => {
        if (!str) return null;
        const tryDate = new Date(String(str).replace("IST", "GMT+0530"));
        if (!isNaN(tryDate)) return tryDate;

        // Example input: "04/07/2025, 07:38:34 PM"
        const [datePart, timePart] = String(str).split(", ");
        if (!datePart || !timePart) return null;
        const [day, month, year] = datePart.split("/").map(Number);
        const [time, period] = timePart.split(" ");
        let [hours, minutes, seconds] = time.split(":").map(Number);
        if (period === "PM" && hours < 12) hours += 12;
        if (period === "AM" && hours === 12) hours = 0;
        return new Date(year, month - 1, day, hours, minutes, seconds);
    };
    const normalizedData = successData?.map(item => ({
        ...item,
        name: item.job_name || item.name,
        data_repo: item.job_repo || item.data_repo,
        from_computer: item.computerName || item.from_computer || item.nodeName,
        computerName: item.computerName || item.from_computer || item.nodeName,
        last_modified: item.done_time || item.create_time || item.last_modified,
        location: item.job_folder || item.location,
        wdone: item.wdone ?? 100,
        status: item.status || 'success',
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

    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();
    const accessToken = localStorage.getItem("AccessToken");
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

    const today = new Date();
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1, 0, 0, 0);
    const endDate = today;


    const fetchSuccessfulJobsData = async () => {
        setShowFilter(false)
        const userPrivileges = JSON.parse(decryptData(localStorage.getItem("user_privileges")) || "{}");
        if (userRole === "Employee" && !userPrivileges.restoreReadWrite) {
            setAlert({
                message: "You do not have permission to access this section.",
                type: 'error'
            });
            return;
        }

        setLoading(true);
        try {
            const response = await axiosInstance.get(`${config.API.Server_URL}/api/getsuccessjobs`, {
                headers: {
                    "Content-Type": "application/json",
                    Job: accessJob,
                },
            });

            const data = response.data;
            const successJobs = (data?.successjobs || []).map((jobs) => ({
                nodeName: jobs.nodeName,
                data: Array.isArray(jobs.data) ? jobs.data.map(job => ({ ...job, nodeName: jobs.nodeName })) : []
            }));

            const allData = successJobs
                .flatMap((job) => job.data)
                .filter((item) => item);

            const sortedJobs = allData.sort((a, b) => {
                const dateA = parseLastModified(a.done_time || a.create_time || '');
                const dateB = parseLastModified(b.done_time || b.create_time || '');
                if (!dateA || !dateB) return 0;
                return dateB - dateA;
            });

            setSuccessData(sortedJobs);
            setCounts({ total: sortedJobs.length, success: sortedJobs.length, failed: 0 });
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch data", error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSuccessfulJobsData();
    }, []);

    const chartSuccessRef = useRef(null)

    useEffect(() => {
        if (chartSuccessRef.current) {
            html2canvas(chartSuccessRef.current).then((canvas) => {
                setImageData(canvas.toDataURL());
            });
        }
    }, [chartSuccessRef])

    function Successfull({ successfulData, selectedEndpoint }) {
        const currentDate = new Date().toLocaleString();
        return (
            <Document>
                <Page size="A4" style={Successcs.page}>
                    <View style={Successcs.section}>
                        <Image src="./apnalogo.png" style={Successcs.logo} />
                        <Text style={Successcs.title}>Success Jobs Of: {selectedEndpoint || "All Endpoints"}</Text>
                        <Text style={Successcs.date}>Generated As On: {currentDate}</Text>


                        {/* chart rendering */}
                        <View style={Successcs.chartContainer}>
                            {/* <Image src={imageData} style={Successcs.chartImage} /> */}
                        </View>


                        {/* Table Section */}
                        <View style={Successcs.nodeContainer}>
                            <View style={Successcs.table}>
                                <View style={Successcs.tableHeaderRow}>
                                    <Text style={Successcs.tableHeader}>Repo</Text>
                                    <Text style={Successcs.tableHeader}>Name</Text>
                                    <Text style={Successcs.tableHeader}>Date</Text>
                                    <Text style={Successcs.tableHeader}>Location</Text>
                                    <Text style={Successcs.tableHeader}>Accuracy</Text>
                                </View>

                                {/* Check if the node has successful jobs */}
                                {successfulData && successfulData.length > 0 ? (
                                    successfulData.map((job, i) => (
                                        <View
                                            key={i}
                                            style={{
                                                ...Successcs.tableRow,
                                                backgroundColor: i % 2 === 0 ? '#f5f7fc' : '#ffffff', // Alternating row colors
                                            }}
                                        >
                                            <Text style={Successcs.tableCell}>{job.data_repo === "LAN" ? "On-Premise" : (job.data_repo === "UNC" ? "LAN/NAS" : job.data_repo)}</Text>
                                            <Text style={Successcs.tableCell}>{job.name}</Text>
                                            <Text style={Successcs.tableCell}>{job.last_modified}</Text>
                                            <Text style={Successcs.tableCell}>{job.location}</Text>
                                            <Text style={Successcs.tableCell}>{job.wdone}</Text>
                                        </View>
                                    ))
                                ) : (
                                    <Text style={Successcs.tableCell}>No job data available for this node.</Text>
                                )}
                            </View>
                        </View>
                    </View>
                </Page>
            </Document>
        )

    }
    const Successcs = StyleSheet.create({
        chartContainer: {
            display: 'flex',
            alignItems: 'center', // Centers items vertically
            justifyContent: 'center', // Centers items horizontally
            textAlign: 'center',
        },
        chartImage: {
            width: 280,
            height: 180,
        },
        mainHeader: {
            backgroundColor: '#D4D4D4',
            marginTop: 10,
            display: 'flex',
            gap: 2,
            textAlign: 'center',
            alignItems: 'center', // Added for vertical alignment consistency
            justifyContent: 'center', // Horizontal alignment
        },
        headerSection: {
            flexDirection: 'row',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 20,
            textAlign: 'center',
        },
        logo: {
            width: 100,
            height: 'auto',
            display: 'block',
            marginLeft: 'auto',
            marginRight: 'auto',
        },
        badges: {
            maxWidth: 30,
            marginLeft: 'auto',
            marginRight: 'auto',
        },
        titleSection: {
            textAlign: 'center',
            marginHorizontal: 20, // Shorthand for marginLeft and marginRight
        },
        title: {
            fontSize: 16,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#007bff',
            marginBottom: 10,
            borderBottomWidth: 2,
            borderBottomColor: '#007bff',
        },
        titlee: {
            fontSize: 16,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#FF0000',
            marginBottom: 10,
            borderBottomWidth: 2,
            borderBottomColor: '#FF0000',
        },
        date: {
            textAlign: 'center',
            fontSize: 12,
            color: '#777',
            marginTop: 2,
        },
        page: {
            flexDirection: 'row',
            backgroundColor: '#FFFFFF',
        },
        section: {
            margin: 10,
            padding: 10,
            flexGrow: 1,
        },
        header: {
            fontSize: 20,
            marginBottom: 20,
            textAlign: 'center',
        },
        subheader: {
            fontSize: 14,
            marginBottom: 10,
            textAlign: 'center',
        },
        nodeContainer: {
            marginBottom: 20,
        },
        table: {
            display: 'table',
            width: '100%',
            marginTop: 10,
        },
        tableHeaderRow: {
            flexDirection: 'row',
            backgroundColor: '#FFFFFF',
            borderBottomWidth: 1,
            borderBottomColor: '#E4E4E4',
        },
        tableHeader: {
            fontWeight: 'bold',
            padding: 10,
            flex: 1,
            textAlign: 'center',
            fontSize: 12,
            borderBottomWidth: 1,
            borderBottomColor: '#E4E4E4',
        },
        tableRow: {
            flexDirection: 'row',
            alignItems: 'stretch',
            width: '100%',
            borderBottomWidth: 1,
            borderBottomColor: '#ccc',
            minHeight: 20,
        },
        tableCell: {
            fontSize: 8,
            padding: 8,
            flex: 1,
            wordWrap: "break-word",
            whiteSpace: "normal",
            overflow: "hidden",
            textOverflow: "clip",
            textAlign: 'center',
        },
        error: {
            fontSize: 8,
            padding: 10,
            flex: 1,
            textAlign: 'center',
            color: '#FF0000',
        },
    });


    const handleDownloadPDF = async () => {
        if (chartSuccessRef.current) {
            html2canvas(chartSuccessRef.current).then((canvas) => {
                setImageData(canvas.toDataURL());
            });
        }
        const pdfBlob = await pdf(<Successfull successfulData={filteredData} selectedEndpoint={"All Endpoints"} />).toBlob();
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'success_jobs_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = `${filters.name || "All Endpoints"} Successful Jobs Report PDF Download`;
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
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
            void isAllRepo;

            setLoading(true);
            try {
                await fetchSuccessfulJobsData();
                setShowFilter(false);
            } catch (error) {
                console.error("Error refetching success jobs:", error);
            } finally {
                setLoading(false);
            }
        };
        handleApplyFilters();

    }, [applyFilterTrigger]);

    /**31st */
    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();
        const ss = [];

        // Add the header row
        ss.push(["Repo", "Name", "Date", "Location", "Accuracy"]);

        // Add data
        filteredData.forEach((job) => {
            ss.push([job.data_repo === "LAN" ? "On-Premise" : (job.data_repo === "UNC" ? "LAN/NAS" : job.data_repo), job.name, job.last_modified, job.location, job.wdone]);
        });

        // Create sheet from data
        const sData = XLSX.utils.aoa_to_sheet(ss);

        // Apply basic styles: bold header row and column width adjustment
        const headerStyle = { font: { bold: true }, alignment: { horizontal: "center" } };

        // Apply style to the header row
        for (let col = 0; col < ss[0].length; col++) {
            const cell = sData[XLSX.utils.encode_cell({ r: 0, c: col })];
            if (cell) {
                cell.s = headerStyle;
            }
        }

        // Set column widths (example: for 4 columns)
        sData["!cols"] = [
            { wpx: 80 }, // Destination
            { wpx: 250 }, // Job Name
            { wpx: 200 }, // Start Time
            { wpx: 150 }, // Type
            { wpx: 260 }, // Location
            { wpx: 120 }, // Accuracy
            { wpx: 180 }, // Endpoint
        ];

        // Append the sheet to the workbook
        XLSX.utils.book_append_sheet(wb, sData, "Successful_Jobs_Report");

        // Download the Excel file
        // XLSX.writeFile(wb, "Successful_Jobs_Report.xlsx");


        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
        const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `successfuljobs_report.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = `${filters.name || "All Endpoints"} Successful Jobs Report Excel Download`;
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function s2ab(str) {
        const buf = new ArrayBuffer(str.length);
        const view = new Uint8Array(buf);
        for (let i = 0; i < str.length; i++) {
            view[i] = str.charCodeAt(i) & 0xFF;
        }
        return buf;
    }

    function HandleNavigateJob(path) {
        navigate(path);
        if (path === "/successfuljob") {
            setOpenSuccessful(true)
        }

    }

    return (

        <>
            <div className="successful-jobs-container h-full flex flex-col">
                {/* Job Cards Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-2 flex-shrink-0">
                    <JobCard icon={<BadgeCheck />} amount="Executed Jobs" iconBg="bg-blue-100 text-blue-500" textColor="text-gray-800" onClick={() => HandleNavigateJob('/executedjob')} isActive={location.pathname === '/executedjob'} />
                    <JobCard icon={<BadgeCheck />} amount="Successful Jobs" iconBg="bg-green-100 text-green-500" textColor="text-gray-800" onClick={() => HandleNavigateJob('/successfuljob')} isActive={location.pathname === '/successfuljob'} />
                    <JobCard icon={<CircleX />} amount="Failed Jobs" iconBg="bg-red-100 text-red-500" textColor="text-gray-800" onClick={() => HandleNavigateJob('/failedjob')} isActive={location.pathname === '/failedjob'} />
                </div>

                {/* Main Content Area - Modified grid layout for better proportions */}
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 flex-1 min-h-0">
                    {/* Left Panel - Success/Failure panels - Reduced width */}
                    <div className="lg:col-span-1 flex flex-col space-y-2 h-full">
                        <div className="flex-1 flex items-center justify-center bg-white">
                            <SuccessFailurePanel title="Executed Data" count={counts.success} total={counts.total} color="#10b981" />
                        </div>
                        <div className="flex-1 flex items-center justify-center bg-white">
                            <SuccessFailurePanel title="Failed Data" count={counts.failed} total={counts.total} color="#ef4444" />
                        </div>
                    </div>

                    {/* Right Panel - Jobs Table - Increased width */}
                    <div className="lg:col-span-4 flex flex-col min-h-0">
                        <div className="bg-white rounded-lg p-2 flex flex-col h-full job-table-container">
                            {/* Header - Fixed height */}
                            <div className="flex justify-between items-center mb-4 flex-shrink-0">
                                <h3 className="text-lg font-bold text-gray-800">Successful Backup Jobs (All Endpoints)</h3>
                                <div className="flex items-center space-x-2">
                                    <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                                    <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />

                                    <button title="Refresh" className="p-2 rounded hover:bg-gray-200 transition" onClick={() => fetchSuccessfulJobsData()}>
                                        <RefreshCw size={20} />
                                    </button>
                                    <button
                                        onClick={() => setShowFilter(true)}
                                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                                    >
                                        Filter Jobs ({filteredData.length})
                                    </button>
                                </div>
                            </div>

                            {/* Table Content - Expandable */}
                            <div className="flex-1 min-h-0 overflow-hidden">
                                {loading ? (
                                    // <div className="flex justify-center items-center h-full">
                                    //     <div className="relative w-64 h-4 bg-blue-200 rounded-xl overflow-hidden">
                                    //         <div
                                    //             className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
                                    //             style={{ animation: 'oceanSlide 3s infinite' }}
                                    //         />
                                    //     </div>
                                    //     <style>{`
                                    //     @keyframes oceanSlide {
                                    //         0% { transform: translateX(-150%); }
                                    //         66% { transform: translateX(0%); }
                                    //         100% { transform: translateX(150%); }
                                    //     }
                                    // `}</style>
                                    // </div>

                                    <LoadingComponent />
                                ) : (
                                    <JobTable columns={columns} data={filteredData} renderRow={renderRow} />
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Filter Popup */}
                <JobFilterPopup
                    visible={showFilter}
                    filters={filters}
                    setFilters={setFilters}
                    onApply={() => setApplyFilterTrigger(c => c + 1)}
                    onClose={() => fetchSuccessfulJobsData()}
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

        </>
    );
}