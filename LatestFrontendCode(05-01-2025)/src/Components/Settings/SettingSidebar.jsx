// Sidebar Component
import React, { useState } from 'react';
import {
    User,
    Database,
    Lock,
    Bell,
    Settings,
    ChevronDown,
    ChevronRight, X
} from "lucide-react";
import CryptoJS from "crypto-js";
import { useSyncData } from '../../Context/SyncDataContext';

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

const SettingSidebar = ({ activeItem, setActiveItem, isOpen, setIsOpen }) => {
    const [expandedItems, setExpandedItems] = useState({});
    const { syncData, loading, error } = useSyncData();
    const Role = decryptData(localStorage.getItem("user_role"));
    const user_profile = localStorage.getItem("admin_img");
    const admin_name = decryptData(localStorage.getItem("admin_name"));

    const {
        first_name,
        last_name,
        role,
        image_url,
        organization_details
    } = syncData || {};

    const fullName = `${first_name || ''} ${last_name || ''}`;

    const menuItems = Role === "Employee"
        ? [
            { id: 'personal', label: 'Personal Information', icon: User },
            { id: 'password', label: 'Change Password', icon: Lock }
        ]
        : [
            { id: 'personal', label: 'Personal Information', icon: User },
            { id: 'storage', label: 'Destination Storage', icon: Database },
            { id: 'password', label: 'Change Password', icon: Lock },
            { id: 'notifications', label: 'Message & Email', icon: Bell }
        ];


    const first_name1 = decryptData(localStorage.getItem("first_name"));
    const last_name1 = decryptData(localStorage.getItem("last_name"));
    const toggleSubmenu = (itemId) => {
        setExpandedItems(prev => ({
            ...prev,
            [itemId]: !prev[itemId]
        }));
    };

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar */}
            <div className={`
        fixed lg:sticky top-0 left-0 w-80 bg-white shadow-xl z-40 lg:z-0 transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0
      `}>
                <div className="p-2 border-b border-gray-100">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-500 rounded-lg">
                                <Settings className="w-6 h-6 text-white" />
                            </div>
                            <h1 className="text-xl font-bold text-gray-800">Settings</h1>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* User Profile Card */}
                <div className="p-2 border-b border-gray-100">
                    <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl"></div>
                        <div className="relative bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-2 text-white">
                            <div className="flex items-center gap-4">
                                <div className="relative">
                                    <div className="w-16 h-16 bg-blue-600 text-white text-3xl rounded-full flex items-center justify-center">
                                        {image_url || user_profile ? (
                                            <img
                                                src={`data:image/png;base64,${image_url || user_profile}`}
                                                alt="Profile"
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <span>{first_name?.charAt(0).toUpperCase() || admin_name?.charAt(0).toUpperCase()}</span>
                                        )}
                                    </div>
                                </div>
                                <div>
                                    <h3 className="font-semibold text-lg text-black">{fullName.trim() || admin_name}</h3>
                                    <p className="text-sm text-blue-500">{Role === "Employee" ? "Admin" : "Admin Account"}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Navigation Menu */}
                <nav className="p-2">
                    <div className="space-y-2">
                        {menuItems.map((item) => (
                            <div key={item.id}>
                                <button
                                    onClick={() => {
                                        if (item.hasSubmenu) {
                                            toggleSubmenu(item.id);
                                        } else {
                                            setActiveItem(item.id);
                                            setIsOpen(false);
                                        }
                                    }}
                                    className={`
                    w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-200
                    ${activeItem === item.id
                                            ? 'bg-blue-500 text-white shadow-lg'
                                            : 'text-gray-700 hover:bg-gray-100'
                                        }
                  `}
                                >
                                    <div className="flex items-center gap-3">
                                        <item.icon className="w-5 h-5" />
                                        <span className="font-medium">{item.label}</span>
                                    </div>
                                    {item.hasSubmenu && (
                                        <ChevronDown className={`w-4 h-4 transition-transform ${expandedItems[item.id] ? 'rotate-180' : ''}`} />
                                    )}
                                </button>

                                {item.hasSubmenu && expandedItems[item.id] && (
                                    <div className="ml-8 mt-2 space-y-1">
                                        {item.submenu.map((subItem, index) => (
                                            <button
                                                key={index}
                                                className="w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                                            >
                                                {subItem}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </nav>
            </div>
        </>
    );
};

export default SettingSidebar;