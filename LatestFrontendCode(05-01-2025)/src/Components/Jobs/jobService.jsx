// jobService.js
import config from "../../config";
import axios from "axios";
import axiosInstance from "../../axiosinstance";

export const fetchJobCounts = async () => {
  try {
    const [successResponse, failedResponse] = await Promise.all([
      axiosInstance.get(`${config.API.Server_URL}/api/getsuccessjobs`, {
        headers: { "Content-Type": "application/json" },
      }),
      axiosInstance.get(`${config.API.Server_URL}/api/getfailedjobs`, {
        headers: { "Content-Type": "application/json" },
      }),
    ]);

    const successJobs = successResponse.data.successjobs;
    const failedJobs = failedResponse.data.failedjobs;

    const totalSuccessCount = successJobs.reduce(
      (acc, curr) => acc + curr.data.length,
      0
    );

    const filteredFailedJobs = failedJobs.reduce((acc, curr) => {
      if (Array.isArray(curr.data)) {
        const uniqueData = curr.data.filter(
          (job, index, self) =>
            self.findIndex(
              (j) =>
                j.job_name === job.job_name &&
                j.error_desc === job.error_desc &&
                j.missed_time === job.missed_time
            ) === index
        );
        return acc.concat(uniqueData);
      }
      return acc;
    }, []);

    const totalFailedCount = filteredFailedJobs.length;
    const totalJobCount = totalSuccessCount + totalFailedCount;

    return {
      success: totalSuccessCount,
      failed: totalFailedCount,
      total: totalJobCount,
    };

  } catch (error) {
    console.error("Error fetching job data:", error);

    // Enhanced error handling
    if (error.response) {
      console.error("Server error:", error.response.status, error.response.data);
    } else if (error.request) {
      console.error("Network error - no response received");
    } else {
      console.error("Request setup error:", error.message);
    }

    return {
      success: 0,
      failed: 0,
      total: 0,
    };
  }
};

// jobService.js

export const fetchJobsByNode = async () => {
  try {
    const [successResponse, failedResponse] = await Promise.all([
      axiosInstance.get(`${config.API.Server_URL}/api/getsuccessjobs`, {
        headers: { "Content-Type": "application/json" },
      }),
      axiosInstance.get(`${config.API.Server_URL}/api/getfailedjobs`, {
        headers: { "Content-Type": "application/json" },
      }),
    ]);

    const successJobs = successResponse.data.successjobs;
    const failedJobs = failedResponse.data.failedjobs;

    const dataMap = new Map();

    // Count success jobs per node
    successJobs.forEach(({ nodeName, data }) => {
      if (!dataMap.has(nodeName)) {
        dataMap.set(nodeName, { node: nodeName, success: 0, failed: 0 });
      }
      dataMap.get(nodeName).success += data.length;
    });

    // Count unique failed jobs per node
    failedJobs.forEach(({ nodeName, data }) => {
      if (!dataMap.has(nodeName)) {
        dataMap.set(nodeName, { node: nodeName, success: 0, failed: 0 });
      }
      const uniqueFails = Array.isArray(data)
        ? data.filter(
          (job, index, self) =>
            self.findIndex(
              (j) =>
                j.job_name === job.job_name &&
                j.error_desc === job.error_desc &&
                j.missed_time === job.missed_time
            ) === index
        )
        : [];

      dataMap.get(nodeName).failed += uniqueFails.length;
    });

    return Array.from(dataMap.values()); // array of { node, success, failed }

  } catch (error) {
    console.error("Error fetching jobs by node:", error);

    // Enhanced error handling
    if (error.response) {
      console.error("Server error:", error.response.status, error.response.data);
    } else if (error.request) {
      console.error("Network error - no response received");
    } else {
      console.error("Request setup error:", error.message);
    }

    return [];
  }
};

export const fetchSuccessJobsByRepository = async () => {
  try {
    const response = await axiosInstance.get(`${config.API.Server_URL}/api/getsuccessjobs`, {
      headers: { "Content-Type": "application/json" },
    });

    const data = response.data;
    const successJobs = data.successjobs;

    // Count jobs per job_repo
    const repoCounts = {};

    successJobs.forEach(({ data: nodeData }) => {
      if (Array.isArray(nodeData)) {
        nodeData.forEach((job) => {
          const repo = job.job_repo || "Unknown";
          repoCounts[repo] = (repoCounts[repo] || 0) + 1;
        });
      }
    });

    // Format for Recharts
    const formattedData = Object.entries(repoCounts).map(([repo, count]) => ({
      repo,
      count,
    }));

    return formattedData;
  } catch (error) {
    console.error("Error fetching job data by repository:", error);
    return [];
  }
};
