import { useState, useEffect } from "react";
import useUserList from "../../Hooks/useUserList";
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../assets/pdf.png';
import XL from '../../assets/XLSD.png';
import config from "../../config";
import axios from "axios";
import CryptoJS from "crypto-js";
import useSaveLogs from "../../Hooks/useSaveLogs";
import axiosInstance from "../../axiosinstance";
import AlertComponent from "../../AlertComponent";
import LoadingComponent from "../../LoadingComponent";

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

const UserList = () => {
    const {
        filteredUsers,
        searchTerm,
        handleSearchChange,
        loading,
        error,
    } = useUserList();

    const [selectedReport, setSelectedReport] = useState('records');
    const [showLogsRep, setShowLogsRep] = useState(false);
    const [recorddata, SetRecordData] = useState({});
    const [allrecorddata, SetAllRecordData] = useState({});
    const [isPdfLoading, setIsPdfLoading] = useState(false);
    const [isExcelLoading, setIsExcelLoading] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [successRData, setSuccessRData] = useState([]); // Store successful job data
    const [failedJobs, setFailedJobs] = useState([]);
    const [successful, setSuccessful] = useState([]);
    const accessToken = localStorage.getItem("accessToken");
    const [alert, setAlert] = useState(null);

    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();

    const generateExcelReport = async (reportType) => {
        const wb = XLSX.utils.book_new(); // Create a new workbook

        const handleCreatedDate = (dateTime) => {
            let [date, time] = dateTime.split(" ");
            // Split the time part to remove seconds and milliseconds
            let [hours, minutes] = time.split(":");
            let newTime = `${hours}:${minutes}`;
            // Combine the date and new time
            let newDatetime = `${date} ${newTime}`;
            return newDatetime;
        };

        // Define awaited and unpairedAgents (replace this with real data)
        const awaited = {};  // This should be an object or array containing awaited agents
        const unpairedAgents = {};  // This should be an object or array containing unpaired agents

        // Function to validate IP address format (http://<IP>:<Port>)
        const isValidIpAddress = (ipAddress) => {
            const ipPattern = /^http:\/\/([0-9]{1,3}\.){3}[0-9]{1,3}:\d{1,5}$/;
            return ipPattern.test(ipAddress);
        };

        // Handle data for different report types
        if (reportType === 'records') {
            if (recorddata.length === 0) {
                setAlert({
                    message: "No data available for the Excel report.",
                    type: 'error'
                });
                return; // Stop further execution if no data is available
            }
            const rr = [];
            rr.push(["Email", "Last Login", "Last Logout"]); // Header row
            const sortedUsers = recorddata.sort((a, b) => new Date(b.login_timestamp) - new Date(a.login_timestamp));

            sortedUsers.forEach((job) => {
                rr.push([job.email, job.login_timestamp, job.logout_timestamp || "Not Logout"]);
            });
            const rData = XLSX.utils.aoa_to_sheet(rr);

            const headerStyle = { font: { bold: true }, alignment: { horizontal: "center" } };

            // Apply style to the header row
            for (let col = 0; col < rr[0].length; col++) {
                const cell = rData[XLSX.utils.encode_cell({ r: 0, c: col })];
                if (cell) {
                    cell.s = headerStyle;
                }
            }

            // Set column widths (example: for 4 columns)
            rData["!cols"] = [
                { wpx: 200 }, // Job Name column width
                { wpx: 200 }, // Created Time column width
                { wpx: 200 }, // Executed Time column width

            ];

            XLSX.utils.book_append_sheet(wb, rData, "UserLogs_Report");
        }
        else if (reportType === 'allrecords') {
            if (allrecorddata.length === 0) {
                setAlert({
                    message: "No data available for the Excel report.",
                    type: 'error'
                });
                return; // Stop further execution if no data is available
            }
            const rr = [];
            const sortedUsers = allrecorddata.sort((a, b) => new Date(b.login_timestamp) - new Date(a.login_timestamp));

            rr.push(["Email", "Last Login", "Last Logout"]); // Header row
            sortedUsers.forEach((job) => {
                rr.push([job.email, job.login_timestamp, job.logout_timestamp || "Not Logout"]);
            });
            const rData = XLSX.utils.aoa_to_sheet(rr);

            const headerStyle = { font: { bold: true }, alignment: { horizontal: "center" } };

            // Apply style to the header row
            for (let col = 0; col < rr[0].length; col++) {
                const cell = rData[XLSX.utils.encode_cell({ r: 0, c: col })];
                if (cell) {
                    cell.s = headerStyle;
                }
            }

            // Set column widths (example: for 4 columns)
            rData["!cols"] = [
                { wpx: 200 }, // Job Name column width
                { wpx: 200 }, // Created Time column width
                { wpx: 200 }, // Executed Time column width

            ];

            XLSX.utils.book_append_sheet(wb, rData, "All_UsersLogs_Report");
        }



        else {
            return;
        }

        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
        const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${reportType}_report.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = `${reportType}_report Excel Download`;
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };


    const styles = StyleSheet.create({
        page: {
            flexDirection: 'column',
            backgroundColor: '#FFFFFF',
            padding: 20,
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
            alignSelf: 'center',  // Center the logo horizontally
            marginBottom: 10,  // Some space below the logo
        },
        sectionHeader: {
            fontSize: 16,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#007bff',
            marginBottom: 5,
            borderBottomWidth: 2, // Border under the section title for visual separation
            borderBottomColor: '#007bff', // Blue color for the border
            paddingBottom: 5,
        },

        table: {
            display: 'table',
            width: '100%',
            borderWidth: 1, // Border for the entire table
            borderColor: '#e9f0f9', // Blue border color for the table
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
        },
        tableRow: {
            flexDirection: 'row',
        },
        tableCell: {
            padding: 10,
            textAlign: 'center',  // Horizontally centers the text
            width: '25%',  // Ensures that each column takes up equal width
            fontSize: 8,
            wordWrap: 'break-word',  // Allows the word wrapping
            overflowWrap: 'break-word',  // Breaks long words and wraps
            whiteSpace: 'normal',  // Ensures wrapping in PDF
            verticalAlign: 'middle',  // Vertically centers the text
            height: '20px',
            display: 'flex',  // Enables Flexbox for centering
            alignItems: 'center',  // Vertically centers the text
            justifyContent: 'center',  // Horizontally centers the text
        },
        date: {
            fontSize: 12,
            color: '#777',
            textAlign: 'center',
            marginBottom: 5,
        },
        repoImage: {
            maxWidth: '18%',  // Ensure images fit within the cell
            height: 'auto',
        },
        jobNameCell: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 8,
            wordWrap: 'break-word',  // Allow word wrapping for job names
            overflowWrap: 'break-word',  // Ensure long words break and wrap
            whiteSpace: 'normal', // Make sure it wraps text correctly
            verticalAlign: 'top',  // Aligns text at the top of the cell
            display: 'flex',
            flexDirection: 'column',
        },
        locationCell: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 8,
            wordWrap: 'break-word',  // Allow word wrapping for location
            overflowWrap: 'break-word',  // Ensure long words break and wrap
            whiteSpace: 'normal', // Make sure it wraps text correctly
            verticalAlign: 'top',  // Aligns text at the top of the cell
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

    const Alllogs = ({ allLogin }) => {
        const currentDate = new Date().toLocaleString(); // Get the current date
        const sortedUsers = allLogin.sort((a, b) => new Date(b.login_timestamp) - new Date(a.login_timestamp));

        return (
            <Document>
                <Page size="A4" style={styles.page}>
                    <Image src="./apnalogo.png" style={styles.centeredLogo} />

                    {/* Unified Heading */}
                    <Text style={styles.sectionHeader}>All Users Logs</Text>
                    <Text style={styles.date}>Generated As On: {currentDate}</Text>

                    {/* Table Section */}
                    <View style={styles.table}>
                        {/* Table Header */}
                        <View style={styles.tableHeaderRow}>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Sr. No.</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Email</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Login Ip Address</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Last Login</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Last Logout</Text>
                        </View>

                        {(
                            sortedUsers.map((user, index) => {
                                const isEvenRow = index % 2 === 0;
                                return (
                                    <View
                                        key={index}
                                        style={[
                                            styles.tableRow,
                                            { backgroundColor: isEvenRow ? '#f5f7fc' : '#ffffff' },
                                        ]}
                                    >
                                        <Text style={[styles.tableCell, styles.borderRight]}>{index + 1}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.email}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.login_ip_name}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.login_timestamp}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.logout_timestamp || "Not Logout"}</Text>
                                    </View>
                                );
                            })
                        )}
                    </View>
                </Page>
            </Document>
        );
    };



    const Login = ({ }) => {
        const currentDate = new Date().toLocaleString(); // Get the current date
        const sortedUsers = recorddata.sort((a, b) => new Date(b.login_timestamp) - new Date(a.login_timestamp));

        const styles = StyleSheet.create({
            page: {
                flexDirection: 'column',
                backgroundColor: '#FFFFFF',
                padding: 20,
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
                alignSelf: 'center',  // Center the logo horizontally
                marginBottom: 10,  // Some space below the logo
            },
            sectionHeader: {
                fontSize: 16,
                textAlign: 'center',
                fontWeight: 'bold',
                color: '#007bff',
                marginBottom: 5,
                borderBottomWidth: 2, // Border under the section title for visual separation
                borderBottomColor: '#007bff', // Blue color for the border
                paddingBottom: 5,
            },

            table: {
                display: 'table',
                width: '100%',
                borderWidth: 1, // Border for the entire table
                borderColor: '#e9f0f9', // Blue border color for the table
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
            },
            tableRow: {
                flexDirection: 'row',
            },
            tableCell: {
                padding: 10,
                textAlign: 'center',  // Horizontally centers the text
                width: '25%',  // Ensures that each column takes up equal width
                fontSize: 8,
                wordWrap: 'break-word',  // Allows the word wrapping
                overflowWrap: 'break-word',  // Breaks long words and wraps
                whiteSpace: 'normal',  // Ensures wrapping in PDF
                verticalAlign: 'middle',  // Vertically centers the text
                height: '20px',
                display: 'flex',  // Enables Flexbox for centering
                alignItems: 'center',  // Vertically centers the text
                justifyContent: 'center',  // Horizontally centers the text
            },
            date: {
                fontSize: 12,
                color: '#777',
                textAlign: 'center',
                marginBottom: 5,
            },
            repoImage: {
                maxWidth: '18%',  // Ensure images fit within the cell
                height: 'auto',
            },
            jobNameCell: {
                padding: 10,
                textAlign: 'center',
                width: '25%',
                fontSize: 8,
                wordWrap: 'break-word',  // Allow word wrapping for job names
                overflowWrap: 'break-word',  // Ensure long words break and wrap
                whiteSpace: 'normal', // Make sure it wraps text correctly
                verticalAlign: 'top',  // Aligns text at the top of the cell
                display: 'flex',
                flexDirection: 'column',
            },
            locationCell: {
                padding: 10,
                textAlign: 'center',
                width: '25%',
                fontSize: 8,
                wordWrap: 'break-word',  // Allow word wrapping for location
                overflowWrap: 'break-word',  // Ensure long words break and wrap
                whiteSpace: 'normal', // Make sure it wraps text correctly
                verticalAlign: 'top',  // Aligns text at the top of the cell
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

        return (
            <Document>
                <Page size="A4" style={styles.page}>
                    <Image src="./apnalogo.png" style={styles.centeredLogo} />

                    {/* Unified Heading */}
                    <Text style={styles.sectionHeader}>User Logs</Text>
                    <Text style={styles.date}>Generated As On: {currentDate}</Text>

                    {/* Table Section */}
                    <View style={styles.table}>
                        {/* Table Header */}
                        <View style={styles.tableHeaderRow}>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Sr. No.</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Email</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Login Ip Address</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Last Login</Text>
                            <Text style={[styles.tableHeader, styles.borderRight]}>Last Logout</Text>
                        </View>

                        {/* Render User Data */}
                        {/* {Array.isArray(recorddata) && recorddata.length > 0 ? (
                  recorddata.map((user, index) => {
                    const isEvenRow = index % 2 === 0;
                    return (
                      <View
                        key={index}
                        style={[
                          styles.tableRow,
                          { backgroundColor: isEvenRow ? '#f5f7fc' : '#ffffff' },
                        ]}
                      >
                        <Text style={[styles.tableCell, styles.borderRight]}>{index + 1}</Text>
                        <Text style={[styles.tableCell, styles.borderRight]}>{user.email}</Text>
                        <Text style={[styles.tableCell, styles.borderRight]}>{user.login_timestamp}</Text>
                      </View>
                    );
                  })
                ) : (
                  <Text style={{ padding: 5 }}>No users available</Text>
                )} */}
                        {(
                            sortedUsers.map((user, index) => {
                                const isEvenRow = index % 2 === 0;
                                return (
                                    <View
                                        key={index}
                                        style={[
                                            styles.tableRow,
                                            { backgroundColor: isEvenRow ? '#f5f7fc' : '#ffffff' },
                                        ]}
                                    >
                                        <Text style={[styles.tableCell, styles.borderRight]}>{index + 1}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.email}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.login_ip_name}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.login_timestamp}</Text>
                                        <Text style={[styles.tableCell, styles.borderRight]}>{user.logout_timestamp || "Not Logout"}</Text>
                                    </View>
                                );
                            })
                        )}
                    </View>
                </Page>
            </Document>
        );
    };

    const MyUsers = ({ users }) => {
        const currentDate = new Date().toLocaleString(); // Get the current date

        const handleCreatedDate = (dateTime) => {
            let [date, time] = dateTime.split(" ");
            // Split the time part to remove seconds and milliseconds
            let [hours, minutes] = time.split(":");
            let newTime = `${hours}:${minutes}`;

            // Combine the date and new time
            let newDatetime = `${date} ${newTime}`;
            return newDatetime;
        };

        return (
            <Document>
                <Page size="A4" style={user.page}>
                    <Image src="./apnalogo.png" style={user.centeredLogo} />
                    <Text style={user.sectionHeader}>Application UserList</Text>
                    <Text style={user.date}>Generated As On: {currentDate}</Text>
                    <View style={user.table}>
                        <View style={user.tableHeaderRow}>
                            <Text style={[user.tableHeader, user.borderRight]}>Sr. No.</Text>

                            <Text style={[user.tableHeader, user.borderRight]}>First Name</Text>
                            <Text style={[user.tableHeader, user.borderRight]}>Last Name</Text>
                            <Text style={[user.tableHeader, user.borderRight]}>Email</Text>
                            <Text style={[user.tableHeader, user.borderRight]}>Mobile Number</Text>
                            <Text style={[user.tableHeader, user.borderRight]}>Designation</Text>
                            <Text style={user.tableHeader}>Created Time</Text>
                        </View>
                        {Array.isArray(users) && users.length > 0 ? (
                            users.map((userr, index) => {
                                const isEvenRow = index % 2 === 0;
                                return (
                                    <View
                                        key={index}
                                        style={[
                                            user.tableRow,
                                            { backgroundColor: isEvenRow ? '#f5f7fc' : '#ffffff' },
                                        ]}
                                    >
                                        <Text style={[user.tableCell, user.borderRight]}>{index + 1}</Text>

                                        <Text style={[user.tableCell, user.borderRight]}>{userr.name}</Text>
                                        <Text style={[user.tableCell, user.borderRight]}>{userr.lname}</Text>
                                        <Text style={[user.tableCell, user.borderRight]}>{userr.email}</Text>
                                        <Text style={[user.tableCell, user.borderRight]}>{userr.mobileNumber}</Text>
                                        <Text style={[user.tableCell, user.borderRight]}>{userr.designation}</Text>
                                        <Text style={user.tableCell}>{handleCreatedDate(userr.createdTime)}</Text>
                                    </View>
                                );
                            })
                        ) : (
                            <Text style={{ padding: 5 }}>No users available</Text>
                        )}
                    </View>
                </Page>
            </Document>
        );
    };

    const user = StyleSheet.create({
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
            display: 'block', // Ensures the logo behaves like a block-level element
            marginLeft: 'auto', // Centers the logo horizontally
            marginRight: 'auto', // Centers the logo horizontally
            marginBottom: 10,
        },


        sectionHeader: {
            fontSize: 16,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#007bff',
            marginBottom: 2,
            borderBottomWidth: 2, // Border under the section title for visual separation
            borderBottomColor: '#007bff', // Blue color for the border
            marginTop: -5,
            paddingBottom: 5,
        },

        table: {
            display: 'table',
            width: '100%',
            borderWidth: 1, // Border for the entire table
            borderColor: '#e9f0f9', // Blue border color for the table
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
            width: '25%',  // Ensures that each column takes up equal width
            fontSize: 8,
            wordWrap: 'break-word', // Allows the word wrapping
            overflowWrap: 'break-word', // Breaks long words and wraps
            whiteSpace: 'normal', // Ensures wrapping in PDF
            verticalAlign: 'top', // Aligns the text at the top of the cell
            display: 'flex',
            flexDirection: 'column',
            height: '50px',
            alignItems: 'center',
        },
        date: {
            textAlign: 'center', // Centering date text
            fontSize: 12,
            color: '#777',
            marginTop: 2,
            marginBottom: 5,
            marginTop: 5,
        },
        repoImage: {
            maxWidth: '18%',  // Ensure images fit within the cell
            height: 'auto',
        },
        jobNameCell: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 8,
            wordWrap: 'break-word',  // Allow word wrapping for job names
            overflowWrap: 'break-word',  // Ensure long words break and wrap
            whiteSpace: 'normal', // Make sure it wraps text correctly
            verticalAlign: 'top',  // Aligns text at the top of the cell
            display: 'flex',
            flexDirection: 'column',
        },
        locationCell: {
            padding: 10,
            textAlign: 'center',
            width: '25%',
            fontSize: 8,
            wordWrap: 'break-word',  // Allow word wrapping for location
            overflowWrap: 'break-word',  // Ensure long words break and wrap
            whiteSpace: 'normal', // Make sure it wraps text correctly
            verticalAlign: 'top',  // Aligns text at the top of the cell
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


    /**31st */
    const handleDownloadPDF = async () => {
        const pdfBlob = await pdf(<MyUsers users={filteredUsers} />).toBlob();
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'users_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = `Users report PDF Download`;
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }


    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();

        const handleCreatedDate = (dateTime) => {
            if (!dateTime) return "";
            let [date, time] = dateTime.split(" ");
            if (!time) return date;
            let [hours, minutes] = time.split(":");
            return `${date} ${hours}:${minutes}`;
        };

        const wsDataUsers = [];
        wsDataUsers.push([
            "Sr. No.", "First Name", "Last Name", "Email",
            "Mobile Number", "Designation", "Created time"
        ]);

        if (Array.isArray(filteredUsers) && filteredUsers.length > 0) {
            filteredUsers.forEach((user, index) => {
                wsDataUsers.push([
                    index + 1,
                    user.name || "",
                    user.lname || "",
                    user.email || "",
                    user.mobileNumber || "",
                    user.designation || "",
                    handleCreatedDate(user.createdTime)
                ]);
            });
        } else {
            // Add "No Data Available" row
            wsDataUsers.push(["", "No Data Available", "", "", "", "", ""]);
        }

        const wsUsers = XLSX.utils.aoa_to_sheet(wsDataUsers);

        const headerCellStyle = {
            font: { bold: true, color: { rgb: "FFFFFF" } },
            fill: { fgColor: { rgb: "4F81BD" } },
            alignment: { horizontal: "center", vertical: "center" },
            border: {
                top: { style: "thin", color: { rgb: "ffffff" } },
                bottom: { style: "thin", color: { rgb: "000000" } },
                left: { style: "thin", color: { rgb: "000000" } },
                right: { style: "thin", color: { rgb: "000000" } },
            },
        };

        const range = XLSX.utils.decode_range(wsUsers["!ref"]);
        for (let col = range.s.c; col <= range.e.c; col++) {
            const cellRef = XLSX.utils.encode_cell({ r: 0, c: col });
            if (wsUsers[cellRef]) {
                wsUsers[cellRef].s = headerCellStyle;
            }
        }

        wsUsers["!cols"] = [
            { wpx: 100 }, { wpx: 100 }, { wpx: 100 },
            { wpx: 200 }, { wpx: 100 }, { wpx: 100 }, { wpx: 100 },
        ];

        XLSX.utils.book_append_sheet(wb, wsUsers, "Users Report");
        const downloadEvent = "Users Report Excel Download";
        handleLogsSubmit(downloadEvent);
        XLSX.writeFile(wb, "Users_Report.xlsx");
    };


    function s2ab(str) {
        const buf = new ArrayBuffer(str.length);
        const view = new Uint8Array(buf);
        for (let i = 0; i < str.length; i++) {
            view[i] = str.charCodeAt(i) & 0xFF;
        }
        return buf;
    }


    const handleDownload = async (type) => {
        try {
            if (type === 'pdf') setIsPdfLoading(true);
            else if (type === 'excel') setIsExcelLoading(true);

            // Ensure the latest data is fetched before generating the report
            await handleSearch();

            // Use a slight delay to allow state updates to process if needed, though direct passing is better
            await new Promise(resolve => setTimeout(resolve, 100));


            if (type === 'pdf') {
                if (selectedReport === 'records') {
                    if (recorddata.length === 0) {
                        setAlert({
                            message: "No data available for the PDF report.",
                            type: 'error'
                        });
                        return;
                    }
                    const pdfBlob = await pdf(<Login Login={recorddata} />).toBlob();
                    const url = URL.createObjectURL(pdfBlob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'UserLogs_report.pdf';
                    link.click();
                    const downloadEvent = `UserLogs report PDF Download`;
                    handleLogsSubmit(downloadEvent);
                    URL.revokeObjectURL(url);
                } else if (selectedReport === 'allrecords') {
                    if (allrecorddata.length === 0) {
                        setAlert({
                            message: "No data available for the PDF report.",
                            type: 'error'
                        });
                        return;
                    }
                    const pdfBlob = await pdf(<Alllogs allLogin={allrecorddata} />).toBlob();
                    const url = URL.createObjectURL(pdfBlob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'All_UsersLogs_report.pdf';
                    link.click();
                    const downloadEvent = `All UsersLogs report PDF Download`;
                    handleLogsSubmit(downloadEvent);
                    URL.revokeObjectURL(url);
                }
            } else if (type === 'excel') {
                if (selectedReport === 'records') {
                    await generateExcelReport('records', recorddata);
                } else if (selectedReport === 'allrecords') {
                    await generateExcelReport('allrecords', allrecorddata);
                }
            }
        } catch (error) {
            console.error('Failed to generate the report:', error);
            setAlert({
                message: "Failed to generate the report. Please try again later.",
                type: 'error'
            });
        } finally {
            if (type === 'pdf') setIsPdfLoading(false);
            else if (type === 'excel') setIsExcelLoading(false);
        }
    };

    const handleSearch = async () => {
        if (selectedReport === 'records') {
            const email = decryptData(localStorage.getItem("adminn"));

            const userData = decryptData(localStorage.getItem("user_email"));
            try {
                const response = await axiosInstance.post(`${config.API.FLASK_URL}/get-records`, {
                    email: email || userData
                }, {
                    headers: {
                        'Content-Type': 'application/json',
                        token: accessToken,
                    },
                });
                // Directly set the data from the response
                SetRecordData(response.data);
            } catch (error) {
                console.error("Failed to fetch records:", error);
                SetRecordData([]); // Clear data on error
            }
        } else if (selectedReport === 'allrecords') {
            try {
                const response = await axiosInstance.post(`${config.API.FLASK_URL}/get-records`, {
                    email: "all"
                }, {
                    headers: {
                        'Content-Type': 'application/json',
                        token: accessToken,
                    },
                });
                // Directly set the data from the response
                SetAllRecordData(response.data);
            } catch (error) {
                console.error("Failed to fetch all records:", error);
                SetAllRecordData([]); // Clear data on error
            }
        }
    };

    useEffect(() => {
        if (selectedReport) {
            handleSearch();
        }
    }, [selectedReport]);


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
                        placeholder="Search for users"
                        value={searchTerm}
                        onChange={handleSearchChange}
                    />
                </div>

                <div className="flex items-center space-x-2">

                    <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                    <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />

                    <button
                        onClick={() => setShowLogsRep(true)}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        Logs
                    </button>
                </div>
            </div>

            <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                    <tr>
                        <th scope="col" className="px-2 py-2">
                            User
                        </th>
                        <th scope="col" className="px-2 py-2">
                            Designation
                        </th>
                        <th scope="col" className="px-2 py-2">
                            Mobile
                        </th>
                        <th scope="col" className="px-2 py-2">
                            Created At
                        </th>
                        <th scope="col" className="px-2 py-2">
                            Modified At
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {filteredUsers.length > 0 ? (
                        filteredUsers.map((user, index) => (
                            <tr key={user.id || index} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-200">
                                <th scope="row" className="flex items-center gap-5 px-2 py-2 text-gray-900 whitespace-nowrap dark:text-white">
                                    {user.profilePhoto && user.profilePhoto.startsWith('data:image') ? (
                                        <img
                                            className="w-10 h-10 rounded-full object-cover"
                                            src={user.profilePhoto}
                                        />
                                    ) : (
                                        <div className="w-10 h-10 rounded-full flex items-center justify-center bg-blue-600 text-white font-bold text-lg uppercase">
                                            {user.name && user.name.charAt(0)}{user.lname && user.lname.charAt(0)}
                                        </div>
                                    )}
                                    <div className="ps-3">
                                        <div className="text-base font-semibold">{user.name} {user.lname}</div>
                                        <div className="font-normal text-gray-500">{user.email}</div>
                                    </div>
                                </th>
                                <td className="px-2 py-2">
                                    {user.designation}
                                </td>
                                <td className="px-2 py-2">
                                    {user.mobileNumber}
                                </td>
                                <td className="px-2 py-2">
                                    {new Date(user.createdTime).toLocaleString()}
                                </td>
                                <td className="px-2 py-2">
                                    {new Date(user.modifyTime).toLocaleString()}
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="5" className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                                {searchTerm ? 'No users found matching your search.' : 'No users available.'}
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
            {showLogsRep && (
                <div className="Filter-popup-overlay">
                    <div className="Filter-popup-content">
                        <span className='close-Filter' onClick={() => setShowLogsRep(false)}>X</span>
                        <h2>Logs Report</h2>
                        <div className="filter-container">
                            <div className="status-filter">

                                <select
                                    value={selectedReport}
                                    onChange={(e) => {
                                        setSelectedReport(e.target.value); // Update selected report
                                        handleSearch(); // Trigger the data fetch
                                    }}
                                    className="status-dropdown"
                                >
                                    <option value="records">User Logs</option>
                                    <option value="allrecords">All Users Logs</option>
                                </select>
                            </div>
                        </div>

                        {!["records", "allrecords"].includes(selectedReport) && (
                            <>
                                {/* <div className="tool-bar">
                                          <div className="date-picker">
                                            <label>From Date</label>
                                            <input
                                              className="date-input"
                                              type="datetime-local"
                                              value={fromDate}
                                              onChange={(e) => setFromDate(e.target.value)}
                                              onBlur={() => document.activeElement.blur()} // Closes the datetime picker when it loses focus
                                              max={new Date().toISOString().slice(0, 16)} // Can't select future dates
                                            />
                                          </div>

                                          <div className="date-picker">
                                            <label>To Date</label>
                                            <input
                                              className="date-input"
                                              type="datetime-local"
                                              value={toDate}
                                              onChange={(e) => setToDate(e.target.value)}
                                              onBlur={() => document.activeElement.blur()} // Closes the datetime picker when it loses focus
                                              min={fromDate} // Can't select dates before "From Date"
                                              max={new Date().toISOString().slice(0, 16)} // Can't select future dates
                                            />
                                          </div>
                                        </div> */}
                            </>
                        )}



                        <div className="button-group">
                            <button className="Filter-close" onClick={() => handleDownload('pdf')}
                                disabled={isPdfLoading || selectedReport === ""}>{isPdfLoading ? (
                                    <div className="spinner"></div>  // Add your spinner component or CSS here
                                ) : (
                                    'PDF'
                                )}
                                <img width={20} src={PDF} /></button>
                            <button className="apply-btn" onClick={() => handleDownload('excel')}
                                disabled={isExcelLoading || selectedReport === ""}>
                                <img width={20} src="./excel.jpg" />
                                {isExcelLoading ? (
                                    <div className="spinner"></div>  // Add your spinner component or CSS here
                                ) : (
                                    'Excel'
                                )}</button>
                        </div>
                    </div>
                </div>
            )}
            {alert && (
                <AlertComponent
                    message={alert.message}
                    type={alert.type}
                    onClose={() => setAlert(null)}
                />
            )}
        </div>
    );
};

export default UserList;