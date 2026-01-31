// hooks/useServerData.js
import { useState, useEffect } from "react";
import config from "../../config";
import axios from "axios";
import axiosInstance from "../../axiosinstance";
import CryptoJS from "crypto-js";

function encryptData(data) {
  const encryptedData = CryptoJS.AES.encrypt(data, "1234567890").toString();

  return encryptedData;
}

export const useServerData = () => {
  const [serverData, setServerData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);



  const fetchServerData = async (showLoader = true) => {
    if (showLoader) setLoading(true); // Only show loader if true
    setError(null);

    try {
      const response = await axiosInstance.get(`${config.API.Server_URL}/serverreport`, {
        headers: {
          "Content-Type": "application/json"
        },
      });
      setServerData(response.data);

      if (response.data?.server_version) {
        localStorage.setItem("serverVersion", encryptData(response.data.server_version));
      }

    } catch (error) {
      console.error("Error fetching server data:", error);

      // Enhanced error handling
      let errorMessage = "Failed to fetch data";
      if (error.response) {
        switch (error.response.status) {
          case 401:
            errorMessage = "Authentication required";
            break;
          case 403:
            errorMessage = "Access denied";
            break;
          case 404:
            errorMessage = "Server report endpoint not found";
            break;
          case 500:
            errorMessage = "Server error occurred";
            break;
          default:
            errorMessage = error.response.data?.message || `Server error: ${error.response.status}`;
        }
      } else if (error.request) {
        errorMessage = "Could not connect to the server";
      } else {
        errorMessage = error.message;
      }

      setError(errorMessage);

    } finally {
      if (showLoader) setLoading(false);
    }
  };

  useEffect(() => {
    fetchServerData(true);
  }, []);




  const diskData = Array.isArray(serverData?.disk)
    ? serverData.disk.map((diskItem) => ({
      name: diskItem.device,
      used: parseFloat(diskItem.used.replace(" GB", "")) || 0,
      used_raw: diskItem.used || '0 GB',
      free: parseFloat(diskItem.free.replace(" GB", "")) || 0,
      free_raw: diskItem.free || '0 GB',
      total: parseFloat(diskItem.total.replace(" GB", "")) || 0,
      total_raw: diskItem.total || '0 GB',
    }))
    : [];


  const memoryChart = serverData?.memory ? {
    labels: ['Used', 'Available'],
    datasets: [{
      data: [
        parseFloat(serverData.memory.used.replace(' GB', '')) || 0,
        parseFloat(serverData.memory.available.replace(' GB', '')) || 0
      ],
      backgroundColor: ['#3b82f6', '#10b981'],
      borderWidth: 1,
    }]
  } : {
    labels: ['Used', 'Available'],
    datasets: [{
      data: [0, 0],
      backgroundColor: ['#3b82f6', '#10b981'],
      borderWidth: 1,
    }]
  };

  const memoryData = serverData?.memory ? {
    used: serverData.memory.used,
    available: serverData.memory.available,
    total: serverData.memory.total,
    percentage: serverData.memory.percentage || 0
  } : {
    used: 0,
    available: 0,
    total: 0,
    percentage: 0
  };

  const processorChart = serverData?.processor ? {
    labels: ['Usage', 'Idle'],
    datasets: [{
      data: [
        serverData.processor.usage, 100 - serverData.processor.usage
      ],
      backgroundColor: ['#3b82f6', '#10b981'],
      borderWidth: 1,
    }]
  } : {
    labels: ['Usage', 'Idle'],
    datasets: [{
      data: [0, 0],
      backgroundColor: ['#3b82f6', '#10b981'],
      borderWidth: 1,
    }]
  };

  const processorData = serverData?.processor ? {
    physical: serverData.processor.physical,
    count: serverData.processor.count,
    usage: serverData.processor.usage,
  } : {
    physical: 0,
    count: 0,
    usage: 0,
  };

  const networkData = serverData?.network ? {
    received: parseFloat(serverData.network.received.replace(' MB', '')) || 0,
    sent: parseFloat(serverData.network.sent.replace(' MB', '')) || 0,
    receivedRaw: serverData.network.received,
    sentRaw: serverData.network.sent,
    totalUsage: (parseFloat(serverData.network.received.replace(' MB', '')) || 0) +
      (parseFloat(serverData.network.sent.replace(' MB', '')) || 0)
  } : {
    received: 0,
    sent: 0,
    receivedRaw: '0 MB',
    sentRaw: '0 MB',
    totalUsage: 0
  };

  const connectedNodesCount = serverData?.server_connected_nodes?.result?.length || 0;

  return {
    serverData,
    diskData,
    memoryChart,
    memoryData,
    processorChart,
    processorData,
    connectedNodesCount,
    networkData,
    loading,
    error,
    refetch: fetchServerData,
  };
};


