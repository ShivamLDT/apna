// components/dashboard/TopJobsList.jsx
import React from "react";

const TopJobsList = ({ jobs }) => {
    return (
        <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Recent Jobs</h3>

            {/* Desktop Table */}
            <div className="hidden md:block overflow-x-auto">
                {/* Add 'table-fixed' to enforce column widths */}
                <table className="w-full text-sm text-left bg-white table-fixed">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                            {/* Assign equal width (25%) to each column */}
                            <th scope="col" className="px-6 py-3 w-1/4">
                                Job Name
                            </th>
                            <th scope="col" className="px-6 py-3 w-1/4">
                                Agent
                            </th>
                            <th scope="col" className="px-6 py-3 w-1/4">
                                Created Time
                            </th>
                            <th scope="col" className="px-6 py-3 w-1/4">
                                Executed Time
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {jobs.map((job,index) => (
                            <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                                {/* 'break-words' will wrap the text within the column */}
                                <td className="px-6 py-4 font-medium text-gray-900 break-words">
                                    {job.name}
                                </td>
                                <td className="px-6 py-4 break-words">
                                    {job.agent}
                                </td>
                                <td className="px-6 py-4 text-green-600 break-words">
                                    {job.latest_created_at}
                                </td>
                                <td className="px-6 py-4 text-green-600 break-words">
                                    {job.next_run_time.replace(/\+0530/, "")}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Mobile Card Layout (No changes needed here) */}
            <div className="md:hidden space-y-4">
                {jobs.map((job,index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                        <div className="font-medium text-gray-900 mb-2 break-words whitespace-normal w-full">
                            {job.name}
                        </div>
                        <div className="space-y-1 text-sm text-gray-600">
                            <div className="flex justify-between">
                                <span className="font-medium">Agent:</span>
                                <span>{job.agent}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="font-medium">Created:</span>
                                <span className="text-green-600">{job.latest_created_at}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="font-medium">Next Run:</span>
                                <span className="text-green-600">{job.next_run_time.replace(/\+0530/, "")}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TopJobsList;