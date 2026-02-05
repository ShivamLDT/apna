import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import config from '../../config';
import { Check } from 'lucide-react';
import CryptoJS from "crypto-js";
import RepoIcon from '../Reports/Jobs/RepoIcon';

function encryptData(data) {
  const encryptedData = CryptoJS.AES.encrypt(data, "1234567890").toString();

  return encryptedData;
}
function decryptData(encryptedData) {
  if (!encryptedData) return "";
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, "1234567890");
    const decrypted = bytes.toString(CryptoJS.enc.Utf8);
    return decrypted || "";
  } catch (error) {
    console.error("Decryption error:", error);
    return "";
  }
}

const LiveProgressTable = () => {
  const [agentsData, setAgentsData] = useState([]);
  const [agentData, setAgentData] = useState([]);
  const [animatedData, setAnimatedData] = useState({});
  const [progressValue, setProgressValue] = useState(0);
  const [jobname, setJobname] = useState(0);
  const [selectedAgent, setSelectedAgent] = useState("all");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const socket = useRef(null);
  const [showGif, setShowGif] = useState(false);

  useEffect(() => {
    const storedJobName = decryptData(localStorage.getItem('jobName'));
    setJobname(storedJobName);

    socket.current = io(`${config.API.WEB_SOCKET}`);
    if (socket.current) {
      socket.current.on('backup_data', (data) => {
        try {
          const fetchedData = data.backup_jobs || [];

          fetchedData.forEach(job => {
            if (job.name === storedJobName) {
              if (job.restore_flag !== true && job.restore_flag !== 'true') return;

              const progress = parseFloat(job.progress_number);
              const adjustedProgress = 100 - progress;

              setProgressValue(adjustedProgress);
            }
          });
        } catch (error) {
          // Error handling
        }
      });

      return () => {
        if (socket.current) {
          socket.current.disconnect();
        }
      };
    }
  }, []);

  useEffect(() => {
    const storedAgentData = decryptData(localStorage.getItem("storedAgentDataa"));
    const storedAnimatedData = decryptData(localStorage.getItem("storedAnimatedDataa"));

    const agentDataFromStorage = storedAgentData ? JSON.parse(storedAgentData) : {};
    const animatedDataFromStorage = storedAnimatedData ? JSON.parse(storedAnimatedData) : {};

    setAgentData(agentDataFromStorage);
    setAnimatedData(animatedDataFromStorage);

    socket.current = io(`${config.API.WEB_SOCKET}`);

    if (socket.current) {
      socket.current.on('connect', () => {
        socket.current.emit('request_backup_data', {});
        socket.current.emit('request_backup_jobs', {});
      });

      socket.current.on('starting', (data) => {
        if (!data || !data.backup_jobs) return;

        try {
          const fetchedData = [data.backup_jobs];
          const uniqueAgents = new Set();

          fetchedData.forEach(job => {
            const agent = job.agent;
            uniqueAgents.add(agent);

            setAgentData(prev => {
              const newAgentData = { ...prev };

              if (!newAgentData[agent]) {
                newAgentData[agent] = [];
              }

              const existingIndex = newAgentData[agent].findIndex(j => j.name === job.name && j.scheduled_time === job.scheduled_time);
              if (existingIndex !== -1) {
                newAgentData[agent][existingIndex] = job;
              } else {
                newAgentData[agent].push(job);
              }

              return newAgentData;
            });
          });
        } catch (error) {
          // Error handling
        }
      });

      socket.current.on('backup_data', (data) => {
        if (!data || !data.backup_jobs) return;

        try {
          const fetchedData = data.backup_jobs || [];
          const restoreFlag = data.restore_flag || false;
          if (restoreFlag) return;

          const uniqueAgents = new Set();
          const sortedData = fetchedData.sort((a, b) => a.id - b.id);

          sortedData.forEach(job => {
            const agent = job.agent;
            uniqueAgents.add(agent);

            setAgentData(prev => {
              const newAgentData = { ...prev };

              if (!newAgentData[agent]) {
                newAgentData[agent] = [];
              }

              const existingIndex = newAgentData[agent].findIndex(j => j.id === job.id);
              if (existingIndex !== -1) {
                newAgentData[agent][existingIndex] = job;
              } else {
                newAgentData[agent].push(job);
              }

              if (job.status !== "counting") {
                localStorage.setItem("storedAgentDataa", encryptData(JSON.stringify(newAgentData)));
              }

              return newAgentData;
            });

            setAnimatedData(prev => {
              const newAnimatedData = { ...prev };

              if (!newAnimatedData[agent]) {
                newAnimatedData[agent] = [];
              }

              const existingIndex = newAnimatedData[agent].findIndex(j => j.id === job.id);
              const previousJob = existingIndex !== -1 ? newAnimatedData[agent][existingIndex] : {};
              // FIXED: Apply the same completion logic as in Backupp.jsx
              // If finished is explicitly true OR progress_number >= 100, consider it completed

              const isOverallLevel = job.progress_number !== undefined && !job.progress_number_file && !job.progress_number_upload;
              const isFileLevel = job.progress_number_file !== undefined;
              const isCloudLevel = job.progress_number_upload !== undefined;

              const progressForOverallDisplay = isOverallLevel
                ? Math.max(0, Math.min(100, job.progress_number || 0))
                : previousJob.progress_number || 0; // Retain previous progress_number

              // Folder upload: progress_number_upload is folder-wide; keep monotonic (never decrease)
              const incomingUploadProgress = isCloudLevel ? Math.max(0, Math.min(100, job.progress_number_upload || 0)) : 0;
              const previousUpload = previousJob?.progress_number_upload ?? 0;
              const progress_number_upload_monotonic = isCloudLevel ? Math.max(previousUpload, incomingUploadProgress) : previousUpload;

              const isJobCompleted =
                (job.finished === true || progressForOverallDisplay >= 100) &&
                job.status !== "failed";


              const animatedJob = {
                ...job,
                progress_number_original: job.progress_number,
                // FIXED: For display purposes, show 100% if completed (finished=true OR progress>=100), otherwise clamp between 0-100
                progress_number: isJobCompleted ? 100 : progressForOverallDisplay,
                progress_number_file: isFileLevel
                  ? Math.max(0, Math.min(100, job.progress_number_file || 0))
                  : previousJob?.progress_number_file || 0,

                progress_number_upload: progress_number_upload_monotonic,
                  
                finished: isJobCompleted, // Set finished flag for consistency
                accuracy: job.accuracy || 100,
              };

              if (existingIndex !== -1) {
                newAnimatedData[agent][existingIndex] = animatedJob;
              } else {
                newAnimatedData[agent].push(animatedJob);
              }

              if (job.status !== "counting") {
                localStorage.setItem("animatedData", encryptData(JSON.stringify(newAnimatedData)));
                localStorage.setItem("storedAnimatedDataa", encryptData(JSON.stringify(newAnimatedData)));
              }

              return newAnimatedData;
            });
          });
        } catch (error) {
          // Error handling
        }
      });

      return () => {
        if (socket.current) {
          socket.current.disconnect();
        }
      };
    }
  }, []);

  useEffect(() => {
    const processLiveData = () => {
      const agentDataMap = {};
      const storedData = JSON.parse(decryptData(localStorage.getItem('storedAnimatedDataa')) || '{}');

      for (const [agentName, tasks] of Object.entries(storedData)) {
        const validTasks = tasks.filter(task =>
          task.name !== undefined &&
          (
            task.status === "initiating" ||
            task.progress_number !== undefined
          )
        );


        if (validTasks.length > 0) {
          if (!agentDataMap[agentName]) {
            agentDataMap[agentName] = [];
          }

          validTasks.forEach((task, index) => {
            // FIXED: Use the same completion logic for displaying progress
            const isInitiating = task.status === "initiating";
            const isCounting = task.status === "counting";
            const isFailed = task.status === "failed";
            const isCompleted =
              (task.finished === true || task.progress_number >= 100) &&
              task.status !== "failed";

            let displayProgress;

            if (isInitiating) {
              displayProgress = 0;  // always 0% until it switches
            } else if (isFailed) {
              displayProgress = 0;
            } else if (isCompleted) {
              displayProgress = 100;
            } else if (isCounting) {
              displayProgress = 0;
            } else {
              displayProgress = Math.max(0, Math.min(100, task.progress_number || 0));
            }

            agentDataMap[agentName].push({
              jobProgress: displayProgress,
              agentTaskName: task.name,
              agentSheduleTime: task.scheduled_time,
              jobId: task.job_id,
              taskIndex: index,
              finished: isCompleted,
              status: task.status,
              repo: task.repo || "N/A"
            });
          });
        }
      }

      return Object.entries(agentDataMap).map(([agentName, tasks]) => ({
        agentName,
        tasks: tasks.sort((a, b) => b.agentSheduleTime?.localeCompare(a?.agentSheduleTime))
      }));

    };

    const initialAgentsData = processLiveData();
    setAgentsData(initialAgentsData);

    const intervalId = setInterval(() => {
      const updatedAgentsData = processLiveData();
      setAgentsData(updatedAgentsData);
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  const removeAgentProgress = (jobId, agentName) => {
    setAgentData(prev => {
      const newAgentData = { ...prev };

      if (newAgentData[agentName]) {
        newAgentData[agentName] = newAgentData[agentName].filter(job => job.job_id !== jobId);
      }

      localStorage.setItem("storedAgentDataa", encryptData(JSON.stringify(newAgentData)));
      return newAgentData;
    });

    setAnimatedData(prev => {
      const newAnimatedData = { ...prev };

      if (newAnimatedData[agentName]) {
        newAnimatedData[agentName] = newAnimatedData[agentName].filter(job => job.job_id !== jobId);
      }

      localStorage.setItem("animatedData", encryptData(JSON.stringify(newAnimatedData)));
      localStorage.setItem("storedAnimatedDataa", encryptData(JSON.stringify(newAnimatedData)));
      return newAnimatedData;
    });
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    localStorage.removeItem('storedAgentDataa');
    localStorage.removeItem('storedAnimatedDataa');
    // Request fresh data from socket
    if (socket.current) {
      socket.current.emit('request_backup_data', {});
      socket.current.emit('request_backup_jobs', {});
    }

    // Stop refreshing animation after 1 second
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setShowGif(prev => !prev);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const agentNames = ["all", ...agentsData.map(agent => agent.agentName)];

  const filteredAgentsData = selectedAgent === "all"
    ? agentsData
    : agentsData.filter(agent => agent.agentName === selectedAgent);

  // Get progress bar color based on status
  const getProgressColorByPercentage = (percentage) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 75) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    if (percentage >= 25) return 'bg-purple-500';
    return 'bg-red-500';
  };

  // Get status badge style
  const getStatusStyle = (status, finished) => {
    if (finished) return 'bg-green-50 text-green-700 border-green-200';
    if (status === 'running') return 'bg-blue-50 text-blue-700 border-blue-200';
    if (status === 'counting') return 'bg-purple-50 yellow-700 border-yellow-200';
    if (status === 'error') return 'bg-red-50 text-red-700 border-red-200';
    return 'bg-gray-50 text-gray-700 border-gray-200';
  };

  if (agentsData.length === 0) {
    return (
      <div className="bg-white p-4 rounded-xl shadow-sm text-center">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-center text-xl font-semibold text-gray-800">Live Progress</h2>

          <div className="flex items-center gap-3">
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${isRefreshing
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200'
                }`}
            >
              <svg
                className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </button>

            {/* Agent Filter */}
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="px-3 py-2 w-full border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {agentNames.map(agent => (
                <option key={agent} value={agent}>
                  {agent === "all" ? "All Agents" : agent}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex flex-col items-center text-center py-20 w-full">
          <div className="text-gray-500 mb-4">
            📊
          </div>
          <h3 className="text-lg font-medium text-gray-700">You don't have any Live Progress yet!</h3>
          {/* <p className="text-sm text-gray-500 mt-2">Connect to WebSocket to see live progress data.</p> */}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm z-50">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-center text-xl font-semibold text-gray-800">Live Progress</h2>

        <div className="flex items-center gap-3">
          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${isRefreshing
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200'
              }`}
          >
            <svg
              className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>

          {/* Agent Filter */}
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="px-3 py-2 w-full border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {agentNames.map(agent => (
              <option key={agent} value={agent}>
                {agent === "all" ? "All Agents" : agent}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="h-64 overflow-auto rounded-lg">
        <div className="space-y-4">
          {filteredAgentsData.map((agent, agentIndex) => (
            <div key={agent.agentName} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Agent Header */}
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs text-gray-800 flex items-center gap-2">
                    <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {agent.agentName}
                  </h3>
                  <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded-full border">
                    {agent.tasks.length} {agent.tasks.length === 1 ? 'job' : 'jobs'}
                  </span>
                </div>
              </div>

              {/* Jobs Table */}
              <div className="bg-white">
                <table className="w-full">
                  <thead className="bg-gray-25">
                    <tr className="border-b border-gray-100">
                      {/* <th className="text-left py-2 px-2 text-xs text-gray-500">Repo</th> */}
                      <th className="text-left py-2 px-4 text-xs text-gray-500">Job Name</th>
                      <th className="text-left py-2 px-4 text-xs text-gray-500 w-48">Progress</th>
                      <th className="text-left py-2 px-4 text-xs text-gray-500 w-24">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {agent.tasks.map((item, index) => (
                      <tr
                        key={`${agent.agentName}-${item.agentTaskName}-${item.agentSheduleTime}`}
                        className={`border-b border-gray-50 hover:bg-gray-25 transition-colors ${index === agent.tasks.length - 1 ? 'border-b-0' : ''
                          }`}
                      >
                        {/* <td className="px-2 py-3">
                          <RepoIcon repo={item.repo} />
                        </td> */}

                        <td className="px-4 py-3">
                          <div className="flex flex-col">
                            <span className="text-xs text-gray-800">{item.agentTaskName}</span>
                            {item.agentSheduleTime && (
                              <span className="text-xs text-gray-500">
                                {item.agentSheduleTime}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3">
                            <div className="flex-1 bg-gray-100 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full transition-all duration-300 ${getProgressColorByPercentage(item.jobProgress)}`}
                                style={{ width: `${Math.max(0, Math.min(item.jobProgress || 0, 100))}%` }}
                              ></div>
                            </div>
                            {/* <span className="text-xs font-medium text-gray-600 min-w-[45px]">
                              {(item.jobProgress || 0).toFixed(1)}%
                            </span> */}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          {item.status === "initiating" ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs border bg-blue-50 text-blue-700 border-blue-200">
                              <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                              Initiating...
                            </span>
                          ) : (
                            <span
                              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs border ${getStatusStyle(item.status, item.finished)}`}
                            >
                              {item.status === "failed" ? (
                                <>
                                  <span className="text-red-600 font-semibold">Failed</span>
                                  <span className="text-red-600 ml-1">0%</span>
                                </>
                              ) : item.finished ? (
                                <>
                                  <Check size={15} color="#03b300" />
                                  100%
                                </>
                              ) : (
                                <>
                                  {(item.jobProgress || 0).toFixed(2)}%
                                </>
                              )}
                            </span>
                          )}
                        </td>

                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live indicator */}
      <div className="flex items-center justify-center mt-4">
        <div className={`w-2 h-2 rounded-full mr-2 transition-opacity duration-500 ${showGif ? 'bg-green-500 opacity-100' : 'bg-green-300 opacity-50'}`}></div>
        <span className="text-xs text-gray-500">Live Updates Active</span>
      </div>
    </div>
  );
};

export default LiveProgressTable;