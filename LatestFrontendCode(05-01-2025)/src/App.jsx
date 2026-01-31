import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, MemoryRouter, Await } from 'react-router-dom';
import { JobsProvider } from "./Components/Jobs/JobsContext";
import LoginPage from "./Components/Login/LoginPage";
import Dashboard from "./Components/Dashboard/Dashboard";
import { AuthProvider, useAuth } from './AuthContext';
import Endpoint from './Components/Endpoint/Endpoint';
import Layout from './Components/Dashboard/Layout';
import ToastProvider from './ToastProvider';
import ForgotPassword from './Components/ForgetPassword/ForgetPassword';
import ProgressBarChart from './Components/Progress/ProgressBarChart';
import Backup from './Components/Backup/Backup'
import Restore from './Components/Restore/Restore';
import ExecutedJobs from './Components/Reports/Jobs/ExecutedJobs';
import SuccessfullJobs from './Components/Reports/Jobs/SuccessfullJobs';
import FailedJobs from './Components/Reports/Jobs/FailedJobs';
import Server from './Components/Reports/Server';
import ReportManager from './Components/Reports/ReportManager';
import ReportLayout from './Components/Reports/ReportLayout';
import { BackupProvider } from './Context/Backupindex';
import BackupLogs from './Components/Reports/BackupLogs';
import PairedEndpoints from './Components/Reports/PairedEndpoints';
import LicenseReport from './Components/Reports/LicenseReport';
import UserList from './Components/Reports/UserList';
import ClientReport from './Components/Reports/ClientReport';
import Pairing from './Components/Pairing/Pairing';
import Account from './Components/Settings/Account';
import { SyncDataProvider } from './Context/SyncDataContext';
import SupportPage from './Components/Support/Support';
import UserManager from './Components/CreateUser/UserManager'
import ChatbotPage from './Components/Support/ChatbotPage';
import ChatBot from './Components/Support/ChatBot';
import SystemLogs from './Components/Reports/Logs/SystemLogs';
import EventLogs from './Components/Reports/Logs/EventLogs';
import TaskLogs from './Components/Reports/Logs/TaskLogs';
import AppProviders from "./Context/AppProviders";
import { ensureSession } from './axiosinstance';
import useInactivityLogout from "./useInactivityLogout";
import InactivityWarningModal from './InactivityWarningModal';

function App() {
  return (
    <ToastProvider>
      <MemoryRouter>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </MemoryRouter>
    </ToastProvider>
  );
}

// Main app content with conditional context providers
function AppContent() {
  React.useEffect(() => {
    if (window.top !== window.self) {
      window.top.location = window.location;
    }
  }, []);

  React.useEffect(() => {
    const init = async () => {
      try {
        await ensureSession()
      } catch (error) {
        console.error(error)
      }
    }
    init()
  }, [])
  // Always call hooks in the same order - no early returns before hooks
  const authContext = useAuth();
  const [contextReady, setContextReady] = React.useState(false);

  // Effect hook always called consistently
  React.useEffect(() => {
    if (authContext?.isLoggedIn) {
      // Small delay to ensure auth is fully initialized
      const timer = setTimeout(() => {
        setContextReady(true);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setContextReady(false);
    }
  }, [authContext?.isLoggedIn]);

  // Now handle loading/error states after all hooks are called
  // if (!authContext) {
  //   return <div className="flex items-center justify-center h-screen">
  //     <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
  //       <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
  //         style={{ animation: 'oceanSlide 3s infinite' }} />
  //       <style>{`
  //     @keyframes oceanSlide {
  //       0% { transform: translateX(-150%); }
  //       66% { transform: translateX(0%); }
  //       100% { transform: translateX(150%); }
  //     }
  //   `}</style>
  //     </div>
  //   </div>;
  // }


  if (!authContext) {
    return <div className="flex items-center justify-center h-screen bg-gray-50">
      <div className="relative w-96 h-4 bg-gradient-to-r from-blue-100 to-blue-200 rounded-2xl overflow-hidden shadow-lg">
        <div
          className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600 w-3/5 rounded-2xl transform -translate-x-full"
          style={{ animation: 'oceanSlide 3s infinite' }}
        />

        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-sm font-bold text-white tracking-wide z-10 mix-blend-difference">
            LOADING
            <span
              className="inline-block ml-1"
              style={{ animation: 'dots 1.5s infinite steps(3, end)' }}
            >
              ...
            </span>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes oceanSlide {
          0% { transform: translateX(-150%); }
          66% { transform: translateX(0%); }
          100% { transform: translateX(150%); }
        }
        
        @keyframes dots {
          0% { content: ''; }
          33% { content: '.'; }
          66% { content: '..'; }
          100% { content: '...'; }
        }
      `}</style>
    </div>
  }

  const { isLoggedIn } = authContext;

  // Not logged in - show routes without context providers
  if (!isLoggedIn) {
    return <AppRoutes />;
  }

  // Logged in but contexts not ready
  // if (!contextReady) {
  //   return <div className="flex items-center justify-center h-screen">
  //     <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
  //       <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
  //         style={{ animation: 'oceanSlide 3s infinite' }} />
  //       <style>{`
  //     @keyframes oceanSlide {
  //       0% { transform: translateX(-150%); }
  //       66% { transform: translateX(0%); }
  //       100% { transform: translateX(150%); }
  //     }
  //   `}</style>
  //     </div>
  //   </div>;
  // }

  if (!contextReady) {
    return <div className="flex items-center justify-center h-screen bg-gray-50">
      <div className="relative w-96 h-4 bg-gradient-to-r from-blue-100 to-blue-200 rounded-2xl overflow-hidden shadow-lg">
        <div
          className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600 w-3/5 rounded-2xl transform -translate-x-full"
          style={{ animation: 'oceanSlide 3s infinite' }}
        />

        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-sm font-bold text-white tracking-wide z-10 mix-blend-difference">
            LOADING
            <span
              className="inline-block ml-1"
              style={{ animation: 'dots 1.5s infinite steps(3, end)' }}
            >
              ...
            </span>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes oceanSlide {
          0% { transform: translateX(-150%); }
          66% { transform: translateX(0%); }
          100% { transform: translateX(150%); }
        }
        
        @keyframes dots {
          0% { content: ''; }
          33% { content: '.'; }
          66% { content: '..'; }
          100% { content: '...'; }
        }
      `}</style>
    </div>
  }

  // Everything ready - provide all contexts
  return (
    <AppProviders>
      <BackupProvider>
        <JobsProvider>
          <SyncDataProvider>
            {/* <AppRoutes /> */}
            <AuthenticatedApp />
          </SyncDataProvider>
        </JobsProvider>
      </BackupProvider>
    </AppProviders>
  );
}

function AppRoutes() {
  // Always call hooks first, in consistent order
  const authContext = useAuth();
  const location = useLocation();
  const intervalRef = React.useRef(null);

  // All hooks called before any conditional logic
  // React.useEffect(() => {
  //   // Clear any existing interval
  //   if (intervalRef.current) {
  //     clearInterval(intervalRef.current);
  //     intervalRef.current = null;
  //   }

  //   if (authContext?.isLoggedIn && authContext.checkTokenValidity) {
  //     authContext.checkTokenValidity();
  //     intervalRef.current = setInterval(() => {
  //       authContext.checkTokenValidity();
  //     }, 12000);
  //   }

  //   return () => {
  //     if (intervalRef.current) {
  //       clearInterval(intervalRef.current);
  //       intervalRef.current = null;
  //     }
  //   };
  // }, [authContext?.isLoggedIn, authContext?.checkTokenValidity]);

  // Handle loading state after hooks
  // if (!authContext) {
  //   return <div className="flex items-center justify-center h-screen">
  //     <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
  //       <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
  //         style={{ animation: 'oceanSlide 3s infinite' }} />
  //       <style>{`
  //     @keyframes oceanSlide {
  //       0% { transform: translateX(-150%); }
  //       66% { transform: translateX(0%); }
  //       100% { transform: translateX(150%); }
  //     }
  //   `}</style>
  //     </div>
  //   </div>;
  // }

  if (!authContext) {
    return <div className="flex items-center justify-center h-screen bg-gray-50">
      <div className="relative w-96 h-4 bg-gradient-to-r from-blue-100 to-blue-200 rounded-2xl overflow-hidden shadow-lg">
        <div
          className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600 w-3/5 rounded-2xl transform -translate-x-full"
          style={{ animation: 'oceanSlide 3s infinite' }}
        />

        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-sm font-bold text-white tracking-wide z-10 mix-blend-difference">
            LOADING
            <span
              className="inline-block ml-1"
              style={{ animation: 'dots 1.5s infinite steps(3, end)' }}
            >
              ...
            </span>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes oceanSlide {
          0% { transform: translateX(-150%); }
          66% { transform: translateX(0%); }
          100% { transform: translateX(150%); }
        }
        
        @keyframes dots {
          0% { content: ''; }
          33% { content: '.'; }
          66% { content: '..'; }
          100% { content: '...'; }
        }
      `}</style>
    </div>
  }

  const { isLoggedIn } = authContext;

  // If not logged in, only show login/forgot password pages
  if (!isLoggedIn) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  // Logged in - show all routes with Layout
  const routesContent = (
    <Routes>
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="/forgot-password" element={<Navigate to="/" replace />} />
      <Route path="/" element={<Dashboard />} />
      <Route path="/backup" element={<Backup />} />
      <Route path="/users" element={<UserManager />} />
      <Route path="/progress" element={<ProgressBarChart />} />
      <Route path="/endpoints" element={<Endpoint />} />
      <Route path="/pairing" element={<Pairing />} />
      <Route path="/restore" element={<Restore />} />
      <Route path="/settings" element={<Account />} />
      <Route path="/chatbot" element={<ChatBot />} />
      <Route path="/support" element={<SupportPage />} />

      {/* Report Routes */}
      <Route path="/report" element={<ReportLayout><Server /></ReportLayout>} />
      <Route path="/executedJob" element={<ExecutedJobs />} />
      <Route path="/successfulJob" element={<SuccessfullJobs />} />
      <Route path="/failedJob" element={<FailedJobs />} />
      <Route path="/backup-logs" element={<ReportLayout><BackupLogs /></ReportLayout>} />
      <Route path="/system-logs" element={<ReportLayout><SystemLogs /></ReportLayout>} />
      <Route path="/event-logs" element={<ReportLayout><EventLogs /></ReportLayout>} />
      <Route path="/task-logs" element={<ReportLayout><TaskLogs /></ReportLayout>} />
      <Route path="/portal-user-logs" element={<ReportLayout><UserList /></ReportLayout>} />
      <Route path="/license-info" element={<ReportLayout><LicenseReport /></ReportLayout>} />
      <Route path="/paired-endpoints" element={<ReportLayout><PairedEndpoints /></ReportLayout>} />
      <Route path="/endpoint-overview" element={<ReportLayout><ClientReport /></ReportLayout>} />
    </Routes>
  );

  return <Layout>{routesContent}</Layout>;
}
function AuthenticatedApp() {
  const { showWarning, secondsLeft } = useInactivityLogout();

  return (
    <>
      <AppRoutes />
      {showWarning && (
        <InactivityWarningModal secondsLeft={secondsLeft} />
      )}
    </>
  );
}

export default App;