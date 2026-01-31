import { useJobs } from "../../Jobs/JobsContext";
import CircularProgress from "./CircularProgress";

export default function SuccessFailurePanel({ title, color }) {
    const { executedJobs, jobCounts } = useJobs();

    const count = title.includes("Executed") ? jobCounts.success : jobCounts.failed;
    const percentage = jobCounts.total ? ((count / jobCounts.total) * 100).toFixed(2) : 0;

    return (
        <div className="bg-white rounded-lg p-4">
            <h3 className="text-lg text-center font-medium text-gray-600 uppercase">{title}</h3>
            <div className="flex justify-center">
                <CircularProgress percentage={percentage} color={color} />
            </div>
            <div className="flex justify-center space-x-6">
                <div className="text-center">
                    <div className="text-lg font-bold text-gray-800">{count} / {jobCounts.total}</div>
                    <div className="text-lg text-gray-500 uppercase">{title}</div>
                </div>
            </div>
        </div>
    );
}
