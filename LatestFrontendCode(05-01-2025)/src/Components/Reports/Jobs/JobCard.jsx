const JobCard = ({ icon, amount, name, iconBg, textColor, onClick, isActive }) => (
    <div
        className={`flex items-center space-x-3 p-4 bg-white rounded-lg cursor-pointer hover:shadow-md transition 
            ${isActive ? 'border-b-4 border-blue-500' : ''}`}
        onClick={onClick}
    >
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${iconBg}`}>
            {icon}
        </div>
        <div>
            <div className={`text-xl font-bold ${textColor}`}>{amount}</div>
            <div className="text-sm text-gray-500">{name}</div>
        </div>
    </div>
);

export default JobCard;
