// hooks/useServerData.js
import { useState, useEffect, useContext } from 'react';
import { Backupindex } from '../Context/Backupindex';
import config from '../config';
import axios from 'axios';
import axiosInstance from '../axiosinstance';
import { NotificationContext } from "../Context/NotificationContext";
import { useJobs } from '../Components/Jobs/JobsContext';

const useServerData = (options = {}) => {
  const [serverData, setServerData] = useState([]);
  const [selectedEndpoint, setSelectedEndpoint] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { checkApi } = useContext(NotificationContext);
  const { refreshClients } = useJobs();

  const { forceClientNodes = false } = options;

  const fetchServerData = async () => {
    setLoading(true);
    setError(null);

    try {
      const clintApi = `${config.API.Server_URL}/restore_nodes`;
      const nodesApi = `${config.API.Server_URL}/clientnodes`;
      const usedApi = forceClientNodes ? nodesApi : (checkApi ? clintApi : nodesApi);

      const response = await axiosInstance.get(usedApi, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = response.data;

      // ✅ Sort by agent name
      const sortedData = data.result.sort((a, b) => {
        if (a.agent.toLowerCase() < b.agent.toLowerCase()) return -1;
        if (a.agent.toLowerCase() > b.agent.toLowerCase()) return 1;
        return 0;
      });

      // ✅ Remove duplicates by agent
      const seenAgents = new Set();
      const uniqueSortedData = sortedData.filter((item) => {
        if (seenAgents.has(item.agent)) {
          return false;
        } else {
          seenAgents.add(item.agent);
          return true;
        }
      });

      setServerData(uniqueSortedData);
      if (uniqueSortedData?.length > 0) {
        setSelectedEndpoint(uniqueSortedData);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    refreshClients();
    fetchServerData();
  }, []);

  return { serverData, selectedEndpoint, loading, error, refetch: fetchServerData };
};

export default useServerData;
