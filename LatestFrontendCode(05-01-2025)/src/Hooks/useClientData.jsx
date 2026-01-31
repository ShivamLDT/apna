// hooks/useClientData.js
import { useState, useEffect } from 'react';
import config from '../config';
import axios from 'axios';
import axiosInstance from '../axiosinstance';
import { useJobs } from '../Components/Jobs/JobsContext';

const useClientData = () => {
  const [clientData, setClientData] = useState([]);
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { refreshClients } = useJobs();

  const fetchClientData = async (showLoader = true) => {
    if (showLoader) setLoading(true); // Only show loader if true
    setError(null);

    try {
      const response = await axiosInstance.get(`${config.API.Server_URL}/clientnodes`, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = response.data; // axios auto-parses JSON
      setClientData(data);

      if (data.result?.length > 0) {
        setSelectedEndpoint(data.result);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      if (showLoader) setLoading(false);
    }
  };


  useEffect(() => {
    refreshClients();
    fetchClientData(true);
  }, []);

  return { clientData, selectedEndpoint, loading, error, refetch: fetchClientData };
};

export default useClientData;
