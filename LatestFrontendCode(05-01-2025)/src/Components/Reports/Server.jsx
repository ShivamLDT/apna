import React, { useState, useEffect, useContext, useRef } from 'react';
import { PieChart, Pie, Cell, LineChart, Line, ResponsiveContainer, Tooltip } from 'recharts';
import {
    Monitor,
    Wifi,
    Shield,
    Activity,
    HardDrive,
    Cpu,
    MemoryStick,
    Globe,
    ChevronDown,
    MonitorCheck,
    RefreshCw
} from 'lucide-react';
import { useServerData } from "../Dashboard/useServerData";
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../assets/pdf.png';
import XL from '../../assets/XLSD.png';
import config from '../../config';
import CryptoJS from "crypto-js";
import useSaveLogs from '../../Hooks/useSaveLogs';
import { Backupindex } from '../../Context/Backupindex';
import { ToastContainer, toast } from 'react-toastify';
import { useToast } from '../../ToastProvider';
import { sendNotification } from '../../Hooks/useNotification';
import { NotificationContext } from "../../Context/NotificationContext";
import LoadingComponent from '../../LoadingComponent';
const Server = () => {
    const { serverData, diskData, memoryData, processorData, networkData, loading, error, refetch } = useServerData();
    const { setNotificationData } = useContext(NotificationContext);
    const [processorLineData, setProcessorLineData] = useState([]);
    const [memoryLineData, setMemoryLineData] = useState([]);

    const { showToast } = useToast();

    const [selectedDisk, setSelectedDisk] = useState('');
    const [lastNotified, setLastNotified] = useState(null);

    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();
    const accessToken = localStorage.getItem("AccessToken");

    const formatDataSize = (size) => {
        const units = ['MB', 'GB', 'TB', 'PB'];
        let unitIndex = 0;

        if (size === 0) return '0 MB';

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        return size.toFixed(2) + ' ' + units[unitIndex];
    };
    // useEffect(() => {
    //     const interval = setInterval(() => {
    //         refetch(false);
    //     }, 10000);

    //     return () => clearInterval(interval);
    // }, []);

    useEffect(() => {
        const interval = setInterval(() => {
            setProcessorLineData(prev => {
                const newData = {
                    name: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                    value: processorData?.usage || 0
                };
                return [...prev.slice(-5), newData];
            });

            setMemoryLineData(prev => {
                const newData = {
                    name: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                    value: memoryData?.percentage || 0
                };
                return [...prev.slice(-5), newData];
            });
        }, 2000);

        return () => clearInterval(interval);
    }, [processorData?.usage, memoryData?.percentage]);


    useEffect(() => {
        if (diskData?.length && !selectedDisk) {
            setSelectedDisk(diskData[0].name);
        }
    }, [diskData, selectedDisk]);

    useEffect(() => {
        if (processorData?.usage > 90) {
            // prevent duplicate notifications for the same usage
            if (lastNotified !== processorData.usage) {
                const Notification_local_Data = {
                    id: Date.now(),
                    message: `⚠️ High Processor usage ${processorData.usage}%.`,
                    timestamp: new Date(),
                    isRead: false,
                };

                setNotificationData((prev) => [Notification_local_Data, ...prev]);
                sendNotification(Notification_local_Data.message);
                showToast(Notification_local_Data.message, "warning");

                setLastNotified(processorData.usage);
            }
        }
    }, [processorData, lastNotified]);

    const alertedDisksRef = useRef(new Set());

    useEffect(() => {
        if (
            serverData?.server_connected_nodes?.result &&
            Array.isArray(serverData.server_connected_nodes.result)
        ) {
            serverData.server_connected_nodes.result.forEach((node) => {
                const disks = node?.data?.disk || [];

                disks.forEach((disk) => {
                    const diskKey = `${node.agent}_${disk.device}`;

                    if (disk.percent > 90 && !alertedDisksRef.current.has(diskKey)) {
                        // Trigger your notification logic here
                        const Notification_local_Data = {
                            id: Date.now(), // unique ID
                            message: `⚠️ Disk usage alert! Agent: ${node.agent}, Disk: ${disk.device}, Usage: ${disk.percent}%`,
                            timestamp: new Date(),
                            isRead: false,
                        };
                        sendNotification(`⚠️ Disk usage alert! Agent: ${node.agent}, Disk: ${disk.device}, Usage: ${disk.percent}%`,)
                        showToast(`⚠️ Disk usage alert! Agent: ${node.agent}, Disk: ${disk.device}, Usage: ${disk.percent}%`, "warning")
                        setNotificationData((prev) => [...prev, Notification_local_Data]);
                        alertedDisksRef.current.add(diskKey);
                    }

                    // Optional: if disk usage goes below threshold, remove from alert set
                    if (disk.percent <= 90 && alertedDisksRef.current.has(diskKey)) {
                        alertedDisksRef.current.delete(diskKey);
                    }
                });
            });
        }
    }, [serverData]);



    const uploadValue = parseFloat(networkData?.sent || 0);
    const downloadValue = parseFloat(networkData?.received || 0);
    const networkMax = uploadValue + downloadValue || 1;


    const uploadChart = [{ name: 'Upload', value: uploadValue, color: '#10b981' }];
    const downloadChart = [{ name: 'Download', value: downloadValue, color: '#3b82f6' }];

    const RADIAN = Math.PI / 180;

    const needle = (value, data, cx, cy, iR, oR, color) => {
        let total = data.reduce((acc, v) => acc + v.value, 0);
        if (total === 0 || isNaN(value)) return null;

        const ang = 180.0 * (1 - value / total);
        const length = (iR + 2 * oR) / 3;
        const sin = Math.sin(-RADIAN * ang);
        const cos = Math.cos(-RADIAN * ang);
        const r = 5;
        const x0 = cx, y0 = cy;
        const xba = x0 + r * sin;
        const yba = y0 - r * cos;
        const xbb = x0 - r * sin;
        const ybb = y0 + r * cos;
        const xp = x0 + length * cos;
        const yp = y0 + length * sin;

        return [
            <circle key="needle-center" cx={x0} cy={y0} r={r} fill={color} />,
            <path key="needle" d={`M${xba} ${yba}L${xbb} ${ybb} L${xp} ${yp} Z`} fill={color} />
        ];
    };


    const Serversrepo = ({ serverrepo, servercss }) => {
        const currentDate = new Date().toLocaleString();


        return (
            <Document>
                <Page size="A4" style={servercss.page}>
                    <View style={servercss.section}>
                        <Image src="./apnalogo.png" style={servercss.logo} />
                        <Text style={servercss.title}>Apna Backup Server Report</Text>
                        <Text style={servercss.date}>Generated As On: {currentDate}</Text>


                        {/* Server Activation Date and Version */}
                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>Apna Backup Server Details</Text>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Activation Date:</Text>
                                <Text style={servercss.value}>{serverrepo.server_activation_date}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Server Version:</Text>
                                <Text style={servercss.value}>{serverrepo.server_version}</Text>
                            </View>
                        </View>

                        {/* System Information */}
                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>System Information</Text>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Manufacturer:</Text>
                                <Text style={servercss.value}>{serverrepo.system?.manufacturer}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Architecture:</Text>
                                <Text style={servercss.value}>{serverrepo.os?.architecture}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Model:</Text>
                                <Text style={servercss.value}>{serverrepo.system?.model}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>System Name:</Text>
                                <Text style={servercss.value}>{serverrepo.system?.name}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>OS:</Text>
                                <Text style={servercss.value}>{serverrepo.os?.name} {serverrepo.os?.version}</Text>
                            </View>
                        </View>

                        {/* Processor Information */}
                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>Processor</Text>
                            {/* <View style={servercss.row}>
                    <Text style={servercss.label}>Name:</Text>
                    <Text style={servercss.value}>{serverrepo.processor?.name}</Text>
                  </View> */}
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Logical Cores:</Text>
                                <Text style={servercss.value}>{serverrepo.processor?.count} Cores</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Physical Cores:</Text>
                                <Text style={servercss.value}>{serverrepo.processor?.physical} Cores</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>CPU Usage:</Text>
                                <Text style={servercss.value}>{serverrepo.processor?.usage}%</Text>
                            </View>
                        </View>

                        {/* Memory Information */}
                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>Memory</Text>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Total:</Text>
                                <Text style={servercss.value}>{serverrepo.memory?.total}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Used:</Text>
                                <Text style={servercss.value}>{serverrepo.memory?.used}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Available:</Text>
                                <Text style={servercss.value}>{serverrepo.memory?.available}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Usage:</Text>
                                <Text style={servercss.value}>{serverrepo.memory?.percentage}%</Text>
                            </View>
                        </View>

                        {/* Disk Information */}
                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>Disk Usage</Text>

                            {/* Header Row with single heading per column */}
                            <View style={servercss.tableRow}>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Device</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Mountpoint</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Type</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Total</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Used</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Free</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Usage</Text>
                                </View>
                            </View>

                            {/* Mapping Disk Data and showing data in columns */}
                            {serverrepo.disk?.length > 0 ? (
                                serverrepo.disk.map((disk, index) => (
                                    <View key={index} style={servercss.tableRow}>
                                        <View style={servercss.tableCell}>
                                            <Text style={servercss.valuee}>{disk.device}</Text>
                                        </View>
                                        <View style={servercss.tableCell}>
                                            <Text style={servercss.valuee}>{disk.mountpoint}</Text>
                                        </View>
                                        <View style={servercss.tableCell}>
                                            <Text style={servercss.valuee}>{disk.type}</Text>
                                        </View>
                                        <View style={servercss.tableCell}>
                                            <Text style={servercss.valuee}>{disk.total}</Text>
                                        </View>
                                        <View style={servercss.tableCell}>
                                            <Text style={servercss.valuee}>{disk.used}</Text>
                                        </View>
                                        <View style={servercss.tableCell}>
                                            <Text style={servercss.valuee}>{disk.free}</Text>
                                        </View>
                                        <View style={servercss.tableCell}>
                                            <Text style={servercss.valuee}>{disk.percent}%</Text>
                                        </View>
                                    </View>
                                ))
                            ) : (
                                <Text style={servercss.text}>No disk data available.</Text>
                            )}
                        </View>

                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>Network Addresses</Text>

                            <View style={servercss.networkRow}>
                                <View style={servercss.networkColumn}>
                                    <Text style={servercss.sectionSubtitleText}>IP Addresses:</Text>
                                    <Text style={servercss.networkItem}>
                                        {serverrepo.ip_addresses?.split(',').map((ip, index, arr) => (
                                            <Text key={index} style={servercss.networkValue}>
                                                {ip.trim()}
                                                {index < arr.length - 1 ? ', ' : ''}
                                            </Text>
                                        ))}
                                    </Text>
                                </View>

                                <View style={servercss.networkColumn}>
                                    <Text style={servercss.sectionSubtitleText}>MAC Addresses:</Text>
                                    <Text style={servercss.networkItem}>
                                        {serverrepo.mac_addresses?.split(',').map((mac, index, arr) => (
                                            <Text key={index} style={servercss.networkValue}>
                                                {mac.trim()}
                                                {index < arr.length - 1 ? ', ' : ''}
                                            </Text>
                                        ))}
                                    </Text>
                                </View>
                            </View>
                        </View>


                        {/* Network Usage */}
                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>Network Usage</Text>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Received:</Text>
                                <Text style={servercss.value}>{serverrepo.network?.received}</Text>
                            </View>
                            <View style={servercss.row}>
                                <Text style={servercss.label}>Sent:</Text>
                                <Text style={servercss.value}>{serverrepo.network?.sent}</Text>
                            </View>
                        </View>

                        <View style={servercss.sectionTitle}>
                            <Text style={servercss.sectionTitleText}>Connected Endpoints</Text>

                            {/* Header Row with sorting functionality */}
                            <View style={servercss.tableRow}>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Sr. No.</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Endpoints</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Status</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>IP Address</Text>
                                </View>
                                <View style={servercss.tableCell}>
                                    <Text style={servercss.header}>Last Connected</Text>
                                </View>
                            </View>

                            {/* Sorting by IP Address */}
                            {serverrepo.server_connected_nodes?.result?.length > 0 ? (
                                // Sort the nodes by IP address (ascending order)
                                serverrepo.server_connected_nodes.result
                                    .sort((a, b) => {
                                        const ipA = a.ipAddress.replace('http://', '').replace(':7777', '');
                                        const ipB = b.ipAddress.replace('http://', '').replace(':7777', '');

                                        // Compare the IPs lexicographically (alphabetical sorting)
                                        if (ipA < ipB) return -1;
                                        if (ipA > ipB) return 1;
                                        return 0;
                                    })
                                    .map((node, index) => (
                                        <View key={index} style={servercss.tableRow}>
                                            <View style={servercss.tableCell}>
                                                <Text style={servercss.valuee}>{index + 1}</Text>
                                            </View>
                                            <View style={servercss.tableCell}>
                                                <Text style={servercss.valuee}>{node.agent}</Text>
                                            </View>
                                            <View style={servercss.tableCell}>
                                                <Text
                                                    style={[
                                                        servercss.valuee,
                                                        node.lastConnected === 'True' ? { color: 'green' } : { color: 'red' }
                                                    ]}
                                                >
                                                    {node.lastConnected === 'True' ? 'Online' : 'offline'}

                                                </Text>
                                            </View>
                                            <View style={servercss.tableCell}>
                                                <Text style={servercss.valuee}>
                                                    {node.ipAddress.replace('http://', '').replace(':7777', '')}
                                                </Text>
                                            </View>

                                            <View style={servercss.tableCell}>
                                                <Text style={servercss.valuee}>
                                                    {node.lastConnected !== 'True' ? node.lastConnectedTime : 'connected'}
                                                </Text>
                                            </View>


                                        </View>
                                    ))
                            ) : (
                                <Text style={servercss.text}>No connected nodes available.</Text>
                            )}
                        </View>

                    </View>
                </Page>
            </Document>
        );
    };

    const servercss = StyleSheet.create({
        networkColumn: {
            padding: 10,
            flex: 1,  // Ensures the columns take equal space
            textAlign: 'center',
        },
        networkRow: {
            flexDirection: 'row',  // Ensures the title and MAC addresses are in a row
            justifyContent: 'space-between',  // Distributes columns evenly
            alignItems: 'flex-start',  // Aligns items at the top of the row
            flexDirection: 'row', // Keep title and value in the same row
            alignItems: 'center',
            paddingHorizontal: 10,

        },
        sectionSubtitleText: {
            fontSize: 12,
            width: '50%',
            fontWeight: 'bold',
            color: '#333',
            textAlign: 'center',
            marginLeft: '50px',
            marginRight: 5,
        },
        networkItem: {
            flexDirection: 'row',
            flexWrap: 'nowrap',
            justifyContent: 'center',

        },
        networkValue: {
            fontSize: 12,
            color: '#555',
            marginBottom: 10, // Add some spacing between each address
            textAlign: 'center',

        },
        page: {
            flexDirection: 'column',
            backgroundColor: '#FFFFFF',
            padding: 15,
            height: '100%',
        },
        section: {
            marginBottom: 20,
            flex: 1,

        },
        logo: {
            width: 120,
            height: 'auto',
            display: 'block',
            alignSelf: 'center',
            marginBottom: 10,
        },
        title: {
            fontSize: 18,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#007bff',
            marginBottom: 8,
            borderBottomWidth: 2,
            borderBottomColor: '#007bff',
            paddingBottom: 5,
        },
        date: {
            textAlign: 'center',
            fontSize: 12,
            color: '#777',
            marginTop: 2,
        },
        sectionTitle: {
            marginTop: 4,
        },
        sectionTitleText: {
            fontSize: 14,
            fontWeight: 'bold',
            color: '#333',
            backgroundColor: '#e7edf1',
            width: '100%',
            textAlign: 'center',
            paddingLeft: 10,
            paddingVertical: 5,
        },
        row: {
            flexDirection: 'row',
            marginBottom: 8,
            alignItems: 'center',
            // marginLeft: 'left',
        },
        label: {
            width: '30%',
            fontWeight: 'bold',
            fontSize: 12,
            color: '#333',
            textAlign: 'left',
            marginLeft: 50,
            marginTop: 10,

        },
        value: {
            fontSize: 12,
            color: '#555',
            flex: 1,
            textAlign: 'center',
        },
        text: {
            fontSize: 12,
            color: '#555',
            marginBottom: 5,
        },
        // New Styles for Table View
        tableContainer: {
            borderWidth: 1,
            borderColor: '#ddd',
            borderRadius: 5,
            overflow: 'hidden',  // Keeps table inside border
            width: '100%',
            marginTop: 10,
        },
        tableHeader: {
            flexDirection: 'row',
            backgroundColor: '#f4f4f4',
            paddingVertical: 10,
            paddingHorizontal: 15,
            borderBottomWidth: 1,
            borderBottomColor: '#ddd',
        },
        tableHeaderText: {
            fontWeight: 'bold',
            fontSize: 14,
            color: '#333',
            textAlign: 'center',
            flex: 1,
        },
        tableRow: {
            flexDirection: 'row',
            paddingVertical: 10,
            paddingHorizontal: 15,
            borderBottomWidth: 1,
            borderBottomColor: '#ddd',
        },
        tableCell: {
            flex: 1,
            textAlign: 'center',  // Center-align the cell contents
            fontSize: 12,
            color: '#555',
        },
        labell: {
            fontWeight: 'bold',
            fontSize: 12,
            color: '#333',
            textAlign: 'left',  // Left-align the label
        },
        valuee: {
            fontSize: 12,
            color: '#555',
            textAlign: 'center',  // Center-align the value text
        },
        text: {
            fontSize: 12,
            color: '#555',
            textAlign: 'center',
            marginBottom: 5,
        },

    });
    const handleDownloadPDF = async () => {
        const pdfBlob = await pdf(<Serversrepo serverrepo={serverData} servercss={servercss} />).toBlob();
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'server_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = "Server Report PDF Download";
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**31/01 */
    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();
        const serverepop = [];
        const headerStyle = {
            font: { bold: true },
            alignment: { horizontal: "center", vertical: "center" }
        };


        // Add System Information
        if (serverData.system?.manufacturer && serverData.system?.architecture) {
            serverepop.push(["System Information"]);
            serverepop.push(["Manufacturer", "Architecture", "Model", "System Name", "OS"]);
            serverepop.push([serverData.system?.manufacturer, serverData.system?.architecture, serverData.system?.model, serverData.system?.name, `${serverData.os?.name} ${serverData.os?.version}`]);
            serverepop.push([""]); // <-- Add empty row for spacing


        }

        // Add Processor Information
        if (serverData.processor?.name) {
            serverepop.push([{ v: "Processor ", s: headerStyle }]);
            serverepop.push([" "])


        } {


            serverepop.push([
                { v: "Logical Cores", s: headerStyle },
                { v: "Physical Cores", s: headerStyle },
                { v: "CPU Usage", s: headerStyle }
            ]);

            serverepop.push([serverData.processor?.count, serverData.processor?.physical, `${serverData.processor?.usage}%`]);
            serverepop.push([""]); // <-- Add empty row for spacing

        }

        // Add Memory Information
        if (serverData.memory?.total) {
            serverepop.push([{ v: "Memory", s: headerStyle }]);
            serverepop.push([{ v: "Total", s: headerStyle }, { v: "Used", s: headerStyle }, { v: "Available", s: headerStyle }, { v: "Usage", s: headerStyle }]);
            serverepop.push([serverData.memory?.total, serverData.memory?.used, serverData.memory?.available, `${serverData.memory?.percentage}%`]);
            serverepop.push([""]); // <-- Add empty row for spacing

        }

        // Add Disk Information
        if (serverData.disk?.length > 0) {
            serverepop.push(["Disk Usage"]);
            serverepop.push(["Device", "Mountpoint", "Type", "Total", "Used", "Free", "Percent"]);
            serverData.disk.forEach(disk => {
                serverepop.push([disk.device, disk.mountpoint, disk.type, disk.total, disk.used, disk.free, disk.percent]);
            });
            serverepop.push([""]); // <-- Add empty row for spacing


        }

        // Add IP Addresses
        if (serverData.ip_addresses?.length > 0) {
            serverepop.push(["Server IP Addresses"]);
            serverepop.push([serverData.ip_addresses]);
            serverepop.push([""]); // <-- Add empty row for spacing
        }

        // Add Network Usage
        if (serverData.network?.received) {
            serverepop.push(["Network Usage"]);
            serverepop.push(["Received", "Sent"]);
            serverepop.push([serverData.network?.received, serverData.network?.sent]);
            serverepop.push([""]); // <-- Add empty row for spacing
        }

        // Add Server Details
        if (serverData.server_activation_date) {
            serverepop.push(["Server Details"]);
            serverepop.push(["Activation Date", "Server Version"]);
            serverepop.push([serverData.server_activation_date, serverData.server_version]);
            serverepop.push([""]); // <-- Add empty row for spacing


        }

        // Add Connected Endpoints
        if (serverData.server_connected_nodes?.result?.length > 0) {
            serverepop.push(["Connected Endpoints"]);
            serverepop.push(["Sr. No.", "Endpoints", "IP Address", "Status"]);
            serverData.server_connected_nodes.result.forEach((node, index) => {
                serverepop.push([index + 1, node.agent, node.ipAddress.replace('http://', '').replace(':7777', ''), node.lastConnected === 'True' ? 'Connected' : 'Disconnected']);
            });
        } else {
            serverepop.push(["", "No connected nodes available."]);
        }

        const serverExcel = XLSX.utils.aoa_to_sheet(serverepop);




        // Auto-fit column width dynamically
        serverExcel["!cols"] = serverepop[1].map((_, colIndex) => ({
            wch: Math.max(...serverepop.map(row => (row[colIndex] ? row[colIndex].toString().length : 10))) + 5
        }));

        // Create a new workbook and append the sheet
        XLSX.utils.book_append_sheet(wb, serverExcel, "Server Report");

        // Save the workbook
        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
        const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Server_report.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = "Server Report Excel Download";
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

    // Handle error state if needed
    if (error) {
        return (
            <div className="bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center text-red-600 font-semibold text-lg">
                Error loading server data: {error.message || "Unknown error"}
            </div>
        );
    }

    return (
        <div className="bg-gradient-to-br from-gray-50 to-blue-50">
            {/* Header */}
            <div className="flex justify-between items-center mb-1">
                <h1 className="text-xl font-bold text-gray-800">Server Dashboard</h1>

                <div className="flex items-center space-x-2">
                    <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                    <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />

                    <button
                        onClick={refetch}
                        className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 shadow-sm hover:shadow-md"
                    >
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Performance Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-2 mb-1">
                {/* CPU Usage */}
                <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-6 shadow-2xl border border-white border-opacity-20 hover:shadow-2xl transition-all duration-300">
                    <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                                <Cpu className="w-3 h-3 text-white" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Processor Usage</p>
                                <p className="text-sm font-bold text-gray-800">{processorData?.usage}%</p>
                            </div>
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={60}>
                        <LineChart data={processorLineData}>
                            <Tooltip
                                contentStyle={{ fontSize: '12px', backgroundColor: '#f9f9f9', borderRadius: '8px', border: '1px solid #ccc' }}
                                labelStyle={{ fontWeight: 'bold', color: '#333' }}
                                formatter={(value) => [`${value?.toFixed(1)}%`, 'Processor Usage']}
                            />
                            <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#8b5cf6"
                                strokeWidth={3}
                                dot={false}
                                strokeLinecap="round"
                            />

                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Memory Usage */}
                <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-6 shadow-2xl border border-white border-opacity-20 hover:shadow-2xl transition-all duration-300">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
                                <MemoryStick className="w-3 h-3 text-black" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Memory Usage</p>
                                <p className="text-sm font-bold text-gray-800">{memoryData?.percentage}%</p>
                            </div>
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={60}>
                        <LineChart data={memoryLineData}>
                            <Tooltip
                                contentStyle={{ fontSize: '12px', backgroundColor: '#f9f9f9', borderRadius: '8px', border: '1px solid #ccc' }}
                                labelStyle={{ fontWeight: 'bold', color: '#333' }}
                                formatter={(value) => [`${value?.toFixed(1)}%`, 'Memory Usage']}
                            />
                            <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#06b6d4"
                                strokeWidth={3}
                                dot={false}
                                strokeLinecap="round"
                            />

                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Network Upload */}
                <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-2 shadow-2xl border border-white border-opacity-20 hover:shadow-2xl transition-all duration-300">
                    <div className="flex items-center space-x-3 mb-4">
                        <div className="p-2 bg-gradient-to-r from-green-500 to-green-600 rounded-lg">
                            <Activity className="w-3 h-3 text-white" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Upload</p>
                            <p className="text-sm font-bold text-gray-800">{formatDataSize(uploadValue)}</p>
                        </div>
                    </div>
                    <div className="flex items-center justify-center">
                        <PieChart width={150} height={100}>
                            <Pie
                                dataKey="value"
                                startAngle={180}
                                endAngle={0}
                                data={[{ name: 'Upload', value: uploadValue, color: '#10b981' }, { name: 'Remaining', value: networkMax - uploadValue, color: '#e5e7eb' }]}
                                cx={75}
                                cy={75}
                                innerRadius={30}
                                outerRadius={60}
                                fill="#8884d8"
                                stroke="none"
                            >
                                {[{ name: 'Upload', value: uploadValue, color: '#10b981' }, { name: 'Remaining', value: networkMax - uploadValue, color: '#e5e7eb' }].map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            {needle(uploadValue, [{ name: 'Upload', value: uploadValue, color: '#10b981' }, { name: 'Remaining', value: networkMax - uploadValue, color: '#e5e7eb' }], 75, 75, 30, 60, '#1f2937')}
                        </PieChart>
                    </div>
                    <div className="text-center mt-1 text-sm text-gray-600">
                        {Math.round((uploadValue / networkMax) * 100)}%
                    </div>
                </div>

                {/* Network Download */}
                <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-2 shadow-2xl border border-white border-opacity-20 hover:shadow-2xl transition-all duration-300">
                    <div className="flex items-center space-x-3 mb-4">
                        <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                            <Globe className="w-3 h-3 text-white" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Download</p>
                            <p className="text-sm font-semibold text-gray-800">{formatDataSize(downloadValue)}</p>
                        </div>
                    </div>
                    <div className="flex items-center justify-center">
                        <PieChart width={150} height={100}>
                            <Pie
                                dataKey="value"
                                startAngle={180}
                                endAngle={0}
                                data={[{ name: 'Download', value: downloadValue, color: '#3b82f6' }, { name: 'Remaining', value: networkMax - downloadValue, color: '#e5e7eb' }]}
                                cx={75}
                                cy={75}
                                innerRadius={30}
                                outerRadius={60}
                                fill="#8884d8"
                                stroke="none"
                            >
                                {[{ name: 'Download', value: downloadValue, color: '#3b82f6' }, { name: 'Remaining', value: networkMax - downloadValue, color: '#e5e7eb' }].map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            {needle(downloadValue, [{ name: 'Download', value: downloadValue, color: '#3b82f6' }, { name: 'Remaining', value: networkMax - downloadValue, color: '#e5e7eb' }], 75, 75, 30, 60, '#1f2937')}
                        </PieChart>
                    </div>
                    <div className="text-center mt-1 text-sm text-gray-600">
                        {Math.round((downloadValue / networkMax) * 100)}%
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-2 mb-1">
                {/* Disk Performance */}
                <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-2 shadow-2xl border border-white border-opacity-20">
                    <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-gradient-to-r from-yellow-500 to-red-500 rounded-lg">
                                <HardDrive className="w-3 h-3 text-white" />
                            </div>
                            <h3 className="text-sm font-semibold text-gray-800">Disk Performance</h3>
                        </div>

                        <div className="relative">
                            <select
                                value={selectedDisk}
                                onChange={(e) => setSelectedDisk(e.target.value)}
                                className="pl-3 pr-8 py-1 bg-white bg-opacity-50 border border-gray-200 rounded-xl appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm w-28"
                            >
                                {diskData?.map((disk, index) => (
                                    <option key={index} value={disk.name}>
                                        {disk.name}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    {diskData
                        ?.filter((disk) => disk.name === selectedDisk)
                        .map((disk, index) => {
                            const usedPercent = ((disk.used / disk.total) * 100).toFixed(1);

                            return (
                                <div key={index} className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <h4 className="font-medium text-gray-800">{disk.name}</h4>
                                        <span className="text-sm text-gray-600">{usedPercent}% used</span>
                                    </div>

                                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full transition-all duration-500"
                                            style={{ width: `${usedPercent}%` }}>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-3 gap-4 text-sm">
                                        <div className="text-center p-2 bg-gray-50 rounded-lg">
                                            <p className="text-gray-600">Total</p>
                                            <p className="font-semibold text-gray-800">{disk.total_raw}</p>
                                        </div>
                                        <div className="text-center p-2 bg-gray-50 rounded-lg">
                                            <p className="text-gray-600">Used</p>
                                            <p className="font-semibold text-gray-800">{disk.used_raw}</p>
                                        </div>
                                        <div className="text-center p-2 bg-gray-50 rounded-lg">
                                            <p className="text-gray-600">Free</p>
                                            <p className="font-semibold text-gray-800">{disk.free_raw}</p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                </div>

                {/* Server Information */}
                <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-2 shadow-2xl border border-white border-opacity-20">
                    <div className="flex items-center space-x-2 mb-1">
                        <div className="p-2 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg">
                            <Monitor className="w-3 h-3 text-white" />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-800">Server Information</h3>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div className="p-2 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-100 hover:shadow-lg transition-all duration-300">
                            <div className="flex items-center space-x-2 mb-2">
                                <MonitorCheck className="w-3 h-3 text-blue-600" />
                                <h6 className="text-sm font-semibold text-gray-800">Server</h6>
                            </div>
                            <p className="text-xs text-gray-600 mb-1">{serverData?.system?.name}</p>
                            <p className="text-xs text-gray-500">version {serverData?.server_version}</p>
                        </div>

                        <div className="p-2 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-100 hover:shadow-lg transition-all duration-300">
                            <div className="flex items-center space-x-3 mb-2">
                                <Monitor className="w-3 h-3 text-green-600" />
                                <h6 className="text-sm font-semibold text-gray-800">Operating System</h6>
                            </div>
                            <p className="text-xs text-gray-600 mb-1">{serverData?.os?.name}</p>
                            <p className="text-xs text-gray-500">{`${serverData?.system?.manufacturer || ''} ${serverData?.system?.model || ''}`}</p>
                        </div>

                        <div className="p-2 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100 hover:shadow-lg transition-all duration-300">
                            <div className="flex items-center space-x-3 mb-2">
                                <Globe className="w-3 h-3 text-purple-600" />
                                <h6 className="text-sm font-semibold text-gray-800">IP Addresses</h6>
                            </div>
                            <p className="text-xs text-gray-600 break-all">{serverData?.ip_addresses}</p>
                        </div>

                        <div className="p-2 bg-gradient-to-r from-yellow-50 to-red-50 rounded-xl border border-yellow-100 hover:shadow-lg transition-all duration-300">
                            <div className="flex items-center space-x-3 mb-2">
                                <Wifi className="w-3 h-3 text-yellow-600" />
                                <h6 className="text-sm font-semibold text-gray-800">MAC Addresses</h6>
                            </div>
                            <p className="text-xs text-gray-600 break-all">{serverData?.mac_addresses}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Endpoints Overview */}
            <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-2 shadow-2xl border border-white border-opacity-20">
                <div className="flex items-center space-x-3 mb-1">
                    <div className="p-2 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-lg">
                        <Shield className="w-3 h-3 text-black" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Connected Endpoints</h3>
                    <div className="ml-auto px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        {serverData?.server_connected_nodes?.result?.filter(node => node.lastConnected === "True").length || 0} Online
                    </div>
                </div>

                <div className="overflow-auto h-48">
                    <table className="w-full">
                        <thead className="sticky bg-blue-500 text-white top-0 z-10">
                            <tr className="border-b border-gray-200">
                                <th className="text-left p-3 text-sm font-semibold">Endpoint</th>
                                <th className="text-left p-3 text-sm font-semibold">IP Address</th>
                                <th className="text-left p-3 text-sm font-semibold">MAC Address</th>
                                <th className="text-left p-3 text-sm font-semibold">Version</th>
                                <th className="text-left p-3 text-sm font-semibold">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {serverData?.server_connected_nodes?.result?.map((node, index) => (
                                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 hover:bg-opacity-50 transition-colors">
                                    <td className="p-2">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-5 h-5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                                                <Monitor className="w-3 h-3 text-white" />
                                            </div>
                                            <span className="text-sm font-medium text-gray-800">{node.agent}</span>
                                        </div>
                                    </td>
                                    <td className="p-3 text-sm text-gray-600">{node.data?.ip_addresses}</td>
                                    <td className="p-3 text-sm text-gray-600 font-mono">{node.data?.mac_addresses}</td>
                                    <td className="p-3 text-sm text-gray-600">{node.data?.client_version}</td>
                                    <td className="p-3">
                                        <div className="flex items-center space-x-2">
                                            <div className={`w-2 h-2 rounded-full animate-pulse ${node.lastConnected === "True" ? "bg-green-500" : "bg-gray-400"}`}></div>
                                            <span className={`text-sm font-medium ${node.lastConnected === "True" ? "text-green-700" : "text-gray-500"}`}>
                                                {node.lastConnected === "True" ? "Online" : "Offline"}
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            {/* <ToastContainer position="top-right" autoClose={3000} /> */}
        </div>
    );
};

export default Server;