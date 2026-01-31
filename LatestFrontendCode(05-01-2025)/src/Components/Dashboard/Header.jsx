// components/layout/Header.jsx
import React, { useState, useEffect, useRef, useContext } from "react";
import { Menu, X, Bell, ChevronDown, LogOut, User } from "lucide-react";
import "./Dashboard.css";
// import Picture from "../../Image/1.jpg";
import CryptoJS from "crypto-js";
import config from "../../config";
import { useToast } from "../../ToastProvider";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Backupindex } from "../../Context/Backupindex";
import { NotificationContext } from "../../Context/NotificationContext";
import { el } from "date-fns/locale/el";
import axiosInstance from "../../axiosinstance";
const Header = ({ sidebarOpen, toggleSidebar }) => {
  const navigate = useNavigate();
  const { setNotificationData, notificationData } = useContext(NotificationContext);
  const [orgName, setOrgName] = useState("");
  const [userName, setUserName] = useState("");
  const [userRole, setUserRole] = useState("");
  const [isUser, setIsUser] = useState(false)
  const [profilePic, setProfilePic] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [notificationDropdownOpen, setNotificationDropdownOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const [notificationApi, setNotificationApi] = useState([])
  const [isReadingAll, setIsReadingAll] = useState(false);

  const getNotification = async () => {
    try {
      const response = await axiosInstance.get(
        `${config.API.FLASK_URL}/eventnotifications`,
        {
          headers: {
            "Content-Type": "application/json",
            token: localStorage.getItem("AccessToken"),
          },
        }
      );

      setNotificationApi(
        Array.isArray(response.data) ? response.data : []
      );

    } catch (error) {
      console.error("Error", error);
    }
  };


  useEffect(() => {
    getNotification();

    const token = localStorage.getItem("AccessToken");
    const eventSource = new EventSource(
      `${config.API.FLASK_URL}/eventnotifications/stream?token=${token}`
    );

    eventSource.onmessage = (event) => {
      const newNotification = JSON.parse(event.data);

      setNotificationApi((prev) => [newNotification, ...prev]);
    };

    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);



  const dropdownRef = useRef(null);
  const notificationRef = useRef(null);

  const { showToast } = useToast();

  const addNotification = (message, type = "info") => {
    const newNotification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date(),
      isRead: false
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const markAsRead = (notificationId) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === notificationId
          ? { ...notification, isRead: true }
          : notification
      )
    );
  };


  useEffect(() => {
    const encrypted = sessionStorage.getItem("notification_Data");
    const check_notification = sessionStorage.getItem("show_notification_Data");
    if (check_notification == "true") {
      if (encrypted) {
        try {
          const decrypted = decryptData(encrypted); // returns JSON string

          if (decrypted && decrypted.trim() !== "") {
            const notification = JSON.parse(decrypted); // now an object

            // Check if already an array (support storing array in future)
            const finalData = Array.isArray(notification) ? notification : [notification];
            const Again_Parse = JSON.parse(finalData);
            setNotificationData((prev) => [...prev, Again_Parse]);
          } else {
            console.warn("Decryption returned empty or invalid JSON string.");
          }

        } catch (error) {
          console.error("Failed to parse notification data:", error);
        }
      }
    }
  }, []);


  const markNotificationRead = async (id) => {
    try {
      await axiosInstance.patch(
        `${config.API.FLASK_URL}/eventnotifications/${id}/read`,
        null,
        {
          headers: {
            "Content-Type": "application/json",
            token: localStorage.getItem("AccessToken"),
          },
        }
      );
      // update local state
      setNotificationApi(prev =>
        prev.map(n => n.id === id ? { ...n, is_read: true } : n)
      );
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  const readAllNotifications = async () => {
    try {
      setIsReadingAll(true);
      const payload = { action: "read_all" };
      const response = await axiosInstance.post(
        `${config.API.FLASK_URL}/eventnotifications`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            token: localStorage.getItem("AccessToken"),
          },
        }
      );

      if (response.status === 200) {
        setNotificationApi(prevNotifications =>
          prevNotifications.map(note => ({
            ...note,
            is_read: true,
          }))
        );
      }

    } catch (error) {
      console.error("Error marking all notifications as read:", error);
    } finally {
      setIsReadingAll(false);
    }
  };



  const clearAllNotifications = async () => {
    try {
      const response = await axiosInstance.delete(
        `${config.API.FLASK_URL}/eventnotifications/clear`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            token: localStorage.getItem("AccessToken"),
          },
        }
      );
      setNotificationApi(response?.data?.remaining || []);
    } catch (error) {
      console.error("Error clearing notifications:", error);
    }
  };

  // Function to remove notification
  const removeNotification = (notificationId) => {
    // setNotificationData(prev => prev.filter(n => n.id !== notificationId));
    const deleteNotification = async (id) => {
      try {
        const response = await axiosInstance.delete(
          `${config.API.FLASK_URL}/eventnotifications/${id}`,
          {},
          {
            headers: {
              "Content-Type": "application/json",
              token: localStorage.getItem("AccessToken"),
            },
          }
        );
        setNotificationApi(response?.data?.remaining);
        return response.data;
      } catch (error) {
        console.error("Error", error);
        throw error;
      }
    };
    deleteNotification(notificationId);
  };



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

  useEffect(() => {
    const storedOrgName = decryptData(localStorage.getItem("org_name"));
    if (storedOrgName) {
      setOrgName(storedOrgName);
    }

    const profileUrl = localStorage.getItem('Admin Profile');
    const user_profile = localStorage.getItem('user_profile');
    const firstName = decryptData(localStorage.getItem("first_name")) || "";
    const lastName = decryptData(localStorage.getItem("last_name")) || "";

    const adminRole = decryptData(localStorage.getItem("role"));
    const employeeRole = decryptData(localStorage.getItem("user_role"));

    const finalRole = adminRole || employeeRole || "";

    const user_designation = decryptData(localStorage.getItem('user_designation'));

    if (user_profile) {
      const expBase64 = /^data:image\/(png|jpg|jpeg|gif|bmp|webp|svg\+xml);base64,[A-Za-z0-9+/]+={0,2}$/;
      if (expBase64.test(user_profile)) {
        setProfilePic(user_profile);
        setIsUser(true);
      }
    }

    if (profileUrl) {
      const prefixBase64 = `data:image/png;base64,${profileUrl}`;
      const expBase64 = /^data:image\/(png|jpg|jpeg|gif|bmp|webp|svg\+xml);base64,[A-Za-z0-9+/]+={0,2}$/;
      if (expBase64.test(prefixBase64)) {
        setProfilePic(prefixBase64);
      }
    }

    setUserName(`${firstName} ${lastName}`.trim());
    setUserRole(finalRole);
  }, []);


  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setNotificationDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);
  useEffect(() => {
    if (isNotificationOpen) {
      setNotificationData((prev) =>
        prev.map((notification) => ({
          ...notification,
          isRead: true,
        }))
      );
    }
  }, [isNotificationOpen]);

  const handleBellClick = () => {
    // Show toast notification only if there are notifications
    setIsNotificationOpen((prev) => !prev);
    // if (notificationData.length > 0) {
    //   showToast(`You have ${notifications.length} new notification${notifications.length > 1 ? 's' : ''}!`, "info");
    // } else {
    //   showToast("No new notifications", "info");
    // }

    // Toggle notification dropdown
    setNotificationDropdownOpen(!notificationDropdownOpen);
    sessionStorage.setItem("show_notification_Data", false)
  };

  const handleNotificationClick = (notification) => {
    showToast(notification.message, "info");
    markNotificationRead(notification.id);
  };


  const handleLogout = async () => {
    setIsLoggingOut(true);

    try {
      const accessToken = localStorage.getItem('AccessToken');

      const response = await axiosInstance.post(
        `${config.API.FLASK_URL}/logout`,
        null,
        {
          headers: {
            'Content-Type': 'application/json',
            'Token': `${accessToken}`
          },
          validateStatus: () => true,
        }
      );

      if (response.status >= 400) {
        throw new Error('Logout request failed');
      }

      // Show success toast
      showToast("Logged out successfully!", "success");

      localStorage.clear();
      window.location.reload();
    } catch (error) {
      console.error('Error during logout:', error);
      // Show error toast
      showToast("Error during logout. Please try again.", "error");
      localStorage.clear();
      window.location.reload();
    } finally {
      setIsLoggingOut(false);
    }
  };

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 ">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={toggleSidebar}>
            {sidebarOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
          <span className="grid organization">
            <h1 className="text-l font-bold text-gray-800">
              {orgName}
            </h1>
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* Notification Bell with Dropdown */}
          <div className="relative" ref={notificationRef}>
            <button
              onClick={handleBellClick}
              className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >

              <Bell className="w-6 h-6 text-gray-600" />
              {notificationApi?.filter(n => !n.is_read).length > 0 && (
                <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-bold">
                    {notificationApi.filter(n => !n.is_read).length > 9
                      ? '9+'
                      : notificationApi.filter(n => !n.is_read).length}
                  </span>
                </div>
              )}

            </button>

            {/* Notification Dropdown */}
            {notificationDropdownOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-51 max-h-96 overflow-y-auto" style={{ zIndex: 51 }}>
                <div className="px-4 py-2 border-b border-gray-100 flex justify-between items-center sticky bg-white" style={{ top: "-8px" }}>
                  <h3 className="font-semibold text-sm text-gray-900">Notifications({notificationApi.filter(n => !n.is_read).length}/{notificationApi.length})</h3>
                  {notificationApi.length > 0 && userRole === "Admin" && (
                    <div className="flex gap-3">
                      <button
                        onClick={readAllNotifications}
                        disabled={
                          isReadingAll ||
                          notificationApi.filter(n => !n.is_read).length === 0
                        }
                        className={`text-xs flex items-center gap-1 
                          ${notificationApi.filter(n => !n.is_read).length === 0
                            ? "text-gray-400 cursor-not-allowed"
                            : "text-green-600 hover:text-green-800"
                          }`}
                      >
                        {isReadingAll ? (
                          <svg
                            className="animate-spin h-3 w-3"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            ></circle>
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8z"
                            ></path>
                          </svg>
                        ) : (
                          "Read All"
                        )}
                      </button>

                      <button
                        onClick={clearAllNotifications}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        Clear All
                      </button>
                    </div>
                  )}

                </div>

                {notificationApi.length === 0 ? (
                  <div className="px-4 py-3 text-sm text-gray-500 text-center">
                    No new notifications
                  </div>
                ) : (
                  notificationApi.map((notification) => (
                    <div
                      key={notification.id}
                      onClick={() => handleNotificationClick(notification)}
                      className={`w-full px-4 py-3 text-left cursor-pointer hover:bg-gray-50 border-b border-gray-400 last:border-b-0 ${!notification.is_read ? 'bg-blue-50' : ''}`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="text-sm text-gray-900 whitespace-normal break-all">{notification.message}</div>
                          <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                            <span>
                              {new Date(notification?.timestamp).toLocaleString("en-GB", {
                                day: "2-digit",
                                month: "long",
                                year: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                                hour12: true,
                              }).replace(",", " -")}
                            </span>

                            {!notification.is_read && (
                              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                            )}
                          </div>
                        </div>
                        {userRole === "Admin" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              removeNotification(notification.id);
                            }}
                            className="text-gray-400 hover:text-red-500 ml-2"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>

                  ))
                )}
              </div>
            )}
          </div>

          <div className="relative" ref={dropdownRef}>
            <button
              onClick={toggleDropdown}
              className="flex items-center gap-3 hover:bg-gray-50 rounded-lg p-2 transition-colors"
              disabled={isLoggingOut}
            >
              <div className={isUser ? "userProfile" : "AdminProfile"}>
                {profilePic ? (
                  <img
                    src={profilePic}
                    className="profile w-10 h-10 rounded-full object-cover"
                    alt="Profile Picture"
                    title="Profile"
                  />
                ) : (
                  <div className="bg-blue-700 text-white w-10 h-10 rounded-full flex items-center justify-center text-lg font-semibold">
                    {userName?.charAt(0).toUpperCase()}
                  </div>
                )}

              </div>
              <div className="text-right">
                <p className="font-semibold text-sm">{userName || "User"}</p>
                <p className="text-xs text-gray-500">{userRole || "Role"}</p>
              </div>
              <ChevronDown
                className={`w-4 h-4 text-gray-400 transition-transform ${dropdownOpen ? "rotate-180" : ""
                  }`}
              />
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50" style={{ zIndex: 51 }}>
                <div className="px-4 py-2 border-b border-gray-100">
                  <p className="font-semibold text-sm text-gray-900">{userName || "User"}</p>
                  <p className="text-xs text-gray-500">{userRole || "Role"}</p>
                </div>

                <button
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  onClick={() => {
                    setDropdownOpen(false);
                    navigate("/settings");
                  }}
                >
                  <User className="w-4 h-4" />
                  Profile
                </button>

                <button
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <LogOut className="w-4 h-4" />
                  {isLoggingOut ? "Logging out..." : "Logout"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;