import React from "react";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { useJobs } from "../Jobs/JobsContext";
import RepoIcon from "../Reports/Jobs/RepoIcon";
import LoadingComponent from "../../LoadingComponent";

const renderRepoTick = ({ x, y, payload }) => {
  return (
    <g transform={`translate(${x},${y + 6})`}>
      <foreignObject x={-40} y={0} width={80} height={80}>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <RepoIcon repo={payload.value} />
        </div>
      </foreignObject>
    </g>
  );
};


const DataRepoJob = ({ chartData }) => {
  const { repoLoading } = useJobs();

  const repoColors = {
    LAN: { type: 'gradient', colors: ['#d946ef', '#ec4899'] }, // Purple to Pink (On-Premise)
    GDRIVE: { type: 'gradient', colors: ['#4285f4', '#34a853', '#fbbc04'] }, // Google Drive colors
    AZURE: { type: 'gradient', colors: ['#0078d4', '#50e6ff'] }, // Azure blue gradient
    AWSS3: { type: 'gradient', colors: ['#ff9900', '#232f3e'] }, // AWS orange to dark
    ONEDRIVE: { type: 'gradient', colors: ['#0078d4', '#0364b8'] }, // OneDrive blue gradient
    UNC: { type: 'gradient', colors: ['#3b82f6', '#60a5fa'] }, // Blue gradient for NAS
  };

  const getPath = (x, y, width, height) => {
    return `M${x},${y + height}C${x + width / 3},${y + height} ${x + width / 2
      },${y + height / 3}
    ${x + width / 2}, ${y}
    C${x + width / 2},${y + height / 3} ${x + (2 * width) / 3},${y + height} ${x + width
      }, ${y + height}
    Z`;
  };

  const TriangleBar = (props) => {
    const { fill, x, y, width, height } = props;
    return <path d={getPath(x, y, width, height)} stroke="none" fill={fill} />;
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm">
      <h3 className="text-center text-lg font-semibold mb-4">
        Successful Backups by Job Repository
      </h3>

      {repoLoading ? (
        //     <div className="flex items-center justify-center h-full">
        //       <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
        //         <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
        //           style={{ animation: 'oceanSlide 3s infinite' }} />
        //         <style>{`
        //   @keyframes oceanSlide {
        //     0% { transform: translateX(-150%); }
        //     66% { transform: translateX(0%); }
        //     100% { transform: translateX(150%); }
        //   }
        // `}</style>
        //       </div>
        //     </div>
        <LoadingComponent />
      ) : chartData?.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-500 text-sm">
          No Data Available
        </div>
      ) : (
        <div className="h-64 data-repo-job">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <defs>
                {Object.entries(repoColors).map(([repo, config]) => (
                  <linearGradient key={repo} id={`gradient-${repo}`} x1="0" y1="0" x2="0" y2="1">
                    {config.colors.map((color, idx) => (
                      <stop
                        key={idx}
                        offset={`${(idx / (config.colors.length - 1)) * 100}%`}
                        stopColor={color}
                      />
                    ))}
                  </linearGradient>
                ))}
              </defs>
              <XAxis dataKey="repo" tick={renderRepoTick} />
              <YAxis allowDecimals={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const repoNameMap = {
                      LAN: "On-Premise",
                      UNC: "NAS",
                    };
                    const rawRepo = payload[0].payload.repo;
                    const label = repoNameMap[rawRepo] || rawRepo;
                    const count = payload[0].value;

                    return (
                      <div className="bg-white p-2 border rounded shadow text-sm">
                        <p className="font-medium">{label}: {count}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />

              <Bar dataKey="count" name="Success Count" shape={<TriangleBar />}>
                {chartData.map((entry, index) => {
                  const fillColor = repoColors[entry.repo]
                    ? `url(#gradient-${entry.repo})`
                    : '#6366f1';

                  return (
                    <Cell
                      key={`cell-${index}`}
                      fill={fillColor}
                    />
                  );
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default DataRepoJob;
