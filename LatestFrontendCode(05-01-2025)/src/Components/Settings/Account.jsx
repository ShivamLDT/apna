import React, { useState } from 'react';
import { Menu } from 'lucide-react';
import SettingSidebar from './SettingSidebar';
import PersonalInfoContent from './PersonalInfoContent';
import DestinationStorage from './DestinationStorage';
import ChangePassword from './ChangePassword';
import NotificationSettings from './NotificationSettings';
// Main Dashboard Component
const Account = () => {
    const [activeItem, setActiveItem] = useState('personal');
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const renderContent = () => {
        switch (activeItem) {
            case 'personal':
                return <PersonalInfoContent />;
            case 'storage':
                return <DestinationStorage />
            case 'password':
                return <ChangePassword />
            case 'notifications':
                return <NotificationSettings />
            default:
                return <PersonalInfoContent />;
        }
    };

    return (
        <div className="bg-gray-50">
            <div className="flex">
                {/* SettingSidebar */}
                <SettingSidebar
                    activeItem={activeItem}
                    setActiveItem={setActiveItem}
                    isOpen={sidebarOpen}
                    setIsOpen={setSidebarOpen}
                />

                {/* Main Content */}
                <div className="flex-1 lg:ml-0">
                    {/* Mobile Header */}
                    <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3">
                        <div className="flex items-center justify-between">
                            <button
                                onClick={() => setSidebarOpen(true)}
                                className="p-2 hover:bg-gray-100 rounded-lg"
                            >
                                <Menu className="w-6 h-6" />
                            </button>
                            <h1 className="text-lg font-semibold text-gray-800">Settings</h1>
                            <div className="w-10"></div>
                        </div>
                    </div>

                    {/* Content Area */}
                    <div className="p-1 lg:p-1 h-full">
                        {renderContent()}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Account;