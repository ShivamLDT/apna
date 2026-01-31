import React, { useState, useEffect, useRef, useContext } from 'react';
import { BadgeCheck, CircleX, RefreshCw } from "lucide-react";
import config from '../../../config';
import JobCard from './JobCard';
import JobTable from './JobTable';
import RepoIcon from './RepoIcon';
import JobFilterPopup from './JobFilterPopup';
import SuccessFailurePanel from './SuccessFailurePanel';
import { useNavigate, useLocation } from 'react-router-dom';
import { useJobs } from '../../Jobs/JobsContext';
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../../assets/pdf.png';
import XL from '../../../assets/XLSD.png';
import html2canvas from 'html2canvas';
import CryptoJS from "crypto-js";
import useSaveLogs from '../../../Hooks/useSaveLogs';
import axios from "axios";
import axiosInstance from '../../../axiosinstance';
import { RestoreContext } from '../../../Context/RestoreContext';
import LoadingComponent from '../../../LoadingComponent';
export default function ExecutedJobs() {
    const columns = [
        { title: 'Destination', width: '12%' },
        { title: 'Endpoint Name', width: '14%' },
        { title: 'Job Name', width: '16%' },
        { title: 'Location', width: '18%' },
        { title: 'Created Time', width: '14%' },
        { title: 'Done Time', width: '14%' },
        { title: 'Status', width: '12%' }
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
        <td key="create" className="border px-2 py-1 text-xs text-gray-800 break-words whitespace-normal">
            {(item.done_time || item.missed_time)?.replace("GMT", "IST")}
        </td>,
        <td key="done" className="border px-2 py-1 text-xs text-gray-800 break-words whitespace-normal">
            {item.create_time?.replace("GMT", "IST")}
        </td>,
        <td key="status" className="border px-2 py-1 text-xs break-words whitespace-normal">
            <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full
        ${item.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {item.status === "success" ? "Executed" : "Not Executed"}
            </span>
        </td>

    ];

    const { executedJobs, jobCounts } = useJobs();
    const accessJob = localStorage.getItem("AccessJob");
    const [executedData, setExecutedData] = useState([]);
    const [counts, setCounts] = useState({ total: 0, success: 0, failed: 0 });
    const [showFilter, setShowFilter] = useState(false);
    const [loading, setLoading] = useState(false);
    const [imageData, setImageData] = useState(null)
    const [filters, setFilters] = useState({ name: '', repo: '', status: '', fromDate: '', toDate: '' });
    const navigate = useNavigate();
    const uniqueNames = [...new Set(executedData.map(item => item.computerName || item.nodeName))];
    const location = useLocation();
    const { setOpenSuccessful, openSuccessful } = useContext(RestoreContext);
    const filteredData = executedData.filter(item => {
        const name = item.computerName || item.nodeName || '';
        const nameMatch = !filters.name || name === filters.name;
        const repoMatch = !filters.repo || item.job_repo === filters.repo;
        const statusMatch = !filters.status || item.status === filters.status;
        const jobDateStr = item.done_time || item.missed_time;
        let jobDate = null;
        if (jobDateStr) {
            jobDate = new Date(jobDateStr.replace("IST", "+0530"));
        }
        const from = filters.fromDate ? new Date(filters.fromDate + "T00:00:00") : null;
        const to = filters.toDate ? new Date(filters.toDate + "T23:59:59") : null;
        const dateMatch =
            (!from || (jobDate && jobDate >= from)) &&
            (!to || (jobDate && jobDate <= to));
        return nameMatch && repoMatch && statusMatch && dateMatch;
    });


    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();
    const accessToken = localStorage.getItem("AccessToken");


    const fetchExecutedJobsData = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get(`${config.API.Server_URL}/api/getfailedsuccessjobs`, {
                headers: {
                    'Content-Type': 'application/json',
                    Job: accessJob
                },
            });

            const data = response.data;
            const jobs = data?.[0]?.data || [];

            const uniqueJobs = [
                ...jobs.filter(job => job.status === "success"),
                ...jobs
                    .filter(job => job.status === "failed")
                    .filter((job, index, arr) =>
                        arr.findIndex(j =>
                            j.job_name === job.job_name &&
                            j.error_desc === job.error_desc &&
                            j.missed_time === job.missed_time
                        ) === index
                    )
            ];

            const sortedJobs = uniqueJobs.sort((a, b) => {
                const dateA = new Date((a.done_time || a.missed_time || '').replace('GMT', '').replace('IST', ''));
                const dateB = new Date((b.done_time || b.missed_time || '').replace('GMT', '').replace('IST', ''));
                return dateB - dateA;
            });

            setExecutedData(sortedJobs);
            setCounts({
                total: sortedJobs.length,
                success: sortedJobs.filter(job => job.status === 'success').length,
                failed: sortedJobs.filter(job => job.status === "failed").length,
            });
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch data", error);
            setLoading(false);
        }
    };


    useEffect(() => { fetchExecutedJobsData(); }, []);

    const successPercentage = counts.total ? Math.round((counts.success / counts.total) * 100) : 0;
    const failedPercentage = counts.total ? Math.round((counts.failed / counts.total) * 100) : 0;

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
                        <Text style={Successcs.title}>Executed Jobs Of: {selectedEndpoint || "All Endpoints"}</Text>
                        <Text style={Successcs.date}>Generated As On: {currentDate}</Text>


                        {/* chart rendering */}
                        <View style={Successcs.chartContainer}>
                            {/* <Image src={imageData} style={Successcs.chartImage} /> */}
                        </View>


                        {/* Table Section */}
                        <View style={Successcs.nodeContainer}>
                            <View style={Successcs.table}>
                                <View style={Successcs.tableHeaderRow}>
                                    <Text style={Successcs.tableHeader}>Destination</Text>
                                    <Text style={Successcs.tableHeader}>Endpoint Name</Text>
                                    <Text style={Successcs.tableHeader}>Job Name</Text>
                                    <Text style={Successcs.tableHeader}>Location</Text>
                                    <Text style={Successcs.tableHeader}>Created Time</Text>
                                    <Text style={Successcs.tableHeader}>Executed Time</Text>
                                    <Text style={Successcs.tableHeader}>Status</Text>
                                </View>

                                {/* Check if the node has successful jobs */}
                                {successfulData && successfulData.length > 0 ? (
                                    successfulData
                                        .filter((job, index, self) => {
                                            if (job.status === "failed") {

                                                return self.findIndex(j => j.job_name === job.job_name && j.error_desc === job.error_desc && j.missed_time === job.missed_time) === index;
                                            }
                                            return true;
                                        }).map((job, i) => (
                                            <View
                                                key={i}
                                                style={{
                                                    ...Successcs.tableRow,
                                                    backgroundColor: i % 2 === 0 ? '#f5f7fc' : '#ffffff', // Alternating row colors
                                                }}
                                            >
                                                <Text style={[Successcs.tableCell]}>{job.job_repo == "LAN" ? "On-Premise" : job.job_repo == "UNC" ? "LAN/NAS" : job.job_repo}</Text>
                                                <Text style={[Successcs.tableCell]}>{job.computerName || job.nodeName}</Text>
                                                <Text style={[Successcs.tableCell]}>{job.job_name}</Text>
                                                <Text style={[Successcs.tableCell]}>{job.job_folder}</Text>
                                                <Text style={[Successcs.tableCell]}>{job.done_time || job.missed_time.replace('GMT', 'IST')}</Text>
                                                <Text style={[Successcs.tableCell]}>{job.create_time.replace('GMT', 'IST')}</Text>
                                                <Text
                                                    style={[
                                                        Successcs.tableCell,
                                                        job.status === "failed" && { color: "red" }
                                                    ]}
                                                >
                                                    {job.status === "success" ? "Executed" : "Not Executed"}
                                                </Text>

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
            paddingBottom: 5,
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
            fontSize: 10,
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
            overflow: "visible",
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
        const pdfBlob = await pdf(<Successfull successfulData={filteredData} selectedEndpoint={filters.name || "All Endpoints"} />).toBlob(); const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'executed_jobs_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = `${filters.name || "All Endpoints"} Executed Jobs Report PDF Download`;
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }


    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();
        const ss = [];
        ss.push(["Destination", "Endpoint Name ", " Job Name", "Location", "Created Time", "Executed Time", "Status"]); // Header row
        filteredData.filter((job, index, self) => {
            if (job.status === "failed") {
                return self.findIndex(j => j.job_name === job.job_name && j.error_desc === job.error_desc && j.missed_time === job.missed_time) === index;
            }
            return true;
        }).forEach((job) => {
            ss.push([job.job_repo == "LAN" ? "On-Premise" : job.job_repo == "UNC" ? "LAN/NAS" : job.job_repo, job.computerName || job.nodeName, job.job_name, job.job_folder, job.done_time || job.missed_time.replace('GMT', 'IST'), job.create_time.replace('GMT', 'IST'), job.status === "success" ? "Executed" : "Not Executed"]);
        });
        const sData = XLSX.utils.aoa_to_sheet(ss);
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
            { wpx: 100 }, // Job Name column width
            { wpx: 110 }, // Created Time column width
            { wpx: 100 }, // Executed Time column width
            { wpx: 200 }, // Endpoint column width
            { wpx: 180 }, // Job Name column width


        ];

        XLSX.utils.book_append_sheet(wb, sData, "Successfull_Jobs_Report");
        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
        const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `executedjobs_report.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = `${filters.name || "All Endpoints"} Executed Jobs Report Excel Download`;
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
                        <SuccessFailurePanel title="Executed Data" count={counts.success} total={counts.total} percentage={successPercentage} color="#10b981" />
                    </div>
                    <div className="flex-1 flex items-center justify-center bg-white">
                        <SuccessFailurePanel title="Failed Data" count={counts.failed} total={counts.total} percentage={failedPercentage} color="#ef4444" />
                    </div>
                </div>
                <div className="lg:col-span-4 flex flex-col min-h-0">
                    <div className="bg-white rounded-lg p-2 flex flex-col h-full job-table-container">
                        <div className="flex justify-between items-center mb-4 flex-shrink-0">
                            <h3 className="text-lg font-bold text-gray-800">Executed Jobs</h3>
                            <div className="flex items-center space-x-2">

                                <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                                <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />

                                <button title="Refresh" className="p-2 rounded hover:bg-gray-200 transition" onClick={() => fetchExecutedJobsData()}>
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
            />
        </div>
    );
}
