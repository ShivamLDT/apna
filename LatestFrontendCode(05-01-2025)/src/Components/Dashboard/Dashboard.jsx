// components/dashboard/Dashboard.jsx
import React, { useEffect, useRef, useState } from "react";
import { useJobs } from "../Jobs/JobsContext";
import { useServerData } from "./useServerData";
import Layout from "./Layout";
import StatsCards from "./StatsCards";
import JobInsightsChart from "./JobInsightsChart";
import DiskUsageChart from "./DiskUsageChart";
import CustomerSatisfactionChart from "./SuccessFailedChart";
import DataRepoJob from "./DataRepoJob";
import TopJobsList from "./TopJobsList";
import MemoryChart from "./MemoryChart";
import ProcessorChart from "./ProcessorChart";
import NetworkChart from "./NetworkChart";
import LiveProgressTable from "./LiveProgress";
import config from "../../config";
import io from 'socket.io-client';
import { useToast } from "../../ToastProvider";
import LoadingComponent from "../../LoadingComponent";
// const style = document.createElement("style");
// style.textContent = `
//   @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
// `;
// document.head.appendChild(style);

const Dashboard = () => {
  const { jobCounts, topJobs, totalTopJobs, jobsByNode, jobsByRepository, onerefetch, tworefetch, loading: jobLoading } = useJobs();
  const { serverData, diskData, memoryChart, memoryData, processorChart, processorData, networkData, loading, error, refetch } = useServerData();
  const { showToast } = useToast();
  const socket = useRef(null);
  const [showConnectionError, setShowConnectionError] = useState(false);

  useEffect(() => {
    if (error) {
      setShowConnectionError(true);
    } else {
      setShowConnectionError(false);
    }
  }, [error]);

  // useEffect(() => {
  //   const interval = setInterval(() => {
  //     refetch(false); // pass false → skip loader
  //     onerefetch(false);
  //     tworefetch(false);
  //   }, 30000);

  //   return () => clearInterval(interval);
  // }, [refetch, onerefetch, tworefetch]);


  useEffect(() => {
    socket.current = io(`${config.API.WEB_SOCKET}`);

    let lastMessage = '';
    let messageCooldown = false;

    socket.current.on('message', (message) => {
      if (message && message.message) {
        const messageData = message.message;

        if (messageData !== lastMessage && !messageCooldown) {
          showToast(`Message: ${messageData}`, "info");
          lastMessage = messageData;
          messageCooldown = true;
          setTimeout(() => {
            messageCooldown = false;
          }, 1000);
        }
      }
    });
  }, []);


  // if (jobLoading) {
  //   return (
  //     <>
  //       <div className="flex items-center justify-center h-full">
  //         <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
  //           <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
  //             style={{ animation: 'oceanSlide 3s infinite' }} />
  //           <style>{`
  //     @keyframes oceanSlide {
  //       0% { transform: translateX(-150%); }
  //       66% { transform: translateX(0%); }
  //       100% { transform: translateX(150%); }
  //     }
  //   `}</style>
  //         </div>
  //       </div>
  //     </>
  //   );
  // }

  if (jobLoading) {
    return <LoadingComponent />;
  }

  // if (error) {
  //   return (
  //     <>
  //       <div className="flex items-center justify-center h-full">
  //         <div className="text-lg text-red-600">Error: {error}</div>
  //       </div>
  //     </>
  //   );
  // }


  return (
    <>
      {showConnectionError && (
        <div className="fixed top-0 left-0 w-full bg-red-600 text-white text-center py-2 z-50 shadow-md animate-slideDown">
          {typeof error === "string" ? error : JSON.stringify(error)}
        </div>
      )}

      {/* Stats Cards */}
      <div className={`${showConnectionError ? "" : ""}`}>
        <StatsCards
          jobCounts={jobCounts}
          networkData={networkData}
          connectedNodesCount={serverData?.server_connected_nodes?.result?.length || 0}
          loading={loading}
          onerefetch={onerefetch}
          tworefetch={tworefetch}
          refetch={refetch}

        />

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 mb-2">
          {/* Job Execution Insights */}
          {/* <JobInsightsChart data={jobsByNode} /> */}

          <DiskUsageChart data={diskData} />
          <LiveProgressTable />
          <MemoryChart data={memoryChart} memoryData={memoryData} />
          <DataRepoJob chartData={jobsByRepository} />

          <CustomerSatisfactionChart data={jobsByNode} jobCounts={jobCounts} />

          <ProcessorChart data={processorChart} processorData={processorData} />

        </div>
        {/* Top Jobs */}
        <TopJobsList jobs={topJobs} />
      </div>
      {/* simple animation */}
      <style>{`
        @keyframes slideDown {
          from { transform: translateY(-100%); }
          to { transform: translateY(0); }
        }
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default Dashboard;