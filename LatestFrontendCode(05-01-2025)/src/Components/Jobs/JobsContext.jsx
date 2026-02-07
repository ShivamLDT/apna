// context/JobsContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import config from "../../config";
import { useLocation } from "react-router-dom";
import axiosInstance from "../../axiosinstance";

const JobsContext = createContext();
export const useJobs = () => useContext(JobsContext);

export const JobsProvider = ({ children }) => {
  const [topJobs, setTopJobs] = useState([]);
  const [totalTopJobs, setTotalTopJobs] = useState(0);

  const [jobsByNode, setJobsByNode] = useState([]);
  const [jobCounts, setJobCounts] = useState({ success: 0, failed: 0, total: 0 });
  const [jobsByRepository, setJobsByRepository] = useState([]);
  const [executedJobs, setExecutedJobs] = useState([]);

  const [loading, setLoading] = useState(false);
  const [repoLoading, setRepoLoading] = useState(true);
  const [error, setError] = useState("");
  const location = useLocation();
  const allowedPaths = ["/", "/executedJob", "/successfulJob", "/failedJob"]

  // const fetchAllJobs = async () => {
  //   setLoading(true);
  //   try {
  //     const [successResponse, failedResponse] = await Promise.all([
  //       axiosInstance.get(`${config.API.Server_URL}/api/getsuccessjobs`),
  //       axiosInstance.get(`${config.API.Server_URL}/api/getfailedjobs`),
  //     ]);

  //     const successJobs = successResponse?.data?.successjobs || [];
  //     const failedJobs = failedResponse?.data?.failedjobs || [];
  //     /** ---------------- JOB COUNTS ---------------- **/
  //     const totalSuccess = successJobs.reduce((acc, curr) => acc + curr.data.length, 0);
  //     const uniqueFailed = failedJobs.reduce((acc, curr) => {
  //       if (Array.isArray(curr.data)) {
  //         const uniqueData = curr.data.filter(
  //           (job, index, self) =>
  //             self.findIndex(
  //               (j) =>
  //                 j.job_name === job.job_name &&
  //                 j.error_desc === job.error_desc &&
  //                 j.missed_time === job.missed_time
  //             ) === index
  //         );
  //         return acc.concat(uniqueData);
  //       }
  //       return acc;
  //     }, []);
  //     const totalFailed = uniqueFailed.length;
  //     setJobCounts({ success: totalSuccess, failed: totalFailed, total: totalSuccess + totalFailed });

  //     /** ---------------- JOBS BY NODE ---------------- **/
  //     const nodeMap = new Map();
  //     successJobs.forEach(({ nodeName, data }) => {
  //       if (!nodeMap.has(nodeName)) nodeMap.set(nodeName, { node: nodeName, success: 0, failed: 0 });
  //       nodeMap.get(nodeName).success += data.length;
  //     });
  //     failedJobs.forEach(({ nodeName, data }) => {
  //       if (!nodeMap.has(nodeName)) nodeMap.set(nodeName, { node: nodeName, success: 0, failed: 0 });
  //       const uniqueFails = Array.isArray(data)
  //         ? data.filter(
  //           (job, index, self) =>
  //             self.findIndex(
  //               (j) =>
  //                 j.job_name === job.job_name &&
  //                 j.error_desc === job.error_desc &&
  //                 j.missed_time === job.missed_time
  //             ) === index
  //         )
  //         : [];
  //       nodeMap.get(nodeName).failed += uniqueFails.length;
  //     });
  //     setJobsByNode(Array.from(nodeMap.values()));

  //     /** ---------------- JOBS BY REPOSITORY ---------------- **/
  //     const repoCounts = {};
  //     successJobs.forEach(({ data }) => {
  //       if (Array.isArray(data)) {
  //         data.forEach((job) => {
  //           const repo = job.job_repo || "Unknown";
  //           repoCounts[repo] = (repoCounts[repo] || 0) + 1;
  //         });
  //       }
  //     });
  //     const repoData = Object.entries(repoCounts).map(([repo, count]) => ({ repo, count }));
  //     setJobsByRepository(repoData);

  //   } catch (err) {
  //     console.error("Error fetching jobs:", err);
  //     setError("Failed to fetch jobs");
  //   } finally {
  //     setLoading(false);
  //     setRepoLoading(false);
  //   }
  // };


  const fetchAllJobs = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.post(
        `${config.API.Server_URL}/api/getfailedsuccessjobs`,
        { action: "count" }
      );

      const statsData = response?.data?.[0]?.data || [];
      const counts = response?.data?.[0]?.counts || null;
      const restoreCounts = response?.data?.[0]?.restore_counts || { success: 0, failed: 0 };

      /** ---------------- JOB COUNTS ---------------- **/
      let totalSuccessJobs = 0;
      let totalFailedJobs = 0;

      /** ---------------- JOBS BY NODE ---------------- **/
      const nodeMap = new Map();

      /** ---------------- JOBS BY REPOSITORY (SUCCESS ONLY) ---------------- **/
      const repoCounts = {};

      statsData.forEach(({ nodeName, status, total_success, total_failed }) => {
        if (!nodeMap.has(nodeName)) {
          nodeMap.set(nodeName, { node: nodeName, success: 0, failed: 0 });
        }

        const nodeData = nodeMap.get(nodeName);

        if (status === "success" && total_success) {
          nodeData.success += total_success.total || 0;
          totalSuccessJobs += total_success.total || 0;

          // ✅ Repository counts ONLY from success
          Object.entries(total_success).forEach(([repo, count]) => {
            if (repo !== "total") {
              repoCounts[repo] = (repoCounts[repo] || 0) + count;
            }
          });
        }

        if (status === "failed" && total_failed) {
          nodeData.failed += total_failed.total_failed || 0;
          totalFailedJobs += total_failed.total_failed || 0;
          // ❌ Do NOT touch repoCounts here
        }
      });

      const restoreSuccess = Number(restoreCounts?.success || 0);
      const restoreFailed = Number(restoreCounts?.failed || 0);
      const fallbackCounts = {
        backup: {
          success: totalSuccessJobs,
          failed: totalFailedJobs,
          total: totalSuccessJobs + totalFailedJobs,
        },
        restore: {
          success: restoreSuccess,
          failed: restoreFailed,
          total: restoreSuccess + restoreFailed,
        },
      };
      const combinedCounts = counts?.combined || {
        success: fallbackCounts.backup.success + fallbackCounts.restore.success,
        failed: fallbackCounts.backup.failed + fallbackCounts.restore.failed,
        total: fallbackCounts.backup.total + fallbackCounts.restore.total,
      };
      setJobCounts({
        success: combinedCounts.success,
        failed: combinedCounts.failed,
        total: combinedCounts.total,
        backup: counts?.backup || fallbackCounts.backup,
        restore: counts?.restore || fallbackCounts.restore,
      });
      setJobsByNode(Array.from(nodeMap.values()));

      const repoData = Object.entries(repoCounts).map(([repo, count]) => ({
        repo,
        count,
      }));

      setJobsByRepository(repoData);

    } catch (err) {
      console.error("Error fetching jobs:", err);
      setError("Failed to fetch jobs");
    } finally {
      setLoading(false);
      setRepoLoading(false);
    }
  };



  /** Top Jobs fetch remains separate */
  const fetchTopJobs = async () => {
    try {
      const response = await axiosInstance.post(`${config.API.Server_URL}/api/top10jobs`, {}, {
        headers: { "Content-Type": "application/json", token: localStorage.getItem("accessToken") },
      });
      const jobs = response.data.top10 || [];
      setTopJobs(jobs);
      setTotalTopJobs(jobs.length);
    } catch (err) {
      setError("Failed to fetch top jobs");
    }
  };

  /** Executed Jobs (separate API) */
  // const fetchExecutedJobs = async () => {
  //   try {
  //     const response = await axiosInstance.get(`${config.API.Server_URL}/api/getfailedsuccessjobs`, {
  //       headers: { "Content-Type": "application/json", Job: localStorage.getItem("AccessToken") },
  //     });
  //     const jobs = response.data?.[0]?.data || [];

  //     setExecutedJobs(jobs);
  //   } catch (err) {
  //     setError("Failed to load executed jobs.");
  //   }
  // };

  // Refresh Clients

  const refreshClients = async () => {
    try {
      const response = await axiosInstance.get(`${config.API.Server_URL}/refreshclientnodes`, {
        headers: { "Content-Type": "application/json" },
      });

    } catch (error) {
      console.error(error)
    }
  }

  useEffect(() => {
    fetchAllJobs();
    fetchTopJobs();
    // fetchExecutedJobs();
    refreshClients();
  }, []);

  return (
    <JobsContext.Provider
      value={{
        topJobs,
        totalTopJobs,
        jobCounts,
        jobsByNode,
        jobsByRepository,
        executedJobs,
        loading,
        repoLoading,
        error,
        onerefetch: fetchTopJobs,
        tworefetch: fetchAllJobs,
        refreshClients
      }}
    >
      {children}
    </JobsContext.Provider>
  );
};
