import { X, AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';

const AlertComponent = ({ message, type = 'error', onClose }) => {
    const typeStyles = {
        success: 'bg-green-50 border-green-200 text-green-800',
        error: 'bg-red-50 border-red-200 text-red-800',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
        info: 'bg-blue-50 border-blue-200 text-blue-800'
    };

    const iconStyles = {
        success: 'text-green-500',
        error: 'text-red-500',
        warning: 'text-yellow-500',
        info: 'text-blue-500'
    };

    const icons = {
        success: CheckCircle,
        error: XCircle,
        warning: AlertCircle,
        info: Info
    };

    const Icon = icons[type];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" style={{ zIndex: 99999999 }}>
            <div className={`relative w-full max-w-md p-6 border-2 rounded-lg shadow-xl ${typeStyles[type]}`}>
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition-colors"
                >
                    <X size={20} />
                </button>

                <div className="flex items-start gap-4">
                    <Icon size={24} className={`flex-shrink-0 ${iconStyles[type]}`} />
                    <div className="flex-1 pt-0.5">
                        <p className="text-sm font-medium leading-relaxed">{message}</p>
                    </div>
                </div>

                <div className="mt-6 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-white bg-gray-800 rounded-md hover:bg-gray-700 transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AlertComponent;