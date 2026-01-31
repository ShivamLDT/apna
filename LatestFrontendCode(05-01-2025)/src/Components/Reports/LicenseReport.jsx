import { useState, useEffect, useContext, useRef } from 'react';
import { Backupindex } from '../../Context/Backupindex';
import config from '../../config';
import {
    CheckCircle,
    User,
    Briefcase,
    Mail,
    Phone,
    Calendar,
    Monitor,
    Users,
    Clock,
    Shield
} from 'lucide-react';
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from "@react-pdf/renderer";
import { pdf } from '@react-pdf/renderer';
import * as XLSX from "xlsx";
import PDF from '../../assets/pdf.png';
import XL from '../../assets/XLSD.png';
import useSaveLogs from '../../Hooks/useSaveLogs';
import { ToastContainer, toast } from 'react-toastify';
import { useToast } from '../../ToastProvider';
import axios from "axios";
import axiosInstance from '../../axiosinstance';
import { sendNotification } from '../../Hooks/useNotification';
import { NotificationContext } from "../../Context/NotificationContext";
import AlertComponent from '../../AlertComponent';
import LoadingComponent from '../../LoadingComponent';
const LicenseReport = () => {

    const { setNotificationData } = useContext(NotificationContext)
    const [error, setError] = useState(null);
    const { showToast } = useToast();
    const [loading, setLoading] = useState(false);
    const hasNotifiedRef = useRef(false);
    const [alert, setAlert] = useState(null);
    const [registrationInfo, setRegistrationInfo] = useState({
        organizationName: '',
        status: '',
        designation: '',
        mobile: '',
        lastLogin: '',
        email: '',
    });

    const [licenseData, setLicenseData] = useState({
        activationDate: '',
        endpointLimit: 0,
        userLimit: 0,
        validityDays: 0,
        remainingDays: 'N/A',
        licenseExpiry: '',
    });


    useEffect(() => {
        if (licenseData?.remainingDays === 0 && !hasNotifiedRef.current) {
            hasNotifiedRef.current = true;

            const Notification_local_Data = {
                id: Date.now(),
                message: `⚠️ Your license will expires today.`,
                timestamp: new Date(),
                isRead: false,
            };

            sendNotification(Notification_local_Data.message);
            showToast("Your license will expires today.", "warning");
            setNotificationData((prev) => [...prev, Notification_local_Data]);
        }
    }, [licenseData]);

    const InfoCard = ({ icon: Icon, title, value, color = 'gray' }) => (
        <div className="bg-white border border-gray-200 rounded-lg p-2">
            <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${color === 'green' ? 'bg-green-100' :
                    color === 'blue' ? 'bg-blue-100' :
                        color === 'purple' ? 'bg-purple-100' :
                            color === 'orange' ? 'bg-yellow-100' :
                                'bg-gray-100'
                    }`}>
                    <Icon className={`h-5 w-5 ${color === 'green' ? 'text-green-600' :
                        color === 'blue' ? 'text-blue-600' :
                            color === 'purple' ? 'text-purple-600' :
                                color === 'orange' ? 'text-yellow-600' :
                                    'text-gray-600'
                        }`} />
                </div>
                <div>
                    <p className="text-sm text-gray-600">{title}</p>
                    <p className="text-sm font-semibold text-gray-900">{value}</p>
                </div>
            </div>
        </div>
    );

    const Section = ({ title, children }) => (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">{title}</h2>
            {children}
        </div>
    );


    const accessToken = localStorage.getItem('AccessToken');

    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();


    const fetchLicenseData = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/sync`, {}, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken,
                },
            });

            setLoading(false);
            const { data } = response.data;

            const org = data.organization_details;
            const activationDate = new Date(org.timestamp).toLocaleString();
            const licenseExpiry = new Date(org.expiry).toLocaleString();
            const remainingDays = Math.max(
                0,
                Math.floor((new Date(org.expiry) - new Date()) / (24 * 60 * 60 * 1000))
            );

            setLicenseData({
                activationDate,
                endpointLimit: org.limit_of_agents,
                userLimit: org.limit_of_users,
                validityDays: org.limit_of_days,
                remainingDays,
                licenseExpiry,
            });

            const reg = data.organization_details;

            setRegistrationInfo({
                firstName: data?.first_name,
                lastName: data?.last_name,
                organizationName: reg.name,
                status: data.status,
                designation: data.designation,
                mobile: data.mobile,
                lastLogin: new Date(data.last_login).toLocaleString(),
                email: data.email,
            });

        } catch (err) {
            console.error('Fetch failed:', err);
            setError('Failed to fetch license information. Please try again later.');
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!userRole) return;

        if (userRole.toLowerCase() === "employee") {
            setAlert({
                message: "You do not have permission to access this section.",
                type: "error"
            });
            return;
        }

        fetchLicenseData();
    }, [userRole]);


    function LicensePDF({ license }) {
        const currentDate = new Date().toLocaleString(); // Get the current date  

        function convertLocalTime(ISOstring) {
            const date = new Date(ISOstring);
            const localdate = date.toLocaleString();
            return localdate;
        }

        const calculateRemainingDays = (expiryDate) => {
            const currentDate = new Date();
            const expiry = new Date(expiryDate);
            const timeDifference = expiry - currentDate;

            if (timeDifference <= 0) {
                return 0;
            }

            const daysRemaining = Math.ceil(timeDifference / (1000 * 3600 * 24));
            return daysRemaining;
        };

        return (
            <Document>
                <Page size="A4" style={licStyles.page}>
                    <Image src="./ablogo.png" style={licStyles.centeredLogo} />

                    <Text style={licStyles.sectionHeader}>License Report</Text>
                    <Text style={licStyles.date}>Generated At: {currentDate}</Text>

                    <View style={licStyles.textContainer}>
                        {/* Admin Information Section */}
                        <View style={licStyles.column}>
                            <Text style={licStyles.tableHeaderMain}>Registration Information</Text>
                            {Array.isArray(license) && license.length > 0 ? (
                                license.map((licData, index) => (
                                    <View key={index}>
                                        <Text style={licStyles.textItem}> Name: {licData.firstName} {licData.lastName}</Text>
                                        {licData.STATUS && (
                                            <Image style={licStyles.image} source={{ uri: licData.STATUS }} />
                                        )}

                                        <Text style={licStyles.textItem}>Designation: {licData.designation}</Text>
                                        <Text style={licStyles.textItem}>Mobile Number: {licData.mobile}</Text>
                                        <Text style={licStyles.textItem}>Email: {licData.email}</Text>
                                        <Text style={licStyles.textItem}>Last Login: {licData.lastLogin}</Text>
                                        <View style={licStyles.separator} />
                                    </View>
                                ))
                            ) : (
                                <Text style={licStyles.noDataText}>No users available</Text>
                            )}
                        </View>

                        {/* License Information Section */}
                        <View style={licStyles.column2}>
                            <Text style={licStyles.tableHeaderMain}>License Information</Text>
                            {Array.isArray(license) && license.length > 0 ? (
                                license.map((licData, index) => (
                                    <View key={index}>
                                        <Text style={licStyles.textItem}>Status: {licData.status}</Text>
                                        <Text style={licStyles.textItem}>Agent/Endpoint Limit: {licData.organization_details.endpointLimit}</Text>
                                        <Text style={licStyles.textItem}>Application User Limit: {licData.organization_details.userLimit}</Text>
                                        <Text style={licStyles.textItem}>Validity in Days: {licData.organization_details.validityDays}</Text>
                                        <Text style={licStyles.textItem}>License Expiry: {licData.organization_details.licenseExpiry}</Text>
                                        <View style={licStyles.separator} />
                                    </View>
                                ))
                            ) : (
                                <Text style={licStyles.noDataText}>No users available</Text>
                            )}
                        </View>
                    </View>
                </Page>
            </Document>
        );
    }


    const licStyles = StyleSheet.create({
        page: {
            display: 'flex',
            flexDirection: 'column',
            padding: 20,
            backgroundColor: '#f4f5f7',
        },

        centeredLogo: {
            width: 120,
            height: 'auto',
            alignSelf: 'center',
            marginBottom: 20,
        },

        sectionHeader: {
            fontSize: 22,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#007bff',
            marginBottom: 20,



            borderBottomWidth: 2,
            borderBottomColor: '#007bff',
            paddingBottom: 10,
        },

        date: {
            fontSize: 12,
            color: '#888',
            textAlign: 'center',
            marginBottom: 30,

        },

        textContainer: {
            marginTop: 30,
            display: 'flex',
            flexDirection: 'column',
            gap: 30, // Spacing between sections
        },

        column: {
            display: 'flex',
            flexDirection: 'column',
            gap: 15,
            padding: 15,
            borderRadius: 8,
            marginTop: '-8%',
            backgroundColor: '#fff',
            boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)', // Added shadow for depth
            border: '1px solid #e0e0e0',
        },
        column2: {
            display: 'flex',
            flexDirection: 'column',
            gap: 15,
            padding: 15,
            borderRadius: 8,
            marginTop: '2%',
            backgroundColor: '#fff',
            boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)', // Added shadow for depth
            border: '1px solid #e0e0e0',
        },
        tableHeaderMain: {
            fontWeight: 'bold',
            fontSize: 16,
            color: '#333',
            textAlign: 'center',
            borderBottom: '2px solid #007bff',
            paddingBottom: 5,
        },

        textItem: {
            fontSize: 14,
            marginBottom: 10,
            color: '#555',
            textAlign: 'left', // Align text to the left for better readability
            lineHeight: 1.5,
        },

        separator: {
            height: 1,
            backgroundColor: '#E4E4E4',
            marginVertical: 15,
        },

        noDataText: {
            padding: 10,
            color: '#888',
            fontSize: 14,
            textAlign: 'center',
            fontStyle: 'italic',
        },

        // You can define a custom card style if needed for other sections
        card: {
            marginBottom: 20,
            padding: 20,
            backgroundColor: '#fff',
            borderRadius: 8,
            boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)',
        },
    });


    const handleDownloadPDF = async () => {
        const combinedLicenseData = [{
            ...registrationInfo,
            organization_details: licenseData
        }];
        const pdfBlob = await pdf(<LicensePDF license={combinedLicenseData} />).toBlob();
        const url = URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'license_report.pdf';
        document.body.appendChild(link);
        link.click();
        const downloadEvent = "License Report PDF Download";
        handleLogsSubmit(downloadEvent);
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };


    /**31st */
    const handleDownloadExcel = async () => {
        const wb = XLSX.utils.book_new();
        const wsData = [];

        // Registration Information Section
        wsData.push(["Registration Information"]);
        wsData.push([]); // empty row
        wsData.push(["Name", `${registrationInfo.firstName} ${registrationInfo.lastName}`]);
        wsData.push(["Designation", registrationInfo.designation]);
        wsData.push(["Mobile Number", registrationInfo.mobile]);
        wsData.push(["Email", registrationInfo.email]);
        wsData.push(["Last Login", registrationInfo.lastLogin]);

        wsData.push([]); // space before next section

        // License Information Section
        wsData.push(["License Information"]);
        wsData.push([]);
        wsData.push(["Status", registrationInfo.status]);
        wsData.push(["Agent/Endpoint Limit", licenseData.endpointLimit]);
        wsData.push(["Application User Limit", licenseData.userLimit]);
        wsData.push(["Validity in Days", licenseData.validityDays]);
        wsData.push(["License Expiry", licenseData.licenseExpiry]);

        const ws = XLSX.utils.aoa_to_sheet(wsData);

        // Merge section titles
        ws["!merges"] = [
            { s: { r: 0, c: 0 }, e: { r: 0, c: 1 } }, // "Registration Information"
            { s: { r: 8, c: 0 }, e: { r: 8, c: 1 } }, // "License Information"
        ];

        // Set column widths
        ws["!cols"] = [{ wpx: 200 }, { wpx: 250 }];

        XLSX.utils.book_append_sheet(wb, ws, "License_Report");
        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
        const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `licenseReport_report.xlsx`;
        document.body.appendChild(a);
        a.click();
        const downloadEvent = "License Report Excel Download";
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

    if (error) {
        return (
            <div className="flex items-center justify-center h-full text-center p-4">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative max-w-xl w-full">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            </div>
        );
    }

    if (userRole?.toLowerCase() === "employee") {
        return (
            <div className="bg-white h-full w-full flex flex-col justify-center items-center p-4">


                <p className="text-lg font-medium text-gray-700 mb-4 text-center">
                    You do not have permission to access this section.
                </p>


                {alert && (
                    <AlertComponent
                        message={alert.message}
                        type={alert.type}
                        onClose={() => setAlert(null)}
                    />
                )}
            </div>
        );
    }


    return (
        <div className="bg-gray-50">
            <div className="mx-auto space-y-6">

                {/* Registration Information */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-sm font-semibold text-gray-900">Registration Information</h2>
                        <div className="flex items-center space-x-2">
                            <img src={PDF} width={20} onClick={handleDownloadPDF} className="cursor-pointer" />
                            <img src={XL} width={20} onClick={handleDownloadExcel} className="cursor-pointer" />
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <InfoCard
                            icon={CheckCircle}
                            title="Status"
                            value={registrationInfo.status}
                            color="green"
                        />
                        <InfoCard
                            icon={User}
                            title="Name"
                            value={registrationInfo.organizationName}
                            color="blue"
                        />
                        <InfoCard
                            icon={Briefcase}
                            title="Designation"
                            value={registrationInfo.designation}
                            color="purple"
                        />
                        <InfoCard
                            icon={Mail}
                            title="Email"
                            value={registrationInfo.email}
                            color="orange"
                        />
                        <InfoCard
                            icon={Phone}
                            title="Mobile"
                            value={registrationInfo.mobile}
                            color="blue"
                        />
                        <InfoCard
                            icon={Clock}
                            title="Last Login"
                            value={registrationInfo.lastLogin}
                            color="gray"
                        />
                    </div>
                </div>


                {/* License Information */}
                <Section title="License Information">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <InfoCard
                            icon={Calendar}
                            title="Activation Date"
                            value={licenseData.activationDate}
                            color="blue"
                        />
                        <InfoCard
                            icon={Monitor}
                            title="Endpoint Limit"
                            value={licenseData.endpointLimit}
                            color="green"
                        />
                        <InfoCard
                            icon={Users}
                            title="User Limit"
                            value={licenseData.userLimit}
                            color="purple"
                        />
                        <InfoCard
                            icon={Calendar}
                            title="Validity (Days)"
                            value={licenseData.validityDays}
                            color="blue"
                        />
                        <InfoCard
                            icon={Clock}
                            title="Remaining Days"
                            value={licenseData.remainingDays}
                            color="orange"
                        />
                        <InfoCard
                            icon={Shield}
                            title="License Expiry"
                            value={licenseData.licenseExpiry}
                            color="gray"
                        />
                    </div>
                </Section>
            </div>
            {/* <ToastContainer position="top-right" autoClose={3000} /> */}
        </div>
    );
};

export default LicenseReport;