// components/layout/Sidebar.jsx
import React, { useState, useEffect, useContext } from "react";
import {
  LayoutDashboard,
  Database,
  CloudDownload,
  UsersRound,
  Laptop,
  Cable,
  BarChart3,
  FileUser,
  ChartNoAxesCombined,
  MessageSquare,
  Settings,
  Crown,
} from "lucide-react";
import Logo from "../../Image/ApnaCloud.png"
import Slogo from "../../Image/title img.png"
import config from "../../config";
import { useLocation, useNavigate } from "react-router-dom";
import CryptoJS from "crypto-js";
import { Backupindex } from "../../Context/Backupindex";
import { UIContext } from "../../Context/UIContext";
const menuItems = [
  { icon: LayoutDashboard, label: "Home", active: true, path: "/" },
  { icon: Database, label: "Backup", path: "/backup" },
  { icon: CloudDownload, label: "Restore", path: "/restore" },
  { icon: UsersRound, label: "Users", path: "/users" },
  { icon: Laptop, label: "Endpoints", path: "/endpoints" },
  { icon: ChartNoAxesCombined, label: "Progress", path: "/progress" },
  { icon: BarChart3, label: "Report", path: "/report" },
  { icon: Cable, label: "Pairing", path: "/pairing" },
  { icon: Settings, label: "Settings", path: "/settings" },
  { icon: MessageSquare, label: "Support", path: "/chatbot" },
  { icon: FileUser, label: "About", path: "https://www.apnabackup.com/" },
];

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

const Sidebar = ({ isOpen, onClose, onNavigate }) => {
  const [activeItem, setActiveItem] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const role = decryptData(localStorage.getItem("user_role"));
  const [privileges, setPrivileges] = useState({});
  const { setSourceData, setIsBackup, setCheckBoxData, } = useContext(Backupindex)
  const { setonechecktable, setShowEndpointBackup } = useContext(UIContext);
  const [serverVersion, setServerVersion] = useState("");

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



  useEffect(() => {
    const currentPath = location.pathname;

    // Define manual route groups
    const routeGroups = {
      "/": ["/"],
      "/backup": ["/backup"],
      "/restore": ["/restore"],
      "/users": ["/users"],
      "/endpoints": ["/endpoints"],
      "/progress": ["/progress"],
      "/report": ["/report", "/backup-logs", "/portal-user-logs", "/license-info", "/paired-endpoints", "/endpoint-overview", "/event-logs", "/task-logs", "/system-logs"],
      "/pairing": ["/pairing"],
      "/settings": ["/settings"],
      "/chatbot": ["/chatbot", "/support"],
      "https://www.apnabackup.com/": ["https://www.apnabackup.com/"]
    };

    let matchedPath = Object.keys(routeGroups).find(key =>
      routeGroups[key].includes(currentPath)
    );

    if (!matchedPath) {
      matchedPath = Object.keys(routeGroups).find(key =>
        currentPath.startsWith(key) && key !== "/"
      );
    }

    const foundIndex = filteredMenuItems.findIndex(item => item.path === matchedPath);
    setActiveItem(foundIndex !== -1 ? foundIndex : 0);
  }, [location.pathname]);


  const handleItemClick = (index, item) => {
    if (item.path) {
      if (item.path.startsWith("http") && item.label !== "Support") {
        window.open(item.path, "_blank", "noopener,noreferrer");
        return;
      } else {
        navigate(item.path);
      }

      if (item.path == "/backup") {
        setIsBackup(true);
        setCheckBoxData(true);
        setonechecktable(true);
        setShowEndpointBackup(false);
        setSourceData('')
      }
      else {
        setIsBackup(false)
        setCheckBoxData(false)
      }
    }

    if (window.innerWidth < 1024) {
      onClose();
    }
  };





  const handleGetPro = () => {
    const upgradeUrl = config.API.UPGRADE_URL;
    window.open(upgradeUrl);
  };


  const filteredMenuItems = menuItems.filter(item => {
    if (role === "Employee" && item.label === "Backup" && !privileges.backupReadWrite) return false;
    if (role === "Employee" && item.label === "Restore" && !privileges.restoreReadWrite) return false;
    if (role === "Employee" && item.label === "Users" && !privileges.userCreate && !privileges.userDelete && !privileges.userUpdate && !privileges.userRead) return false;
    if (role === "Employee" && item.label === "Pairing") return false;

    return true;
  });

  useEffect(() => {
    let intervalId;

    const fetchVersion = () => {
      const storedVersion = decryptData(localStorage.getItem("serverVersion"));
      if (storedVersion) {
        setServerVersion(storedVersion);
        clearInterval(intervalId);
      }
    };
    fetchVersion();
    intervalId = setInterval(fetchVersion, 1000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <>
      {/* Sidebar */}
      <div
        className={`bg-white shadow-lg transition-all duration-300 ease-in-out ${isOpen
          ? "w-40"
          : "w-16"
          } overflow-hidden relative z-30 h-full flex flex-col`}
      >
        {/* Header with Logo */}
        <div className="p-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex justify-center items-center w-full">
            {isOpen ? (
              <div className="w-full flex items-center justify-center flex-col relative">
                <img src={Logo} className="w-30 object-contain" alt="Logo" />
                <span className="absolute text-xl font-semibold" style={{ top: '5px', left: '100px' }}>™</span>
                <span className="text-xs mt-1">Version: {serverVersion}</span>
              </div>
            ) : (
              <div className="w-8 h-8 flex items-center justify-center flex-col">
                <img src={Slogo} className="w-8 h-8 object-contain" alt="Logo" />
                <span className="text-xs mt-1">{serverVersion}</span>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden">
          <nav className="p-2 space-y-1">
            {filteredMenuItems.map((item, index) => (
              <div
                key={index}
                onClick={() => handleItemClick(index, item)}
                className={`flex items-center rounded-lg cursor-pointer transition-all duration-200 group relative ${isOpen ? 'p-2' : 'p-2 justify-center'
                  } ${activeItem === index
                    ? "bg-blue-600 text-white shadow-md"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  }`}
                title={!isOpen ? item.label : ""}
              >
                {isOpen ? (
                  <div className="flex items-center gap-3 w-full">
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    <span className="text-xs font-medium truncate">{item.label}</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center w-full">
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                  </div>
                )}

                {/* Tooltip for collapsed state */}
                {!isOpen && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                    {item.label}
                    <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-800 rotate-45"></div>
                  </div>
                )}
              </div>
            ))}
          </nav>


          {/* Pro Component - Fixed at bottom */}
          {isOpen && (
            <div className="p-3 flex-shrink-0">
              <div className="bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl p-4 text-white relative overflow-hidden">
                {/* Background decoration */}
                <div className="absolute top-0 right-0 w-16 h-16 bg-opacity-10 rounded-full -translate-y-8 translate-x-8"></div>
                <div className="absolute bottom-0 left-0 w-12 h-12 bg-opacity-10 rounded-full translate-y-6 -translate-x-6"></div>

                {/* Content */}
                <div className="relative z-10">
                  <div className="flex items-center justify-center w-8 h-8 bg-opacity-20 rounded-full mb-3 mx-auto">
                    <Crown className="w-4 h-4 text-white" />
                  </div>

                  <h3 className="text-sm font-bold text-center mb-1">
                    Apna Backup LTS
                  </h3>

                  <p className="text-xs text-center text-white text-opacity-90 mb-3 leading-tight">
                    Get access to all features of Apna Backup
                  </p>

                  <button
                    onClick={handleGetPro}
                    className="w-full bg-white text-purple-600 text-xs font-semibold py-2 px-3 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                  >
                    Upgrade Plan
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Collapsed Pro Component */}
          {!isOpen && (
            <div className="p-2 flex-shrink-0">
              <div
                className="bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg p-2 text-white cursor-pointer hover:from-purple-600 hover:to-blue-700 transition-all duration-200 group relative flex items-center justify-center"
                onClick={handleGetPro}
                title="Upgrade Plan"
              >
                <Crown className="w-5 h-5" />

                {/* Tooltip for collapsed state */}
                <div className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                  Upgrade Plan
                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-800 rotate-45"></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {isOpen && window.innerWidth < 1024 && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={onClose}
        />
      )}
    </>
  );
};

export default Sidebar;