import React, { useState, useEffect } from 'react';
import { RefreshCw, Server, Search, Database, RotateCcw } from 'lucide-react';
import Backupp from './Backupp';
import Restorepp from './Restorepp';
import config from '../../config';
import ServerInfoPopup from './ServerInfoPopup';
import axios from "axios";
import axiosInstance from '../../axiosinstance';
import { useLocation } from 'react-router-dom';
const ProgressBarChart = () => {
  // State to handle menu page selection (Backup or Restore)
  const [currentPage, setCurrentPage] = useState('Backup'); // Default to 'Backup'

  // Other state variables
  const [searchQuery, setSearchQuery] = useState('');
  const [showServerPopup, setShowServerPopup] = useState(false);
  const [serverData, setServerData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const location = useLocation();
  // Switch between Backup and Restore pages
  const handlePageSwitch = (page) => {
    setCurrentPage(page);
    setProgress(0); // Reset progress when switching pages
  };

  const handleShowServerInfo = () => {
    setShowServerPopup(true);
  };


  useEffect(() => {
    if (location.state?.tab === "Restore") {
      setCurrentPage("Restore");
    }
  }, [location]);

  // Simulate server data fetching

  useEffect(() => {
    let intervalId;

    const fetchServerInfo = async () => {
      try {
        const response = await axiosInstance.get(`${config.API.Server_URL}/serverreport`);
        setServerData(response.data);
      } catch (error) {
        console.error('Error fetching server info:', error);
      }
    };

    if (showServerPopup) {
      setLoading(true);
      fetchServerInfo().finally(() => setLoading(false));
      // intervalId = setInterval(fetchServerInfo, 30000);
    }

    return () => {
      clearInterval(intervalId);
    };
  }, [showServerPopup]);

  // Simulate progress updates
  useEffect(() => {
    if (loading) {
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return prev + Math.random() * 12;
        });
      }, 100);

      return () => clearInterval(progressInterval);
    }
  }, [loading]);


  const renderBackupPage = () => (
    <div className="backup-page">
      <Backupp searchQuery={searchQuery} />
    </div>
  );

  const renderRestorePage = () => (
    <div className="restore-page">
      <Restorepp searchQuery={searchQuery} />
    </div>
  );

  const handleRefresh = () => {
    setLoading(true);

    // Only clear backup progress; preserve restore progress so it survives refresh
    if (currentPage === 'Backup') {
      localStorage.removeItem('storedAgentDataa');
      localStorage.removeItem('storedAnimatedDataa');
      localStorage.removeItem('storedJobFiles');
    }
    // Restore data (storedRestoreAgentData, storedRestoreAnimatedData) is NOT cleared
    // so in-progress restore progress bar remains visible after refresh
    setProgress(0);

    // Simulate refresh process
    setTimeout(() => {
      setLoading(false);
      setProgress(100);
    }, 2000);
  };

  // Loading spinner component
  if (loading && !showServerPopup) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-sm w-full mx-4">
          <div className="text-center space-y-4">
            <RefreshCw className="w-12 h-12 text-blue-600 mx-auto animate-spin" />
            <h3 className="text-lg font-semibold text-gray-900">Loading...</h3>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${Math.min(progress, 100)}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">{Math.round(progress)}% Complete</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`w-full`}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-4 space-y-4 sm:space-y-0">

            {/* Page Navigation */}
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => handlePageSwitch('Backup')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${currentPage === 'Backup'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
                  }`}
              >
                Backup
              </button>
              <button
                onClick={() => handlePageSwitch('Restore')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${currentPage === 'Restore'
                  ? 'bg-green-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
                  }`}
              >
                Restore
              </button>
            </div>

            {/* Search and Actions */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
              {/* Search Input */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button
                  onClick={handleRefresh}
                  disabled={loading}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  <span className="hidden sm:inline">Refresh</span>
                </button>

                <button
                  onClick={handleShowServerInfo}
                  className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200"
                >
                  <Server className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">Server</span>
                </button>
              </div>
            </div>
          </div>

          {/* Progress Bar - Shows when loading */}
          {loading && (
            <div className="pb-4">
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-1 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${Math.min(progress, 100)}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="pt-2">
        {currentPage === 'Backup' ? renderBackupPage() : renderRestorePage()}
      </div>

      {/* Server Info Popup */}
      {/* {showServerPopup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Server className="w-5 h-5 mr-2" />
                  Server Information
                </h3>
                <button
                  onClick={() => setShowServerPopup(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              
              {serverData ? (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Name:</span>
                    <span className="font-medium text-green-600">{serverData.system.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Manufacturer:</span>
                    <span className="font-medium">{serverData.system.manufacturer}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Memory:</span>
                    <span className="font-medium">{serverData.memory}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">CPU:</span>
                    <span className="font-medium">{serverData.cpu}</span>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="w-6 h-6 text-blue-600 animate-spin" />
                  <span className="ml-2 text-gray-600">Loading server data...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )} */}

      {showServerPopup && (
        <ServerInfoPopup
          serverData={serverData}
          loading={loading}
          onClose={() => setShowServerPopup(false)}
        />
      )}
    </div>
  );
};

export default ProgressBarChart;