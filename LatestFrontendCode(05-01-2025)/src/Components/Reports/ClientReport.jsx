import React, { useState, useEffect } from 'react';
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
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../assets/pdf.png';
import XL from '../../assets/XLSD.png';
import useClientData from '../../Hooks/useClientData';
import SelectEndpointPopup from './SelectEndpointPopup';
import config from '../../config';
import CryptoJS from "crypto-js";
import useSaveLogs from '../../Hooks/useSaveLogs';
import LoadingComponent from '../../LoadingComponent';
const ClientReport = () => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [processorLineData, setProcessorLineData] = useState([]);
  const [memoryLineData, setMemoryLineData] = useState([]);
  const [selectedDisk, setSelectedDisk] = useState('');

  const { clientData, loading, error, refetch } = useClientData();

  const agentEntry = clientData?.result?.find((entry) => entry.agent === selectedAgent);
  const agentData = agentEntry?.data;

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

  useEffect(() => {
    const interval = setInterval(() => {
      setProcessorLineData((prev) => [
        ...prev.slice(-5),
        {
          name: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          value: agentData?.processor?.usage ?? 0,
        },
      ]);
      setMemoryLineData((prev) => [
        ...prev.slice(-5),
        {
          name: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          value: agentData?.memory?.percentage ?? 0,
        },
      ]);
    }, 2000);

    return () => clearInterval(interval);
  }, [agentData?.processor?.usage, agentData?.memory?.percentage]);

  // useEffect(() => {
  //   const interval = setInterval(() => {
  //     refetch(false);
  //   }, 10000);

  //   return () => clearInterval(interval);
  // }, []);

  useEffect(() => {
    if (agentData?.disk?.length && !selectedDisk) {
      setSelectedDisk(agentData.disk[0].device);
    }
  }, [agentData, selectedDisk]);


  const uploadValue = parseFloat(agentData?.network?.sent || 0);
  const downloadValue = parseFloat(agentData?.network?.received || 0);
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


  if (!selectedAgent) {
    return <SelectEndpointPopup setEndPointAgentName={setSelectedAgent} />;
  }

  const Endpointdetails = ({ endpointdet, endpointdetcss }) => {
    const currentDate = new Date().toLocaleString();

    // Extract the data object from the endpointdetail
    const data = endpointdet || {};

    return (
      <Document>
        <Page size="A4" style={endpointdetcss.page}>
          <View style={endpointdetcss.section}>
            <Image src="./apnalogo.png" style={endpointdetcss.logo} />
            {/* <Text style={endpointdetcss.title}>Endpoint Report of {selectedEndpoint} </Text>
              <Text style={endpointdetcss.date}>Generated As On: {currentDate}</Text> */}

            {/* Displaying Endpoint Details */}
            {/* <Text style={endpointdetcss.sectionTitleText}>Endpoint Details</Text> */}

            {/* System Information */}

            {

              <View>
                <Text style={endpointdetcss.title}>Endpoint Report of {data?.system?.name} </Text>
                <Text style={endpointdetcss.date}>Generated As On: {currentDate}</Text>
                <View style={endpointdetcss.sectionTitle}>
                  <Text style={endpointdetcss.sectionTitleText}>System Information</Text>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>System Name:</Text>
                    <Text style={endpointdetcss.value}>{data?.system?.name || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Manufacturer:</Text>
                    <Text style={endpointdetcss.value}>{data?.system?.manufacturer || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Architecture:</Text>
                    <Text style={endpointdetcss.value}>{data?.os?.architecture || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Model:</Text>
                    <Text style={endpointdetcss.value}>{data?.system?.model || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>OS:</Text>
                    <Text style={endpointdetcss.value}>
                      {data?.os?.name || 'N/A'} {data?.os?.version || 'N/A'}
                    </Text>
                  </View>
                </View>

                {/* Client Information */}
                <View style={endpointdetcss.sectionTitle}>
                  <Text style={endpointdetcss.sectionTitleText}>Endpoint Information</Text>
                  {/* <View style={endpointdetcss.row}>
                          <Text style={endpointdetcss.label}>Activation Date:</Text>
                          <Text style={endpointdetcss.value}>{data?.client_activation_date || 'N/A'}</Text>
                        </View> */}
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Version:</Text>
                    <Text style={endpointdetcss.value}>{data?.client_version || 'N/A'}</Text>
                  </View>
                  {/* <View style={endpointdetcss.row}>
                          <Text style={endpointdetcss.label}>Connected Nodes:</Text>
                          <Text style={endpointdetcss.value}>{data?.client_connected_nodes || 'n/a'}</Text>
                        </View> */}
                </View>

                {/* Network Information */}
                <View style={endpointdetcss.sectionTitle}>
                  <Text style={endpointdetcss.sectionTitleText}>Network Information</Text>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>IP Addresses:</Text>
                    <Text style={endpointdetcss.value}>{data?.ip_addresses || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>MAC Addresses:</Text>
                    <Text style={endpointdetcss.value}>{data?.mac_addresses || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Received:</Text>
                    <Text style={endpointdetcss.value}>{data?.network?.received || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Sent:</Text>
                    <Text style={endpointdetcss.value}>{data?.network?.sent || 'N/A'}</Text>
                  </View>
                </View>

                {/* Processor Information */}
                <View style={endpointdetcss.sectionTitle}>
                  <Text style={endpointdetcss.sectionTitleText}>Processor</Text>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Name:</Text>
                    <Text style={endpointdetcss.value}>{data?.processor?.name || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Logical Cores:</Text>
                    <Text style={endpointdetcss.value}>{data?.processor?.count || 'N/A'} Cores</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Physical Cores:</Text>
                    <Text style={endpointdetcss.value}>{data?.processor?.physical || 'N/A'} Cores</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>CPU Usage:</Text>
                    <Text style={endpointdetcss.value}>{data?.processor?.usage || 'N/A'}%</Text>
                  </View>
                </View>

                {/* Memory Information */}
                <View style={endpointdetcss.sectionTitle}>
                  <Text style={endpointdetcss.sectionTitleText}>Memory</Text>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Total:</Text>
                    <Text style={endpointdetcss.value}>{data?.memory?.total || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Used:</Text>
                    <Text style={endpointdetcss.value}>{data?.memory?.used || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Available:</Text>
                    <Text style={endpointdetcss.value}>{data?.memory?.available || 'N/A'}</Text>
                  </View>
                  <View style={endpointdetcss.row}>
                    <Text style={endpointdetcss.label}>Usage:</Text>
                    <Text style={endpointdetcss.value}>{data?.memory?.percentage || 'N/A'}%</Text>
                  </View>
                </View>

                <View style={endpointdetcss.sectionTitle}>
                  <Text style={endpointdetcss.sectionTitleText}>Disk Usage</Text>

                  {/* Header Row with single heading per column */}
                  <View style={endpointdetcss.tableRow}>
                    <View style={endpointdetcss.tableCell}>
                      <Text style={endpointdetcss.header}>Device</Text>
                    </View>
                    <View style={endpointdetcss.tableCell}>
                      <Text style={endpointdetcss.header}>Mountpoint</Text>
                    </View>
                    <View style={endpointdetcss.tableCell}>
                      <Text style={endpointdetcss.header}>Type</Text>
                    </View>
                    <View style={endpointdetcss.tableCell}>
                      <Text style={endpointdetcss.header}>Total</Text>
                    </View>
                    <View style={endpointdetcss.tableCell}>
                      <Text style={endpointdetcss.header}>Used</Text>
                    </View>
                    <View style={endpointdetcss.tableCell}>
                      <Text style={endpointdetcss.header}>Free</Text>
                    </View>
                    <View style={endpointdetcss.tableCell}>
                      <Text style={endpointdetcss.header}>Percent</Text>
                    </View>
                  </View>
                </View>
                {/* Mapping Disk Data and showing data in columns */}
                {data.disk?.length > 0 ? (
                  data.disk.map((disk, diskIndex) => (
                    <View key={diskIndex} style={endpointdetcss.tableRow}>
                      <View style={endpointdetcss.tableCell}>
                        <Text style={endpointdetcss.valuee}>{disk.device}</Text>
                      </View>
                      <View style={endpointdetcss.tableCell}>
                        <Text style={endpointdetcss.valuee}>{disk.mountpoint}</Text>
                      </View>
                      <View style={endpointdetcss.tableCell}>
                        <Text style={endpointdetcss.valuee}>{disk.type}</Text>
                      </View>
                      <View style={endpointdetcss.tableCell}>
                        <Text style={endpointdetcss.valuee}>{disk.total}</Text>
                      </View>
                      <View style={endpointdetcss.tableCell}>
                        <Text style={endpointdetcss.valuee}>{disk.used}</Text>
                      </View>
                      <View style={endpointdetcss.tableCell}>
                        <Text style={endpointdetcss.valuee}>{disk.free}</Text>
                      </View>
                      <View style={endpointdetcss.tableCell}>
                        <Text style={endpointdetcss.valuee}>{disk.percent}%</Text>
                      </View>
                    </View>
                  ))
                ) : (
                  <Text style={endpointdetcss.text}>No disk data available.</Text>
                )}

              </View>

            }
          </View>
        </Page>
      </Document>
    );
  };

  const Endpointdetcss = StyleSheet.create({
    page: {
      flexDirection: 'column',
      backgroundColor: '#FFFFFF',
      padding: 10,
      height: '100%',
      paddingVertical: 1,
    },
    networkColumn: {
      padding: 5,
      flex: 1,
    },
    networkRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
    },
    sectionSubtitleText: {
      fontSize: 12,
    },
    networkValue: {
      fontSize: 10,
      color: '#555',
      marginBottom: 5,
      textAlign: 'center',
    },
    section: {
      marginBottom: 15,
      flex: 1,
    },
    logo: {
      width: 120,
      height: 'auto',
      display: 'block',
      alignSelf: 'center',
      marginBottom: 5,
    },
    title: {
      fontSize: 16,
      textAlign: 'center',
      fontWeight: 'bold',
      color: '#007bff',
      marginBottom: 5,
      borderBottomWidth: 1,
      borderBottomColor: '#007bff',
      paddingBottom: 3,
    },
    date: {
      textAlign: 'center',
      fontSize: 10,
      color: '#777',
      marginTop: 2,
    },
    sectionTitle: {
      marginTop: 2,
      paddingVertical: 0,
    },
    sectionTitleText: {
      fontSize: 12,
      fontWeight: 'bold',
      color: '#333',
      backgroundColor: '#e7edf1',
      width: '100%',
      textAlign: 'center',
      paddingLeft: 5,
      paddingVertical: 3,
    },
    row: {
      flexDirection: 'row',
      marginBottom: 5,
      alignItems: 'center',
      marginTop: 5,
    },
    label: {
      width: '30%',
      fontWeight: 'bold',
      fontSize: 10,
      color: '#333',
      textAlign: 'left',
      marginLeft: 20,
    },
    value: {
      fontSize: 10,
      color: '#555',
      flex: 1,
      textAlign: 'center',
    },
    text: {
      fontSize: 10,
      color: '#555',
      marginBottom: 3,
      textAlign: 'center',
    },
    tableContainer: {
      borderWidth: 1,
      borderColor: '#ddd',
      borderRadius: 5,
      overflow: 'hidden',
      width: '100%',
      marginTop: 5,
    },
    tableHeader: {
      flexDirection: 'row',
      backgroundColor: '#f4f4f4',
      paddingVertical: 8,
      paddingHorizontal: 10,
      borderBottomWidth: 1,
      borderBottomColor: '#ddd',
    },
    tableHeaderText: {
      fontWeight: 'bold',
      fontSize: 12,
      color: '#333',
      textAlign: 'center',
      flex: 1,
    },
    tableRow: {
      flexDirection: 'row',
      paddingVertical: 8,
      paddingHorizontal: 10,
      borderBottomWidth: 1,
      borderBottomColor: '#ddd',
    },
    tableCell: {
      flex: 1,
      textAlign: 'center',
      fontSize: 10,
      color: '#555',
    },
    usageSection: {
      break: false,
    },

  });


  const handleDownloadPDF = async () => {
    const pdfBlob = await pdf(<Endpointdetails endpointdet={agentData} endpointdetcss={Endpointdetcss} />).toBlob();
    const url = URL.createObjectURL(pdfBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'specification_report.pdf';
    document.body.appendChild(link);
    link.click();
    const downloadEvent = `${agentData?.system?.name} Endpoint Specification Report PDF Download`;
    handleLogsSubmit(downloadEvent);
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

  }


  /**01/01 */
  const handleDownloadExcel = async () => {
    const wb = XLSX.utils.book_new();

    // Create a new array for the sheet data based on the `endpointdetail` data


    const sheetData = [];

    // Loop through the endpoint details
    const endpoint = agentData; // Assuming it's an object, not an array
    if (endpoint) {
      // Add Endpoint Information
      sheetData.push([`Endpoint Information - ${endpoint?.system?.name}`]);
      sheetData.push(["IP Address", "Last Connected", "Client Version", "Activation Date"]);
      sheetData.push([endpoint.ip_addresses, endpoint?.lastConnectedTime, endpoint?.client_version, endpoint?.client_activation_date || 'N/A']);
      sheetData.push([" "]);



      // Add System Information
      if (endpoint?.system) {
        sheetData.push(["System Information"]);
        sheetData.push(["Manufacturer", "Architecture", "Model", "System Name", "OS"]);
        sheetData.push([endpoint.system.manufacturer, endpoint.os.architecture, endpoint.system.model, endpoint.system.name, `${endpoint.os.name} ${endpoint.os.version}`]);
        sheetData.push([""]);

      }

      // Add Processor Information
      if (endpoint?.processor) {
        sheetData.push(["Processor"]);
        sheetData.push(["Logical Cores", "Physical Cores", "CPU Usage"]);
        sheetData.push([`${endpoint.processor?.count}Cores`, `${endpoint.processor?.physical}Cores`, `${endpoint.processor.usage}%`]);
        sheetData.push([""]);

      }

      // Add Memory Information
      if (endpoint?.memory) {
        sheetData.push(["Memory"]);
        sheetData.push(["Total", "Used", "Available", "Usage"]);
        sheetData.push([endpoint.memory.total, endpoint.memory.used, endpoint.memory.available, `${endpoint.memory.percentage}%`]);
        sheetData.push([""]);

      }

      // Add Disk Information
      if (endpoint?.disk && endpoint?.data?.disk?.length > 0) {
        sheetData.push(["Disk Usage"]);
        sheetData.push(["Device", "Mountpoint", "Type", "Total", "Used", "Free", "Percent"]);
        endpoint.data.disk.forEach(disk => {
          sheetData.push([disk.device, disk.mountpoint, disk.type, disk.total, disk.used, disk.free, disk.percent]);
        });
        sheetData.push([""]);

      }

      // Add IP Addresses
      if (endpoint?.data?.ip_addresses) {
        sheetData.push(["IP Addresses"]);
        endpoint.data.ip_addresses.split(", ").forEach(ip => {
          sheetData.push([ip]);
        });
        sheetData.push([""]);

      }

      // Add Network Usage
      if (endpoint?.data?.network) {
        sheetData.push(["Network Usage"]);
        sheetData.push(["Received", "Sent"]);
        sheetData.push([endpoint.data.network.received, endpoint.data.network.sent]);
        sheetData.push([""]);

      }

      // Add GPU Information
      if (endpoint?.data?.gpu) {
        sheetData.push(["GPU"]);
        sheetData.push(["GPU Name"]);
        sheetData.push([endpoint.data.gpu.name || "Not Detected"]);
        sheetData.push([""]);
      }
    };


    const endpointExcel = XLSX.utils.aoa_to_sheet(sheetData);
    endpointExcel["!cols"] = sheetData[1].map((_, colIndex) => ({
      wch: Math.max(...sheetData.map(row => (row[colIndex] ? row[colIndex].toString().length : 10))) + 5
    }));

    XLSX.utils.book_append_sheet(wb, endpointExcel, "Endpoint_Report");
    const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
    const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Client_report.xlsx`;
    document.body.appendChild(a);
    a.click();
    const downloadEvent = `${agentData?.system?.name} Endpoint Specification Report Excel Download`;
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
  //   return (
  //     <>
  //       <div className="flex items-center justify-center h-full">
  //         <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
  //           <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
  //             style={{ animation: 'oceanSlide 3s infinite' }} />
  //           <style>{`
  //     @keyframes oceanSlide {
  //       0% { transform: translateX(-150%); }
  //       66% { transform: translateX(0%); }
  //       100% { transform: translateX(150%); }
  //     }
  //   `}</style>
  //         </div>
  //       </div>
  //     </>
  //   );
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
      <div className="flex justify-between items-center mb-2">
        <span className="bg-yellow-200 text-black-100 text-sm rounded-lg p-2">
          🖥️ {selectedAgent}
        </span>
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
          <button
            onClick={() => setSelectedAgent(null)}
            className="text-white bg-blue-600 p-2 rounded-lg text-sm"
          >
            Change Endpoint
          </button>
        </div>
      </div>
      {/* Performance Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-2 mb-2">
        {/* CPU Usage */}
        <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-6 shadow-2xl border border-white border-opacity-20 hover:shadow-2xl transition-all duration-300">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                <Cpu className="w-3 h-3 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Processor Usage</p>
                <p className="text-sm font-bold text-gray-800">{agentData?.processor?.usage ?? 0}%</p>
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
                <p className="text-sm font-bold text-gray-800">{agentData?.memory?.percentage ?? 0}%</p>
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
                {agentData?.disk?.map((disk, index) => (
                  <option key={index} value={disk.device}>
                    {disk.device}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {agentData?.disk
            ?.filter((disk) => disk.device === selectedDisk)
            .map((disk, index) => {

              return (
                <div key={index} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-800">{disk.device}</h4>
                    <span className="text-sm text-gray-600">{disk.percent}% used</span>
                  </div>

                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full transition-all duration-500"
                      style={{ width: `${disk.percent}%` }}>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center p-2 bg-gray-50 rounded-lg">
                      <p className="text-gray-600">Total</p>
                      <p className="font-semibold text-gray-800">{disk.total}</p>
                    </div>
                    <div className="text-center p-2 bg-gray-50 rounded-lg">
                      <p className="text-gray-600">Used</p>
                      <p className="font-semibold text-gray-800">{disk.used}</p>
                    </div>
                    <div className="text-center p-2 bg-gray-50 rounded-lg">
                      <p className="text-gray-600">Free</p>
                      <p className="font-semibold text-gray-800">{disk.free}</p>
                    </div>
                  </div>
                </div>
              );
            })}
        </div>

        {/* Endpoint Information */}
        <div className="bg-white bg-opacity-70 backdrop-filter backdrop-blur-sm rounded-2xl p-2 shadow-2xl border border-white border-opacity-20">
          <div className="flex items-center space-x-3 mb-1">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg">
              <Monitor className="w-3 h-3 text-white" />
            </div>
            <h3 className="text-sm font-semibold text-gray-800">Endpoint Information</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-2 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-100 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center space-x-3 mb-2">
                <MonitorCheck className="w-3 h-3 text-blue-600" />
                <h6 className="text-sm font-semibold text-gray-800">Endpoint</h6>
              </div>
              <p className="text-xs text-gray-600 mb-1">{agentData?.system?.name}</p>
              <p className="text-xs text-gray-500">version {agentData?.client_version}</p>
            </div>

            <div className="p-2 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-100 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center space-x-3 mb-2">
                <Monitor className="w-3 h-3 text-green-600" />
                <h6 className="text-sm font-semibold text-gray-800">Operating System</h6>
              </div>
              <p className="text-xs text-gray-600 mb-1">{agentData?.os?.name}</p>
              <p className="text-xs text-gray-500">{`${agentData?.system?.manufacturer || ''} ${agentData?.system?.model || ''}`}</p>
            </div>

            <div className="p-2 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center space-x-3 mb-2">
                <Globe className="w-3 h-3 text-purple-600" />
                <h6 className="text-sm font-semibold text-gray-800">IP Addresses</h6>
              </div>
              <p className="text-xs text-gray-600 break-all">{agentData?.ip_addresses}</p>
            </div>

            <div className="p-2 bg-gradient-to-r from-yellow-50 to-red-50 rounded-xl border border-yellow-100 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center space-x-3 mb-2">
                <Wifi className="w-3 h-3 text-yellow-600" />
                <h6 className="text-sm font-semibold text-gray-800">MAC Addresses</h6>
              </div>
              <p className="text-xs text-gray-600 break-all">{agentData?.mac_addresses}</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default ClientReport;