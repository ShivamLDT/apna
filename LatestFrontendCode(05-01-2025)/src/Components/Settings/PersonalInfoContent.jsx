import { useEffect, useState } from 'react';
import {
    Calendar,
    Clock,
    Shield,
    Monitor,
    Users,
    Mail,
    Phone,
    Briefcase,
    User,
    RefreshCw,
    Loader2
}
    from 'lucide-react';
import CryptoJS from "crypto-js";
import { useSyncData } from '../../Context/SyncDataContext';
import useClientData from '../../Hooks/useClientData';
import useUserList from '../../Hooks/useUserList';
import config from '../../config';
import useSaveLogs from '../../Hooks/useSaveLogs';
import { sendNotification } from '../../Hooks/useNotification';
import { useToast } from '../../ToastProvider';
import LoadingComponent from '../../LoadingComponent';

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

export function formatDateTimeString(dateTimeString) {
    if (!dateTimeString || typeof dateTimeString !== 'string') return 'Not Available';
    try {
        const datePart = dateTimeString.slice(0, 10).split('-').reverse().join('-');
        const rawTime = dateTimeString.slice(11, 16);
        let [hours, minutes] = rawTime.split(':').map(Number);
        let ampm = 'AM';

        if (hours >= 12) {
            ampm = 'PM';
            if (hours > 12) hours -= 12;
        } else if (hours === 0) {
            hours = 12;
        }

        const formattedTime = `${String(hours).padStart(2, '0')}:${minutes}`;
        return `${datePart} at ${formattedTime} ${ampm}`;
    } catch {
        return 'Invalid Date';
    }
}


const PersonalInfoContent = () => {
    const role = decryptData(localStorage.getItem("user_role"));
    const Mobile_num = decryptData(localStorage.getItem("user_Phone No."));
    const user_designation = decryptData(localStorage.getItem("user_designation"));
    const first_name1 = decryptData(localStorage.getItem("first_name"));
    const admin_email = decryptData(localStorage.getItem("admin_email"));
    const last_name1 = decryptData(localStorage.getItem("last_name"));
    const last_login1 = decryptData(localStorage.getItem("last_login"));
    const user_role = decryptData(localStorage.getItem("user_role"));
    const limit_of_users = decryptData(localStorage.getItem("limit_of_users"));
    const admin_name = decryptData(localStorage.getItem("admin_name"));
    const user_email = decryptData(localStorage.getItem("user_email"));
    const user_profile = localStorage.getItem("user_profile");
    const [timerSeconds, setTimerSeconds] = useState(0);
    const [isTimerActive, setIsTimerActive] = useState(false);
    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();

    const { syncData, loading, error, refetch, isRefetching, } = role === "Employee"
        ? { syncData: {}, loading: false, error: null, refetch: () => { }, isRefetching: false }
        : useSyncData();

    const {
        first_name,
        last_name,
        designation,
        email,
        mobile,
        last_login,
        image_url,
        organization_details
    } = syncData || {};
    const fullName = `${first_name || ''} ${last_name || ''}`;
    const { clientData, loading: clientLoading } = useClientData();
    const { userData } = useUserList();
    const { showToast } = useToast();

    const handleLicenseSync = () => {
        const downloadEvent = "License Sync";
        handleLogsSubmit(downloadEvent);
        refetch();
        setTimerSeconds(30);
        setIsTimerActive(true);
    };

    const handleTryAgain = () => {
        const downloadEvent = "License Sync";
        handleLogsSubmit(downloadEvent);
        refetch();
    };

    useEffect(() => {
        let interval = null;
        if (isTimerActive && timerSeconds > 0) {
            interval = setInterval(() => {
                setTimerSeconds(seconds => seconds - 1);
            }, 1000);
        } else if (timerSeconds === 0 && isTimerActive) {
            setIsTimerActive(false);
        }
        return () => clearInterval(interval);
    }, [isTimerActive, timerSeconds]);


    const remainingDays = organization_details?.expiry
        ? Math.max(
            0,
            Math.ceil(
                (new Date(organization_details.expiry) - new Date()) / (1000 * 60 * 60 * 24)
            ) - 1
        )
        : "N/A";


    useEffect(() => {
        if (remainingDays === 0) {
            sendNotification(`⚠️ Your license will expires today.`);
            showToast("Your license will expires today.", "warning");
        }
    }, [remainingDays, showToast]);


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
            <div className="flex flex-col items-center justify-center h-full space-y-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md text-center">
                    <div className="text-red-600 text-lg font-semibold mb-2">Failed to Load Data</div>
                    <div className="text-red-600 mb-4">{error}</div>
                    <button
                        onClick={handleTryAgain}
                        disabled={isRefetching}
                        className={`inline-flex items-center gap-2 px-6 py-2 ${isRefetching
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-red-500 hover:bg-red-600'
                            } text-white rounded-lg font-medium transition-colors`}
                    >
                        <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
                        {isRefetching ? 'Refreshing...' : 'Try Again'}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-2" >
            {/* Header */}
            {/* User Profile Section */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2 relative" >
                {/* Licence Sync Button in top-right */}
                {mobile && email && designation && (
                    <div className="absolute top-2 right-2">
                        <button
                            onClick={handleLicenseSync}
                            disabled={isRefetching || isTimerActive}
                            className={`px-4 py-1 ${isRefetching || isTimerActive
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-blue-500 hover:bg-blue-600'
                                } text-white rounded-lg text-sm transition-colors`}
                        >
                            {isRefetching
                                ? 'Syncing...'
                                : isTimerActive
                                    ? `Wait ${timerSeconds}s`
                                    : 'License Sync'
                            }
                        </button>
                    </div>
                )
                }

                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
                    <div className="relative">
                        <div
                            className={`w-24 h-24 rounded-full flex items-center justify-center text-white text-3xl font-bold overflow-hidden ${image_url || user_profile ? '' : 'bg-blue-600'
                                }`}
                        >
                            {image_url || user_profile ? (
                                <img
                                    src={image_url ? `data:image/png;base64,${image_url}` : user_profile}
                                    alt="Profile"
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <span>
                                    {(first_name?.charAt(0) || first_name1?.charAt(0) || "").toUpperCase()}
                                    {(last_name1?.charAt(0) || "").toUpperCase()}
                                </span>
                            )}
                        </div>
                    </div>


                    <div className="flex-1 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex items-center gap-3">
                                <User className="w-5 h-5 text-gray-400" />
                                <div>
                                    <p className="text-sm text-gray-500 flex">Name</p>
                                    <p className="font-semibold text-gray-800">{fullName.trim() ? fullName : first_name1 + " " + last_name1}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <Briefcase className="w-5 h-5 text-gray-400" />
                                <div>
                                    <p className="text-sm text-gray-500">Designation</p>
                                    <p className="font-semibold text-gray-800">{designation || user_designation}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <Phone className="w-5 h-5 text-gray-400" />
                                <div>
                                    <p className="text-sm text-gray-500">Phone</p>
                                    <p className="font-semibold text-gray-800">{mobile || Mobile_num}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <Mail className="w-5 h-5 text-gray-400" />
                                <div>
                                    <p className="text-sm text-gray-500">Email</p>
                                    <p className="font-semibold text-gray-800">{email || user_email}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div >


            {/* Usage Stats */}
            {
                mobile && email && designation ? (
                    <>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
                            <h3 className="text-lg font-semibold text-gray-800 ">Usage Statistics</h3>

                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                                {/* Days Used */}
                                <div className="text-center">
                                    <div className="relative w-24 h-24 mx-auto">
                                        <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center">
                                            <Clock className="w-8 h-8 text-red-500" />
                                        </div>
                                    </div>

                                    <p className="text-2xl font-bold text-gray-800">
                                        {organization_details?.limit_of_days &&
                                            organization_details?.expiry
                                            ? organization_details.limit_of_days -
                                            Math.max(
                                                0,
                                                Math.ceil(
                                                    (new Date(organization_details.expiry) - new Date()) /
                                                    (1000 * 60 * 60 * 24)
                                                )
                                            ) + 1
                                            : 'N/A'}
                                    </p>
                                    <p className="text-sm text-gray-500">Days Used</p>
                                    <p className="text-xs text-gray-400">
                                        of {organization_details?.limit_of_days || 'N/A'} total
                                    </p>
                                </div>


                                {/* Users */}
                                <div className="text-center">
                                    <div className="relative w-24 h-24 mx-auto">

                                        <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center">
                                            <Users className="w-8 h-8 text-blue-500" />
                                        </div>
                                    </div>
                                    <p className="text-2xl font-bold text-gray-800">{userData?.length || 0}</p>
                                    <p className="text-sm text-gray-500">Users</p>
                                    <p className="text-xs text-gray-400">of {organization_details?.limit_of_users} total</p>
                                </div>

                                {/* License Info */}
                                <div className="text-center">
                                    <div className="relative w-24 h-24 mx-auto">
                                        <div className="w-24 h-24 bg-purple-100 rounded-full flex items-center justify-center">
                                            <Monitor className="w-8 h-8 text-purple-500" />
                                        </div>
                                    </div>

                                    {clientLoading ? (
                                        <Loader2 className="w-6 h-6 text-purple-500 animate-spin mx-auto" />
                                    ) : (
                                        <p className="text-2xl font-bold text-gray-800">
                                            {clientData?.result?.length}
                                        </p>
                                    )}

                                    <p className="text-sm text-gray-500">Active</p>
                                    <p className="text-xs text-gray-400">
                                        of {organization_details?.limit_of_agents} agents
                                    </p>
                                </div>

                                {/* Remaining Days */}
                                <div className="text-center">
                                    <div className="relative w-24 h-24 mx-auto">
                                        <div className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center">
                                            <Calendar className="w-8 h-8 text-yellow-500" />
                                        </div>
                                    </div>
                                    <p className="text-2xl font-bold text-gray-800">{organization_details?.expiry
                                        ? Math.max(
                                            0,
                                            Math.ceil(
                                                (new Date(organization_details.expiry) - new Date()) / (1000 * 60 * 60 * 24)
                                            ) - 1
                                        )
                                        : 'N/A'}</p>
                                    <p className="text-sm text-gray-500">Days Left</p>
                                    <p className="text-xs text-gray-400">until renewal</p>
                                </div>
                            </div>
                        </div>

                        {/* Quick Info Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
                                <div className="flex items-center gap-2">
                                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <Shield className="w-6 h-6 text-blue-500" />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-800">Last Login</h4>
                                        <p className="text-sm text-gray-500">{formatDateTimeString(last_login)}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
                                <div className="flex items-center gap-2">
                                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                        <Calendar className="w-6 h-6 text-green-500" />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-800">Remaining Days</h4>
                                        <p className="text-2xl font-bold text-green-500">
                                            {organization_details?.expiry
                                                ? Math.max(
                                                    0,
                                                    Math.ceil(
                                                        (new Date(organization_details.expiry) - new Date()) / (1000 * 60 * 60 * 24)
                                                    )
                                                ) - 1
                                                : 'N/A'}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
                                <div className="flex items-center gap-2">
                                    <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                                        <Clock className="w-6 h-6 text-red-500" />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-800">License Expire</h4>
                                        <p className="text-sm text-gray-500">{formatDateTimeString(organization_details?.expiry)}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </>
                ) : <>
                    <div className="bg-white rounded-xl p-6 shadow-lg max-w-4xl">
                        <h2 className="text-lg font-semibold text-gray-800 mb-5">Statistics</h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div className="bg-red-50 border border-gray-200 rounded-lg p-4 text-center transition-all duration-300 hover:shadow-md hover:-translate-y-0.5">
                                <div className="w-10 h-10 mx-auto mb-3 flex items-center justify-center rounded-full bg-black bg-opacity-10">
                                    <span className="text-xl">👤</span>
                                </div>
                                <div className="text-2xl font-bold text-gray-800 mb-1">Admin</div>
                                <div className="text-sm font-medium text-gray-600">{admin_name}</div>
                                <div className="text-sm font-medium text-gray-600">{admin_email}</div>
                            </div>

                            <div className="bg-blue-50 border border-gray-200 rounded-lg p-4 text-center transition-all duration-300 hover:shadow-md hover:-translate-y-0.5">
                                <div className="w-10 h-10 mx-auto mb-3 flex items-center justify-center rounded-full bg-black bg-opacity-10">
                                    <span className="text-xl">👥</span>
                                </div>
                                <div className="text-2xl font-bold text-gray-800 mb-1">{limit_of_users}</div>
                                <div className="text-sm font-medium text-gray-600">Total Users</div>
                                <div className="text-sm font-medium text-gray-600">🔵 including {first_name1}</div>

                            </div>

                            <div className="bg-purple-50 border border-gray-200 rounded-lg p-4 text-center transition-all duration-300 hover:shadow-md hover:-translate-y-0.5">
                                <div className="w-10 h-10 mx-auto mb-3 flex items-center justify-center rounded-full bg-black bg-opacity-10">
                                    <span className="text-xl">🔒</span>
                                </div>
                                <div className="text-2xl font-bold text-gray-800 mb-1">Last-Login</div>
                                <div className="text-sm font-medium text-gray-600">{last_login1}</div>
                            </div>
                        </div>
                    </div>
                </>
            }



        </div >
    );
};

export default PersonalInfoContent;