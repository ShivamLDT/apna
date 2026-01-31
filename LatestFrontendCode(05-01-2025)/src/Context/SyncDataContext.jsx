import React, { createContext, useContext, useState, useEffect } from 'react';
import config from '../config';
import axios from "axios";
import axiosInstance from '../axiosinstance';
import useSaveLogs from '../Hooks/useSaveLogs';

const SyncDataContext = createContext();

export const SyncDataProvider = ({ children }) => {
  const { userRole } = useSaveLogs();
  const [syncData, setSyncData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const accessToken = localStorage.getItem("AccessToken");

  const [isRefetching, setIsRefetching] = useState(false);

  const fetchSyncData = async (isManual = false) => {
    if (isManual) setIsRefetching(true);
    else setLoading(true);

    setError(null);

    try {
      const response = await axiosInstance.post(
        `${config.API.FLASK_URL}/sync`,
        {}, // no body needed
        {
          headers: {
            "Content-Type": "application/json",
            token: accessToken,
          },
        }
      );

      setSyncData(response.data.data); // axios parses JSON automatically
    } catch (err) {
      setError(err.response?.data?.message || err.message || "Unknown error");
    } finally {
      if (isManual) setIsRefetching(false);
      else setLoading(false);
    }
  };


  useEffect(() => {
    if (!userRole) return; 
    if (userRole.toLowerCase() === "employee") return; 

    fetchSyncData();
  }, [userRole]);

  return (
    <SyncDataContext.Provider
      value={{ syncData, loading, error, refetch: () => fetchSyncData(true), isRefetching }}
    >
      {children}
    </SyncDataContext.Provider>
  );



};

export const useSyncData = () => useContext(SyncDataContext);
