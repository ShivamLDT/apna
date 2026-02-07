// components/dashboard/StatsCards.jsx
import { useState, useEffect, useContext } from "react";
import { BadgeCheck, CircleX, Sigma, Download, UsersRound, ScreenShareOff, Monitor, Loader2, RefreshCcw } from "lucide-react";
import "./Dashboard.css";
import { useNavigate } from "react-router-dom";
import ProcessorChart from "./ProcessorChart";
import config from "../../config";
import { useJobs } from "../Jobs/JobsContext";
import NetworkChart from "./NetworkChart";
import GaugeComponent from 'react-gauge-component';
import useUserList from "../../Hooks/useUserList";
import CryptoJS from "crypto-js";
import useSaveLogs from "../../Hooks/useSaveLogs";
import axios from "axios";
import axiosInstance from "../../axiosinstance";
import { RestoreContext } from '../../Context/RestoreContext';
import AlertComponent from "../../AlertComponent";

const StatsCards = ({ jobCounts, networkData, connectedNodesCount, loading, refetch, onerefetch, tworefetch }) => {
  const navigate = useNavigate();
  const { userData } = useUserList();
  const { jobCounts: jobsFromContext } = useJobs();
  const accessToken = localStorage.getItem("AccessToken");
  const [allEndpoints, setAllEndpoints] = useState([]);
  const [unpairedAgentsData, setUnpairedAgentsData] = useState({});
  const { setOpenSuccessful, openSuccessful } = useContext(RestoreContext);
  const [alert, setAlert] = useState(null);

  const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();

  const handleClick = () => {
    const downloadEvent = "Endpoint Download";
    handleLogsSubmit(downloadEvent);
    const url = config.API.DOWNLOAD_URL;
    window.location.href = url; // Redirect to the download URL
  };

  const handleRefresh = () => {
    refetch();
    onerefetch();
    tworefetch();
  }

  const mbitsToDisplayValue = (value) => {
    if (value >= 1000) {
      const gbValue = value / 1000;
      if (Number.isInteger(gbValue)) {
        return gbValue.toFixed(2) + ' GB';
      } else {
        return gbValue.toFixed(2) + ' GB';
      }
    } else {
      return value.toFixed(2) + ' MB';
    }
  };

  const fetchPairData = async () => {
    try {
      const response = await axiosInstance.post(`${config.API.FLASK_URL}/pair`, {}, {
        headers: {
          'Content-Type': 'application/json',
          token: accessToken,
        },
      });

      const data = response.data;

      const paired = Object.values(data?.pairedAgents || {}).map((item, index) => ({
        id: index + 1,
        name: item.IPname || item.activationkey || 'Unnamed',
        status: 'paired',
      }));

      const awaited = Object.values(data?.awaited || {}).map((item, index) => ({
        id: index + 1000, // just offset to avoid clash
        name: item.IPname || item.activationkey || 'Unnamed',
        status: 'awaited',
      }));

      const unpairedRaw = data?.unpairedAgents || {};
      setUnpairedAgentsData(unpairedRaw);

      const unpaired = Object.entries(unpairedRaw).map(([key, item], index) => ({
        id: key,
        name: item.IPname || item.activationkey || 'Unnamed',
        status: 'unpaired',
      }));

      setAllEndpoints([...paired, ...awaited, ...unpaired]);

    } catch (error) {
      console.error('Error fetching endpoints:', error);

      // Enhanced error handling
      if (error.response) {
        console.error("Server error:", error.response.status, error.response.data);
      } else if (error.request) {
        console.error("Network error - no response received");
      } else {
        console.error("Request setup error:", error.message);
      }

      // Optionally set error state or show user notification
      // toast.error("Failed to fetch endpoint data");
      // setError("Failed to load endpoints");
    }
  };

  useEffect(() => {
    if (!userRole) return;

    if (userRole.toLowerCase() !== "employee") {
      fetchPairData();
    }
  }, [userRole]);


  function handlenavigate(path, state = {}) {
    if (path === "/pairing" && userRole?.toLowerCase() === "employee") {
      setAlert({
        message: "You do not have permission to access this section.",
        type: 'error'
      });
      return;
    }

    navigate(path, { state });

    if (path === "/successfuljob") {
      setOpenSuccessful(true);
    }
  }


  const statsData = [
    {
      title: "Success Jobs",
      value: jobCounts.success,
      icon: BadgeCheck,
      gradient: "from-green-100 to-green-200",
      iconBg: "bg-green-500",
      path: "/successfuljob",
    },
    {
      title: "Failed Jobs",
      value: jobCounts.failed,
      icon: CircleX,
      gradient: "from-red-100 to-red-200",
      iconBg: "bg-red-500",
      path: "/failedjob",
    },
    {
      title: "Total Jobs",
      value: jobCounts.total,
      icon: Sigma,
      gradient: "from-blue-100 to-blue-200",
      iconBg: "bg-blue-500",
      path: "/executedjob",
    },
    {
      title: "Endpoints",
      value: connectedNodesCount,
      icon: Monitor,
      gradient: "from-yellow-100 to-yellow-200",
      iconBg: "bg-yellow-500",
      path: "/endpoints",
      loading: loading,
    },
    {
      title: "Total Users",
      value: userData?.length || 0,
      icon: UsersRound,
      gradient: "from-purple-100 to-purple-200",
      iconBg: "bg-purple-500",
      path: "/users",
    },
    {
      title: "Unpaired",
      value: Object.keys(unpairedAgentsData).length || 0,
      icon: ScreenShareOff,
      gradient: "from-red-200 to-red-400",
      iconBg: "bg-red-500",
      path: "/pairing",
      navigateState: { tab: "unpaired" },
    },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 mb-2 homefirstsec">
      {/* Left side: Job Summary */}
      <div className="bg-white rounded-xl p-5">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Apna Backup</h2>
            <p className="text-gray-500">Summary</p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50" onClick={handleRefresh}>
            <RefreshCcw className="w-4 h-4" />
            Refresh
          </button>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50" onClick={handleClick}>
            <Download className="w-4 h-4" />
            Endpoint Download
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {statsData.map((stat, index) => (
            <div
              key={index}
              onClick={() => handlenavigate(stat.path, stat.navigateState)}
              className={`bg-gradient-to-br ${stat.gradient} p-6 rounded-xl cursor-pointer hover:shadow-lg jobscountsection`}
            >
              <div className="flex items-center gap-4">
                <div className={`${stat.iconBg} p-3 rounded-full`}>
                  {stat.loading ? (
                    <Loader2 className="w-6 h-6 text-white animate-spin" />
                  ) : (
                    <stat.icon className="w-6 h-6 text-white" />
                  )}
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">
                    {stat.loading ? "..." : stat.value}
                  </p>
                  <p className="text-xs font-semibold text-gray-600">{stat.title}</p>
                  {stat.subtext ? (
                    <p className="text-[10px] text-gray-500">{stat.subtext}</p>
                  ) : null}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right side: Network Chart */}
      <div className="bg-white rounded-xl p-5">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Server Network Usage</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Network Received Gauge */}
          <div className="flex flex-col items-center">
            <h4 className="text-lg font-semibold text-blue-600 mb-2">Data Received</h4>
            <div className="w-full max-w-xs">
              <GaugeComponent
                arc={{
                  nbSubArcs: 150,
                  colorArray: ['#5BE12C', '#F5CD19', '#EA4228'],
                  width: 0.3,
                  padding: 0.003
                }}
                labels={{
                  valueLabel: {
                    style: { fontSize: 40 },
                    formatTextValue: mbitsToDisplayValue
                  },
                  tickLabels: {
                    type: "outer",
                    ticks: [
                      { value: 2000 },
                      { value: 4000 },
                      { value: 6000 },
                      { value: 8000 },
                    ],
                    defaultTickValueConfig: {
                      formatTextValue: mbitsToDisplayValue
                    }
                  }
                }}
                value={networkData?.received || 0}
                maxValue={10000}
              />
            </div>
          </div>

          {/* Network Sent Gauge */}
          <div className="flex flex-col items-center">
            <h4 className="text-lg font-semibold text-green-600 mb-2">Data Sent</h4>
            <div className="w-full max-w-xs">
              <GaugeComponent
                arc={{
                  nbSubArcs: 150,
                  colorArray: ['#5BE12C', '#F5CD19', '#EA4228'],
                  width: 0.3,
                  padding: 0.003
                }}
                labels={{
                  valueLabel: {
                    style: { fontSize: 40 },
                    formatTextValue: mbitsToDisplayValue
                  },
                  tickLabels: {
                    type: "outer",
                    ticks: [
                      { value: 2000 },
                      { value: 4000 },
                      { value: 6000 },
                      { value: 8000 }, ,
                    ],
                    defaultTickValueConfig: {
                      formatTextValue: mbitsToDisplayValue
                    }
                  }
                }}
                value={networkData?.sent || 0}
                maxValue={10000}
              />
            </div>
          </div>
        </div>
      </div>
      {alert && (
        <AlertComponent
          message={alert.message}
          type={alert.type}
          onClose={() => setAlert(null)}
        />
      )}
    </div>
  );
};

export default StatsCards;