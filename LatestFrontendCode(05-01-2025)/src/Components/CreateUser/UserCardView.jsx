import React, { useState, useEffect } from 'react';
import { Mail, Phone, Clock, Briefcase, Trash2, SquarePen, Eye, X, Check, AlertCircle } from 'lucide-react';
import useUserList from '../../Hooks/useUserList';
import CryptoJS from "crypto-js";
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

const UserCardView = ({ onEdit, onDelete, refreshTrigger = 0 }) => {
    const {
        filteredUsers,
        searchTerm,
        handleSearchChange,
        loading,
        error,
    } = useUserList(refreshTrigger);

    const [privilegesModal, setPrivilegesModal] = useState(false);
    const [selectUser, setSelectUser] = useState(null);

    const showPrivileges = (user) => {
        setSelectUser(user);
        setPrivilegesModal(true);
    }

    const closePrivileges = () => {
        setPrivilegesModal(false);
    }

    const role = decryptData(localStorage.getItem("user_role"));

    const [privileges, setPrivileges] = useState({});

    useEffect(() => {
        const stored = decryptData(localStorage.getItem("user_privileges"));
        if (stored) {
            try {
                setPrivileges(JSON.parse(stored));
            } catch (err) {
                console.error("Failed to parse user_privileges", err);
            }
        }
    }, []);

    const hasActionPermissions = () => {
        if (role !== "Employee") {
            return true;
        }
        return privileges.userUpdate || privileges.userDelete || privileges.userRead;
    };

    const canEdit = () => {
        if (role !== "Employee") return true;
        return privileges.userUpdate;
    };

    const canDelete = () => {
        if (role !== "Employee") return true;
        return privileges.userDelete;
    };

    const canView = () => {
        if (role !== "Employee") return true;
        return privileges.userRead;
    };

    const showActionsColumn = hasActionPermissions() && (canEdit() || canDelete());

    // Group privileges by category for better organization
    const groupPrivileges = (privileges) => {
        const groups = {
            'User Management': [],
            'Endpoint Management': [],
            'Backup & Restore': [],
            'Progress Management': [],
            'Report Management': [],
            'Settings': []
        };

        Object.entries(privileges).forEach(([key, value]) => {
            const privilege = { key, value, label: formatPrivilegeLabel(key) };

            if (key.startsWith('user')) {
                groups['User Management'].push(privilege);
            } else if (key.startsWith('agent')) {
                groups['Endpoint Management'].push(privilege);
            } else if (key.includes('backup') || key.includes('restore')) {
                groups['Backup & Restore'].push(privilege);
            } else if (key.startsWith('progress')) {
                groups['Progress Management'].push(privilege);
            }// else if (key.startsWith('report')) {
            //     groups['Report Management'].push(privilege);
            // } else if (key.startsWith('setting')) {
            //     groups['Settings'].push(privilege);
            // }
        });

        return groups;
    };

    const formatPrivilegeLabel = (key) => {
        return key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    };

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
            <div className="h-full flex items-center justify-center">
                <div className="text-center p-8">
                    <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Error loading users</h3>
                    <p className="text-gray-500 dark:text-gray-400">{error}</p>
                </div>
            </div>
        );
    }

    // If user doesn't have read permission, show access denied message
    if (role === "Employee" && !canView()) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center p-8">
                    <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Access Denied</h3>
                    <p className="text-gray-500 dark:text-gray-400">You don't have permission to view the user list.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
            <div className="max-w-7xl mx-auto">
                {/* Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
                    {filteredUsers.length > 0 ? (

                        filteredUsers.map((profile, index) => (
                            <div
                                key={profile.id || index}
                                className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover: overflow-hidden border border-gray-100"
                            >
                                {/* Gradient Background */}
                                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-purple-600/5 to-indigo-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                                {/* Card Content */}
                                <div className="relative p-2">
                                    {/* Profile Image */}
                                    <div className="flex items-center justify-left gap-2 mb-2">
                                        {profile.profilePhoto && profile.profilePhoto.startsWith('data:image') ? (
                                            <div className="relative">
                                                <img
                                                    src={profile.profilePhoto}
                                                    className="w-20 h-20 rounded-full object-cover shadow-md border-4 border-white group-hover:shadow-lg transition-shadow duration-300"
                                                />
                                            </div>
                                        ) : (
                                            <div className="w-20 h-20 rounded-full flex items-center justify-center bg-gradient-to-br from-blue-400 to-blue-600 text-white font-bold text-lg shadow-md group-hover:shadow-lg transition-shadow duration-300">
                                                {profile.name && profile.name.charAt(0).toUpperCase()}{profile.lname && profile.lname.charAt(0).toUpperCase()}
                                            </div>
                                        )}
                                        {/* Name */}
                                        <div>
                                            <h3 className="text-sm font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">
                                                {profile.name || profile.firstName} {profile.lname || profile.lastName}
                                            </h3>
                                            <h3 className="text-sm text-gray-900 group-hover:text-blue-600 transition-colors duration-300">
                                                {profile.designation}
                                            </h3>
                                        </div>

                                    </div>

                                    {/* Info Items */}
                                    <div className="space-y-2">
                                        <div className="flex items-center text-sm text-gray-600 group-hover:text-gray-800 transition-colors duration-300">
                                            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-green-200 transition-colors duration-300">
                                                <Mail className="w-4 h-4 text-green-600" />
                                            </div>
                                            <span className="truncate">{profile.email}</span>
                                        </div>

                                        <div className="flex items-center text-sm text-gray-600 group-hover:text-gray-800 transition-colors duration-300">
                                            <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-purple-200 transition-colors duration-300">
                                                <Phone className="w-4 h-4 text-purple-600" />
                                            </div>
                                            <span className="truncate">{profile.mobileNumber}</span>
                                        </div>

                                        <div className="flex items-center text-xs text-gray-500 group-hover:text-gray-600 transition-colors duration-300">
                                            <div className="flex-shrink-0 w-6 h-6 bg-gray-100 rounded-md flex items-center justify-center mr-2 group-hover:bg-gray-200 transition-colors duration-300">
                                                <Clock className="w-3 h-3 text-gray-500" />
                                            </div>
                                            <span>Created At: {new Date(profile.createdTime).toLocaleString()}</span>
                                        </div>
                                    </div>

                                    {/* Action Buttons Vertical Right */}
                                    {showActionsColumn && (
                                        <div className="absolute right-2 top-4 flex flex-col gap-y-6 items-end z-10">
                                            {canEdit() && (
                                                <button
                                                    className="p-1 bg-gray-500 text-white rounded-lg shadow-md hover:shadow-lg"
                                                    onClick={() => onEdit(profile)}
                                                >
                                                    <SquarePen className="w-4 h-4" />
                                                </button>
                                            )}

                                            {canDelete() && (
                                                <button
                                                    className="p-1 bg-red-500 text-white rounded-lg shadow-md hover:shadow-lg"
                                                    onClick={() => onDelete(profile)}
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            )}
                                            <button
                                                className="p-1 bg-blue-500 text-white rounded-lg shadow-md hover:shadow-lg"
                                                onClick={() => showPrivileges(profile)}
                                            >
                                                <Eye className="w-4 h-4" />
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    ) : (<div className="text-center py-12">
                        <div className="text-gray-400 mb-4">

                        </div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No users available</h3>
                    </div>)}
                </div>

                {/* Empty State */}
                {/* {filteredUsers.length === 0 && (
                    <div className="text-center py-12">
                        <div className="text-gray-400 mb-4">
                            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
                        <p className="text-gray-600">Try adjusting your search criteria</p>
                    </div>
                )} */}
            </div>

            {privilegesModal && selectUser && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                    <div className="bg-white w-full max-w-4xl rounded-2xl shadow-2xl p-0 relative overflow-hidden h-5/6 flex flex-col">
                        {/* Header */}
                        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-1 flex items-center justify-between">
                            <div className="flex items-center gap-1">

                                <div>
                                    <h2 className="text-sm font-bold">User Privileges - {selectUser.name} {selectUser.lname}</h2>
                                </div>
                            </div>
                            <button
                                className="text-white hover:text-red-500 transition-colors duration-200 p-2 rounded-full hover:bg-white hover:bg-opacity-20"
                                onClick={closePrivileges}
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        {/* Privileges Content */}
                        <div className="flex-1 overflow-y-auto">
                            {selectUser.privileges ? (
                                <div>
                                    {Object.entries(groupPrivileges(selectUser.privileges)).map(([category, privileges]) => (
                                        privileges.length > 0 && (
                                            <div key={category} className="bg-white rounded-xl p-2 shadow-sm">
                                                <h3 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                                                    {category}
                                                </h3>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                                    {privileges.map((privilege) => (
                                                        <div
                                                            key={privilege.key}
                                                            className={`flex items-center justify-between p-1 rounded-lg border transition-all duration-200 ${privilege.value
                                                                ? 'bg-green-50 border-green-200 hover:bg-green-100'
                                                                : 'bg-red-50 border-red-200 hover:bg-red-100'
                                                                }`}>
                                                            <div className="flex items-center gap-3">

                                                                <span className="text-sm text-gray-700">
                                                                    {privilege.label}
                                                                </span>
                                                            </div>
                                                            <span className={`text-xs px-2 py-1 rounded-full ${privilege.value
                                                                ? 'bg-green-100 text-green-800'
                                                                : 'bg-red-100 text-red-800'
                                                                }`}>
                                                                {privilege.value ? 'Granted' : 'Denied'}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12">
                                    <div className="text-gray-400 mb-4">
                                        <AlertCircle className="w-16 h-16 mx-auto" />
                                    </div>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">No privileges data available</h3>
                                    <p className="text-gray-600">This user doesn't have any privilege information</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserCardView;