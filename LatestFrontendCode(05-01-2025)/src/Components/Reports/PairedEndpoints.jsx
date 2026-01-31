import { useState, useEffect } from "react";
import config from "../../config";
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../assets/pdf.png';
import XL from '../../assets/XLSD.png';
import useSaveLogs from "../../Hooks/useSaveLogs";
import axios from 'axios';
import axiosInstance from "../../axiosinstance";
import { useJobs } from "../Jobs/JobsContext";
import LoadingComponent from "../../LoadingComponent";

const PairedEndpoints = () => {
    const [enpData, setEnpData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [filteredUsers, setFilteredUsers] = useState([]);
    const accessToken = localStorage.getItem("AccessToken");
    const { refreshClients } = useJobs();

    const { profilePic, userName, userRole, handleLogsSubmit } = useSaveLogs();



    const fetchEndpointData = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get(`${config.API.Server_URL}/clientnodes`, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken,
                },
            });

            const data = response.data;
            setEnpData(data.result);
            setFilteredUsers(data.result);
            setLoading(false);
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!searchTerm) {
            setFilteredUsers(enpData);
        } else {
            const filtered = enpData.filter(user =>
                user.agent?.toLowerCase().includes(searchTerm.toLowerCase())
            );
            setFilteredUsers(filtered);
        }
    }, [searchTerm, enpData]);

    useEffect(() => {
        refreshClients();
        fetchEndpointData();
    }, []);

    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
    };

    const Allendpointss = ({ allendpointr }) => {
        const currentDate = new Date().toLocaleString();
        return (
            <Document>
                <Page size="A4" style={endpoint.page}>
                    <View style={endpoint.section}>
                        <Image src="./apnalogo.png" style={endpoint.logo} />
                        <Text style={endpoint.title}>All Endpoints</Text>
                        <Text style={endpoint.date}>Generated As On: {currentDate}</Text>
                        {allendpointr && allendpointr.length > 0 ? (
                            <>
                                {/* Render the table headers only once */}
                                <View style={endpoint.tableHeaderRow}>
                                    <Text style={[endpoint.tableHeader, endpoint.borderRight]}>Sr. No.</Text>
                                    <Text style={[endpoint.tableHeader, endpoint.borderRight]}>Endpoint</Text>
                                    <Text style={[endpoint.tableHeader, endpoint.borderRight]}>IP Address</Text>
                                    <Text style={[endpoint.tableHeader, endpoint.borderRight]}>Mac Address</Text>
                                    <Text style={[endpoint.tableHeader, endpoint.borderRight]}>Status</Text>
                                    <Text style={[endpoint.tableHeader, endpoint.borderRight]}>Last Connected Time</Text>
                                </View>

                                {/* Render data rows with alternating row colors */}
                                {allendpointr.map((e, index) => (
                                    <View
                                        key={index}
                                        style={[
                                            endpoint.tableRow,
                                            { backgroundColor: index % 2 === 0 ? '#f5f7fc' : '#ffffff' }, // Alternating colors
                                        ]}
                                    >
                                        <Text style={[endpoint.tableCell, endpoint.borderRight]}>{index + 1}</Text>
                                        <Text style={[endpoint.tableCell, endpoint.borderRight]}>{e.agent}</Text>

                                        {/* Display IP Address */}
                                        <Text style={[endpoint.tableCell, endpoint.borderRight]}>
                                            {e.data?.ip_addresses}
                                        </Text>
                                        <Text style={[endpoint.tableCell, endpoint.borderRight]}>
                                            {e.data?.mac_addresses || "No data available"}
                                        </Text>
                                        {/* Display Last Connected Status */}
                                        <Text style={[e.lastConnected === 'True' ? { color: 'green' } : { color: 'red' }, endpoint.tableCell, endpoint.borderRight]} >
                                            {e.lastConnected === 'True' ? 'Online' : 'Offline'}
                                        </Text>
                                        {/* Display Last Connected Time */}

                                        <Text style={[endpoint.tableCell, endpoint.borderRight]}>{e.lastConnectedTime}</Text>
                                    </View>

                                ))}
                            </>
                        ) : (
                            <Text style={endpoint.tableCell}>No data available for the selected node</Text>
                        )}
                    </View>
                </Page>
            </Document>
        );
    };

    const endpoint = StyleSheet.create({
        section: {
            fontFamily: 'Helvetica',
            backgroundColor: '#f7f7f7',
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
        titleSection: {
            textAlign: 'center', // Centering the text
            marginLeft: 20,
            marginRight: 20, // Optional, for padding around the text
            textAlign: 'center',
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
            fontSize: 20,
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
            marginTop: 10,
        },
        tableHeaderRow: {
            flexDirection: 'row',
            backgroundColor: '#ffffff',
            borderBottomWidth: 0,
        },
        tableHeader: {
            fontWeight: 'bold',
            padding: 8,
            flex: 1,
            textAlign: 'center',
            fontSize: 8,
            borderRightWidth: 1, // Vertical line between columns
            borderRightColor: '#E4E4E4', // Vertical border color
        },
        tableRow: {
            flexDirection: 'row',
            borderBottomWidth: 0, // Removed horizontal border between rows
            paddingTop: 0,  // Remove padding to avoid extra space between rows
            paddingBottom: 0, // Avoid extra space below the row
        },
        tableCell: {
            fontSize: 8,
            padding: 10,
            flex: 1,
            textAlign: 'center',
            borderRightWidth: 1, // Vertical line between columns
            borderRightColor: '#E4E4E4', // Vertical border color
        },
        borderRight: {
            borderRightWidth: 0.4, // Vertical border line
            borderRightColor: '#E4E4E4', // Vertical line color
        },
    });


    const handleDownloadPDF = async () => {
        const pdfBlob = await pdf(<Allendpointss allendpointr={filteredUsers} allendpointcss={endpoint} />).toBlob();
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Allendpoints_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = 'Allendpoints report PDF Download';
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**31st */
    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();
        const enData = [];

        enData.push(["Endpoint", "Ip Addresses", "Mac Addresses", "Status", "Last Connected Time"]); // Header row
        filteredUsers.forEach((job) => {
            const connectionStatus = job.lastConnected === 'True' ? 'Online' : 'Offline';
            enData.push([job.agent, job?.data?.ip_addresses, job?.data?.mac_addresses, connectionStatus, job.lastConnectedTime,]);
        });
        const enDataa = XLSX.utils.aoa_to_sheet(enData);
        const headerStyle = { font: { bold: true }, alignment: { horizontal: "center" } };

        // Apply style to the header row
        for (let col = 0; col < enData[0].length; col++) {
            const cell = enDataa[XLSX.utils.encode_cell({ r: 0, c: col })];
            if (cell) {
                cell.s = headerStyle;
            }
        }

        // Set column widths (example: for 4 columns)
        enDataa["!cols"] = [
            { wpx: 180 }, // Job Name column width
            { wpx: 350 }, // Created Time column width
            { wpx: 400 }, // Executed Time column width
            { wpx: 90 }, // Endpoint column width
            { wpx: 200 }, // Job Name column width


        ];





        XLSX.utils.book_append_sheet(wb, enDataa, "Allendpoint_Report");

        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
        const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `AllEndpoint_report.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = 'Allendpoints report Excel Download';
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

    return (
        <div className="h-full relative overflow-x-auto shadow-md sm:rounded-lg">
            <div className="flex items-center justify-between flex-column flex-wrap md:flex-row space-y-4 md:space-y-0 pb-4 bg-white dark:bg-gray-900">
                <label htmlFor="table-search" className="sr-only">Search</label>
                <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        id="table-search-users"
                        className="block w-80 pl-10 pr-3 py-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 transition-colors duration-200"
                        placeholder="Search for Endpoint"
                        value={searchTerm}
                        onChange={handleSearchChange}
                    />
                </div>

                <div className="flex items-center space-x-2">

                    <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                    <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />


                </div>
            </div>
            <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-white uppercase bg-blue-600">
                    <tr>
                        <th className="px-6 py-3">SR NO</th>
                        <th className="px-6 py-3">Endpoint Name</th>
                        <th className="px-6 py-3">IP Address</th>
                        <th className="px-6 py-3">Mac Address</th>
                        <th className="px-6 py-3">Status</th>
                        <th className="px-6 py-3">Last Connected Time</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredUsers.length === 0 ? (
                        <tr>
                            <td colSpan="6" className="text-center py-8 text-gray-500 dark:text-gray-300">
                                No endpoints available
                            </td>
                        </tr>
                    ) : (
                        filteredUsers.map((item, index) => (
                            <tr
                                key={index}
                                className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                            >
                                <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                                    {index + 1}
                                </td>
                                <td className="px-6 py-4">{item.agent}</td>
                                <td className="px-6 py-4">{item.ip}</td>
                                <td className="px-6 py-4">{item?.data?.mac_addresses}</td>
                                <td className="px-6 py-4">
                                    <span
                                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full
                                        ${item.lastConnected == "True"
                                                ? "bg-green-100 text-green-800"
                                                : "bg-red-100 text-red-800"
                                            }`}
                                    >
                                        {item.lastConnected == "True" ? "Online" : "Offline"}
                                    </span>
                                </td>
                                <td className="px-6 py-4">{item.lastConnectedTime}</td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );

};

export default PairedEndpoints;
