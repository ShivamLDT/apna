import React, { useState, useEffect, useContext } from 'react';
import { BadgeCheck, CircleX, RefreshCw } from "lucide-react";
import config from '../../../config';
import JobCard from './JobCard';
import JobTable from './JobTable';
import JobFilterPopup from './JobFilterPopup';
import RepoIcon from './RepoIcon';
import SuccessFailurePanel from './SuccessFailurePanel';
import { useNavigate, useLocation } from 'react-router-dom';
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../../assets/pdf.png';
import XL from '../../../assets/XLSD.png';
import useSaveLogs from '../../../Hooks/useSaveLogs';
import axios from "axios";
import axiosInstance from '../../../axiosinstance';
import { RestoreContext } from '../../../Context/RestoreContext';
import LoadingComponent from '../../../LoadingComponent';

export default function FailedJobs() {
    const columns = [
        { title: 'Destination', width: '12%' },
        { title: 'Endpoint Name', width: '14%' },
        { title: 'Job Name', width: '16%' },
        { title: 'Location', width: '16%' },
        { title: 'Created Time', width: '14%' },
        { title: 'Missed Time', width: '14%' },
        { title: 'Error Description', width: '14%' }
    ];

    const renderRow = (item, index) => [
        <td key="repo" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal text-center">
            <RepoIcon repo={item.job_repo} />
        </td>,
        <td key="name" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {item.computerName || item.nodeName}
        </td>,
        <td key="jobname" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {item.job_name}
        </td>,
        <td key="location" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {item.job_folder}
        </td>,

        <td key="create" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {item.create_time?.replace("GMT", "IST")}
        </td>,
        <td key="done" className="border px-2 py-1 text-xs text-gray-700 break-words whitespace-normal">
            {(item.done_time || item.missed_time)?.replace("GMT", "IST")}
        </td>,
        <td key="err_desc" className="border px-2 py-1 text-xs text-red-500 break-words whitespace-normal">
            {item.error_desc}
        </td>,

    ];


    const accessJob = localStorage.getItem("AccessJob");
    const [failedData, setFailedData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [counts, setCounts] = useState({ total: 0, success: 0, failed: 0 });
    const [showFilter, setShowFilter] = useState(false);
    const [filters, setFilters] = useState({ name: '', repo: '', status: '', fromDate: '', toDate: '' });
    const navigate = useNavigate();
    const uniqueNames = [...new Set(failedData.map(item => item.computerName || item.nodeName))];
    const location = useLocation();
    const { setOpenSuccessful, openSuccessful } = useContext(RestoreContext);


    const uniqueFailedData = failedData.filter((job, index, arr) =>
        arr.findIndex(j =>
            j.job_name === job.job_name &&
            j.error_desc === job.error_desc &&
            j.missed_time === job.missed_time
        ) === index
    );
    const filteredData = uniqueFailedData.filter(item => {
        const name = item.computerName || item.nodeName || '';
        const nameMatch = !filters.name || name === filters.name;
        const repoMatch = !filters.repo || item.job_repo === filters.repo;
        const statusMatch = !filters.status || item.status === filters.status;
        const jobDateStr = item.done_time || item.missed_time;
        const jobDate = jobDateStr ? new Date(jobDateStr.replace('GMT', '')) : null;
        const from = filters.fromDate ? new Date(filters.fromDate + "T00:00:00") : null;
        const to = filters.toDate ? new Date(filters.toDate + "T23:59:59") : null;
        const dateMatch = (!from || (jobDate && jobDate >= from)) && (!to || (jobDate && jobDate <= to));
        return nameMatch && repoMatch && statusMatch && dateMatch;
    });

    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();


    const fetchFailedJobsData = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get(`${config.API.Server_URL}/api/getfailedjobs`, {
                headers: {
                    'Content-Type': 'application/json',
                    Job: accessJob
                },
            });

            const data = response.data;

            const failedJobs = data.failedjobs.map((jobs) => {
                return {
                    nodeName: jobs.nodeName,
                    data: Array.isArray(jobs.data) ? jobs.data.map(job => ({ ...job, nodeName: jobs.nodeName })) : []
                }
            });

            const allData = failedJobs
                .flatMap((job) => job.data)
                .filter((data) => data);

            const sortedJobs = allData.sort((a, b) => {
                const dateA = new Date((a.done_time || a.missed_time || '').replace('GMT', '').replace('IST', ''));
                const dateB = new Date((b.done_time || b.missed_time || '').replace('GMT', '').replace('IST', ''));
                return dateB - dateA;
            });

            setFailedData(sortedJobs);
            setCounts({
                total: sortedJobs.filter((job, index, arr) =>
                    arr.findIndex(j =>
                        j.job_name === job.job_name &&
                        j.error_desc === job.error_desc &&
                        j.missed_time === job.missed_time
                    ) === index
                ).length,
            });
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch data", error);
            setLoading(false);
        }
    };

    useEffect(() => { fetchFailedJobsData(); }, []);

    const getFormattedErrorMessage = (errorDesc) => {
        const errorReplacements = {
            "Connecting to file server is failed due to unkown reasons": "Data not found on destination",
        };

        return errorReplacements[errorDesc] || errorDesc;
    };

    const FailedAllPDF = ({ failedJobs, selectedEndpoint }) => {
        const currentDate = new Date().toLocaleString();
        const endpointName =
            selectedEndpoint && typeof selectedEndpoint === "object"
                ? selectedEndpoint.name || "Unknown Endpoint"
                : selectedEndpoint || "All Endpoint";
        return (
            <Document>
                <Page size="A4" style={Successcs.page}>
                    <View style={Successcs.section}>
                        <Image src="./apnalogo.png" style={Successcs.logo} />
                        <Text style={Successcs.titlee}>Failed Jobs Of {endpointName}</Text>
                        <Text style={Successcs.date}>Generated As On: {currentDate}</Text>

                        {/* chart rendering */}
                        <View style={Successcs.chartContainer}>
                            {/* <Image src={imageData} style={Successcs.chartImage} /> */}
                        </View>

                        <View style={Successcs.tableHeaderRow}>
                            <Text style={[Successcs.tableHeader, Successcs.borderRight]}>Destination</Text>
                            <Text style={[Successcs.tableHeader, Successcs.borderRight]}>Endpoint Name</Text>
                            <Text style={[Successcs.tableHeader, Successcs.borderRight]}>Job Name</Text>
                            <Text style={[Successcs.tableHeader, Successcs.borderRight]}>Location</Text>
                            <Text style={[Successcs.tableHeader, Successcs.borderRight]}>Created Time</Text>
                            <Text style={[Successcs.tableHeader, Successcs.borderRight]}>Missed Time</Text>
                            <Text style={Successcs.tableHeader}>Error Desc</Text>
                        </View>
                        {/* Table Section */}
                        <View style={Successcs.nodeContainer}>
                            <View style={Successcs.table}>
                                {failedJobs.length > 0 ? (
                                    failedJobs
                                        .filter((job, index, self) =>
                                            self.findIndex(j => j.job_name === job.job_name && j.error_desc === job.error_desc && j.missed_time === job.missed_time) === index
                                        )
                                        .map((job, i) => (

                                            // <View key={i}  style={Successcs.tableRow}>
                                            <View
                                                key={i}
                                                style={{
                                                    ...Successcs.tableRow,
                                                    backgroundColor: i % 2 === 0 ? '#f5f7fc' : '#ffffff', // Alternating row colors
                                                }}
                                            >
                                                <Text style={[Successcs.tableCell, Successcs.borderRight]}>{job.job_repo == "LAN" ? "On-Premise" : job.job_repo == "UNC" ? "LAN/NAS" : job.job_repo}</Text>
                                                <Text style={[Successcs.tableCell, Successcs.borderRight]}>{job.nodeName}</Text>
                                                <Text style={[Successcs.tableCell, Successcs.borderRight]}>{job.job_name}</Text>
                                                <Text style={[Successcs.tableCell, Successcs.borderRight]}>{job.job_folder}</Text>
                                                <Text style={[Successcs.tableCell, Successcs.borderRight]}>{job.create_time.replace('GMT', 'IST')}</Text>
                                                <Text style={[Successcs.tableCell, Successcs.borderRight]}>{job.missed_time.replace('GMT', 'IST')}</Text>
                                                <Text style={Successcs.error}>{job.error_desc}</Text>
                                            </View>
                                        ))
                                ) : (
                                    <Text style={Successcs.tableCell}>No data available for the selected node</Text>
                                )}
                            </View>
                        </View>
                    </View>
                </Page>
            </Document>
        )
    };

    const Successcs = StyleSheet.create({
        chartContainer: {
            display: 'flex',
            textAlign: 'center',
            alignItems: 'center',
            justifyContent: 'center',

        },
        chartImage: {
            width: 280,
            height: 180
        },
        mainHeader: {
            backgroundColor: '#D4D4D4',
            marginTop: 10,
            display: 'flex',
            gap: 2,
            textAlign: 'center',
        },
        headerSection: {
            flexDirection: 'row',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 20,
            textAlign: 'center', // Centering content
        },
        logo: {
            width: 100,
            height: 'auto',
            display: 'block', // Ensures the logo behaves like a block-level element
            marginLeft: 'auto', // Centers the logo horizontally
            marginRight: 'auto', // Centers the logo horizontally
        },

        badges: {
            maxWidth: '30',
            marginLeft: 'auto', // Centers the logo horizontally
            marginRight: 'auto', // Centers the logo horizontally
        },

        titleSection: {
            textAlign: 'center', // Centering the text
            marginLeft: 20,
            marginRight: 20, // Optional, for padding around the text
        },
        title: {
            fontSize: 16,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#007bff',
            marginBottom: 10,
            borderBottomWidth: 2, // Border under the section title for visual separation
            borderBottomColor: '#007bff', // Blue color for the border
        },
        titlee: {
            fontSize: 16,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#FF0000',
            marginBottom: 10,
            borderBottomWidth: 2, // Border under the section title for visual separation
            borderBottomColor: '#FF0000', // Blue color for the border
        },
        date: {
            textAlign: 'center', // Centering date text
            fontSize: 12,
            color: '#777',
            marginTop: 2,
        },
        page: {
            flexDirection: 'row',
            backgroundColor: '#FFFFFF', // Change to white background
        },
        section: {
            margin: 10,
            padding: 10,
            flexGrow: 1,
        },
        header: {
            fontSize: 15,
            marginBottom: 20,
            textAlign: 'center', // Centered header text
        },
        subheader: {
            fontSize: 14,
            marginBottom: 10,
            textAlign: 'center', // Center align the node name
        },
        nodeContainer: {
            marginBottom: 20,

        },
        table: {
            display: 'table',
            width: '100%',
            marginTop: 30,
            marginBottom: 30,

        },
        tableHeaderRow: {
            flexDirection: 'row',
            backgroundColor: '#FFFFFF',
            borderBottomWidth: 1,
            borderBottomColor: '#E4E4E4',
            // No borders here
        },
        tableHeader: {
            // fontWeight: 'bold',
            padding: 20,
            flex: 1,

            textAlign: 'center',
            fontSize: 8,
            borderBottomWidth: 1,
            borderBottomColor: '#E4E4E4',
            // Removed border
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
            overflow: "visible",
            textOverflow: "clip",
            textAlign: 'center',
        },
        error: {
            fontSize: 8, // Smaller font for minimal text

            flex: 1,
            textAlign: 'center', // Center-align error text
            color: '#FF0000', // Red for error text

            maxWidth: '50%', // Ensure it stays within the table cell
            lineHeight: 1, // Adjust line spacing for readability
            textOverflow: 'ellipsis', // Add ellipsis for overflowed text
            overflow: 'hidden', // Prevent text from overflowing the container
            whiteSpace: 'nowrap',
        },
        errorContainer: {
            marginTop: 10,
            padding: 10,
            backgroundColor: '#FFF5F5', // Light red background for error container
        },

    });

    const handleDownloadPDF = async () => {
        // html2canvas(chartFailedRef.current).then((canvas) => {
        //   setImageData(canvas.toDataURL());
        // });
        const pdfBlob = await pdf(<FailedAllPDF failedJobs={filteredData} selectedEndpoint={filters.name || "All Endpoints"} />).toBlob();
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'failed_jobs_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = `${filters.name || "All Endpoints"} Failed Jobs Report PDF Download`;
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**31st */
    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();

        const ff = [];
        ff.push(["Destination", "Computer Name", "Location", "Job Name", "Created Time", "Missed Time", "Error Desc."]); // Header row
        filteredData
            .filter((job, index, self) =>
                self.findIndex(j => j.job_name === job.job_name && j.error_desc === job.error_desc && j.missed_time === job.missed_time) === index
            )
            .forEach((job) => {
                ff.push([job.job_repo == "LAN" ? "On-Premise" : job.job_repo == "UNC" ? "LAN/NAS" : job.job_repo, job.nodeName, job.job_name, job.job_folder, job.create_time.replace('GMT', 'IST'), job.missed_time.replace('GMT', 'IST'), job.error_desc]);
            });
        const fData = XLSX.utils.aoa_to_sheet(ff);
        XLSX.utils.book_append_sheet(wb, fData, "Failed_Jobs_Report");

        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
        const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `failedReport_report.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = `${filters.name || "All Endpoints"} Failed Jobs Report Excel Download`;
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
        <div className="successful-jobs-container h-full flex flex-col">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-2 flex-shrink-0">
                <JobCard icon={<BadgeCheck />} amount="Executed Jobs" iconBg="bg-blue-100 text-blue-500" textColor="text-gray-800" onClick={() => HandleNavigateJob('/executedjob')} isActive={location.pathname === '/executedjob'} />
                <JobCard icon={<BadgeCheck />} amount="Successful Jobs" iconBg="bg-green-100 text-green-500" textColor="text-gray-800" onClick={() => HandleNavigateJob('/successfuljob')} isActive={location.pathname === '/successfuljob'} />
                <JobCard icon={<CircleX />} amount="Failed Jobs" iconBg="bg-red-100 text-red-500" textColor="text-gray-800" onClick={() => HandleNavigateJob('/failedjob')} isActive={location.pathname === '/failedjob'} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 flex-1 min-h-0">
                <div className="lg:col-span-1 flex flex-col space-y-2 h-full">
                    <div className="flex-1 flex items-center justify-center bg-white">

                        <SuccessFailurePanel title="Executed Data" count={counts.success} total={counts.total} color="#10b981" />
                    </div>
                    <div className="flex-1 flex items-center justify-center bg-white">

                        <SuccessFailurePanel title="Failed Data" count={counts.failed} total={counts.total} color="#ef4444" />
                    </div>
                </div>
                <div className="lg:col-span-4 flex flex-col min-h-0">
                    <div className="bg-white rounded-lg p-2 flex flex-col h-full job-table-container">
                        <div className="flex justify-between items-center mb-4 flex-shrink-0">
                            <h3 className="text-lg font-bold text-gray-800">Failed Jobs</h3>
                            <div className="flex items-center space-x-2">

                                <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                                <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />

                                <button title="Refresh" className="p-2 rounded hover:bg-gray-200 transition" onClick={() => fetchFailedJobsData()}>
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
                                //         @keyframes oceanSlide {
                                //             0% { transform: translateX(-150%); }
                                //             66% { transform: translateX(0%); }
                                //             100% { transform: translateX(150%); }
                                //         }
                                //     `}</style>
                                // </div>

                                <LoadingComponent />
                            ) : (
                                <JobTable columns={columns} data={filteredData} renderRow={renderRow} />
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <JobFilterPopup
                visible={showFilter}
                filters={filters}
                setFilters={setFilters}
                onApply={() => setShowFilter(false)}
                onClose={() => setShowFilter(false)}
                nameOptions={uniqueNames}
                showStatus={false}
            />
        </div>
    );
}
