import React, { useContext, useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import './Sidebar.css';
import {
  ChevronDown,
  ChevronRight,
  Server,
  Globe,
  Play,
  CheckCircle,
  XCircle,
  Archive,
  Users,
  FileText,
  Link,
  BarChart3,
  Menu,
  ScreenShare,
  CalendarCheck,
  ListTodo,
  X,
  Search
} from 'lucide-react';

import { Backupindex } from '../../Context/Backupindex';
import { NotificationContext } from "../../Context/NotificationContext";
import { UIContext } from '../../Context/UIContext';
const ReportSidebar = () => {
  const [isOverviewOpen, setIsOverviewOpen] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isActivityOpen, setIsActivityOpen] = useState(true);
  const { showBackuplog, setShowBackuplog } = useContext(UIContext);
  const { setIsSechduler, } = useContext(Backupindex);
  const { checkApi, setCheckApi, } = useContext(NotificationContext);
  const location = useLocation();

  // Close sidebar when route changes (mobile)
  useEffect(() => {
    setIsSidebarOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (location.pathname === '/backup-logs') {
      setCheckApi(true);
      setIsSechduler(true);
      setShowBackuplog(true)
    } else {
      setCheckApi(false);
    }
  }, [location.pathname, checkApi]);


  const overviewItems = [
    { label: "Server Overview", path: "/report", icon: Server },
    { label: "Endpoint Overview", path: "/endpoint-overview", icon: Globe },
  ];

  const activityItems = [
    { label: "System Logs", path: "/system-logs", icon: ScreenShare },
    { label: "Event Logs", path: "/event-logs", icon: CalendarCheck },
    { label: "Task Logs", path: "/task-logs", icon: ListTodo },
  ];

  const otherItems = [
    { label: "Backup/Restore Logs", path: "/backup-logs", icon: Archive },
    { label: "User List", path: "/portal-user-logs", icon: Users },
    { label: "License", path: "/license-info", icon: FileText },
    { label: "Paired Endpoints", path: "/paired-endpoints", icon: Link },
  ];

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <>
      <button
        className="menu-toggle"
        onClick={toggleSidebar}
        aria-label="Open reports menu"

      >
        <Menu size={20} />
      </button>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={closeSidebar}
        />
      )}

      <div
        className={`sidebar ${isSidebarOpen ? 'sidebar-open' : ''}`}
        style={{
          transform: isSidebarOpen ? 'translateX(0)' : undefined
        }}
      >
        <button
          className="Sideclose-button"
          onClick={closeSidebar}
          aria-label="Close menu"
        >
          <X size={20} />
        </button>

        <div className="logo">Reports</div>
        <hr />
        <ul className="menu">
          {/* Overview Section */}
          <li className="dropdown-item">
            <div
              className={`dropdown-header ${isOverviewOpen ? 'open' : ''}`}
              onClick={() => setIsOverviewOpen(!isOverviewOpen)}
            >
              <div className="dropdown-label">
                <BarChart3 size={16} />
                <span>Overview</span>
              </div>
              {isOverviewOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </div>

            {isOverviewOpen && (
              <ul className="dropdown-menu">
                {overviewItems.map(({ label, path, icon: Icon }) => (
                  <li key={path}>
                    <NavLink
                      to={path}
                      className={({ isActive }) => (isActive ? "active" : "")}
                      onClick={closeSidebar}
                    >
                      <Icon size={16} />
                      {label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            )}
          </li>

          {/* Activity Logs Section */}
          <li className="dropdown-item">
            <div
              className={`dropdown-header ${isActivityOpen ? 'open' : ''}`}
              onClick={() => setIsActivityOpen(!isActivityOpen)}
            >
              <div className="dropdown-label">
                <Archive size={16} />
                <span>Activity Logs</span>
              </div>
              {isActivityOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </div>

            {isActivityOpen && (
              <ul className="dropdown-menu">
                {activityItems.map(({ label, path, icon: Icon }) => (
                  <li key={path}>
                    <NavLink
                      to={path}
                      className={({ isActive }) =>
                        isActive || location.pathname === "/activity-logs" && path === "/activity-logs"
                          ? "active"
                          : ""
                      }
                      onClick={closeSidebar}
                    >
                      <Icon size={16} />
                      {label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            )}
          </li>
          {/* Other Items */}
          {otherItems.map(({ label, path, icon: Icon }) => (
            <li key={path}>
              <NavLink
                to={path}
                className={({ isActive }) => (isActive ? "active" : "")}
                onClick={closeSidebar}
              >
                <Icon size={16} />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
};

export default ReportSidebar;