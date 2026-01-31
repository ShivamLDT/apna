import React, { createContext, useState, useEffect, useContext } from 'react';
import config from '../../../config';
import axios from "axios";
import axiosInstance from '../../../axiosinstance';

const ExecutedJobsContext = createContext();

export const ExecutedJobsProvider = ({ children }) => {
    const [executedJobs, setExecutedJobs] = useState([]);
    const [counts, setCounts] = useState({ total: 0, success: 0, failed: 0 });


    const fetchExecutedJobs = async () => {
        try {
            const response = await axiosInstance.get(`${config.API.Server_URL}/api/getfailedsuccessjobs`, {
                headers: {
                    'Content-Type': 'application/json'
                },
            });

            const data = response.data;
            const jobs = data?.[0]?.data || [];
            setExecutedJobs(jobs);
            setCounts({
                total: jobs.length,
                success: jobs.filter(job => job.status === 'success').length,
                failed: jobs.filter(job => job.status === 'failed').length
            });
        } catch (error) {
            console.error("Failed to fetch executed jobs:", error);
        }
    };

    useEffect(() => {
        fetchExecutedJobs();
    }, []);

    return (
        <ExecutedJobsContext.Provider value={{ executedJobs, counts }}>
            {children}
        </ExecutedJobsContext.Provider>
    );
};

export const useExecutedJobs = () => useContext(ExecutedJobsContext);
