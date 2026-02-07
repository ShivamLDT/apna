// contexts/ToastProvider.jsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ToastContext = createContext();

// Custom hook to use toast
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

const ToastProvider = ({ children }) => {
  const [showCustomError, setShowCustomError] = useState(false);
  const [internetSpeed, setInternetSpeed] = useState(null);
  const [showLowBandwidthWarning, setShowLowBandwidthWarning] = useState(false);
  const [toastId, setToastId] = useState(null);

  const showToast = (message, type = "success", autoClose = 5000, options = {}) => {
    const opts = {
      autoClose,
      ...options,
      toastId: options.toastId !== undefined ? options.toastId : (typeof message === "string" ? message : undefined),
    };
    switch (type) {
      case "success":
        toast.success(message, opts);
        break;
      case "error":
        toast.error(message, opts);
        break;
      case "info":
        toast.info(message, opts);
        break;
      case "warning":
        toast.warning(message, opts);
        break;
      default:
        toast(message, opts);
    }
  };

  const role = localStorage.getItem("role");

  const handleOffline = () => {
    localStorage.clear();
    window.location.reload();
    showCustomErrorMessage(); // Show the custom error message when offline
  };

  const handleOnline = () => {
    setShowCustomError(false);
    showToast("Connection restored!", "success");
  };

  const showCustomErrorMessage = () => {
    setShowCustomError(true);
    showToast("Connection lost! Please check your internet connection.", "error");
  };


  const contextValue = {
    showToast,
    showCustomError,
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer
        position="top-center"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        style={{
          fontSize: '14px'
        }}
      />
    </ToastContext.Provider>
  );
};

export default ToastProvider;