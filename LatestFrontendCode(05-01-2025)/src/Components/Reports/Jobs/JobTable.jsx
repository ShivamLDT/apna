const JobTable = ({ columns, data, renderRow }) => (
    <div className="h-full flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto">
            <table className="w-full table-fixed break-words">
                <thead className="sticky top-0 bg-white z-10">
                    <tr className="text-xs font-medium text-gray-600 border-b">
                        {columns.map((col, idx) => (
                            <th
                                key={idx}
                                className={`border px-4 py-2 text-left ${col.className || ''}`}
                                style={{ width: col.width || 'auto' }}
                            >
                                {col.title}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 min-h-full">
                    {data.length > 0 ? (
                        data.map((item, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                                {renderRow(item, index)}
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="100%" className="text-center py-4 text-gray-500">
                                No Data Available
                            </td>
                        </tr>
                    )}
                </tbody>

            </table>
        </div>
    </div>
);

export default JobTable;
