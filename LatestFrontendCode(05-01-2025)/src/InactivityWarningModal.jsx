import { AlertTriangle, Clock, MousePointer } from 'lucide-react';

export default function InactivityWarningModal({ secondsLeft }) {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fade-in">
            <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md mx-4 transform animate-scale-in">
                <div className="flex justify-center mb-6">
                    <div className="relative">
                        <div className="absolute inset-0 bg-yellow-400 rounded-full animate-ping opacity-75"></div>
                        <div className="relative bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full p-4">
                            <AlertTriangle className="w-8 h-8 text-white" />
                        </div>
                    </div>
                </div>

                <h3 className="text-2xl font-bold text-gray-800 text-center mb-4">
                    Session Expiring
                </h3>

                <div className="flex items-center justify-center mb-6 bg-red-50 rounded-lg p-4">
                    <Clock className="w-6 h-6 text-red-500 animate-bounce flex-shrink-0" />
                    <p className="text-gray-700 text-lg ml-3">
                        You will be logged out in{' '}
                        <span className="text-red-600">
                            {secondsLeft}
                        </span>{' '}
                        <span className="text-gray-600">seconds</span>
                    </p>
                </div>

                <div className="flex items-center justify-center bg-blue-50 rounded-lg p-4">
                    <MousePointer className="w-5 h-5 text-blue-500 animate-wiggle flex-shrink-0" />
                    <p className="text-sm text-gray-600 ml-2">
                        Move your mouse or press any key to stay logged in
                    </p>
                </div>
            </div>

            <style jsx>{`
                @keyframes fade-in {
                    from {
                        opacity: 0;
                    }
                    to {
                        opacity: 1;
                    }
                }

                @keyframes scale-in {
                    from {
                        transform: scale(0.9);
                        opacity: 0;
                    }
                    to {
                        transform: scale(1);
                        opacity: 1;
                    }
                }

                @keyframes wiggle {
                    0%, 100% {
                        transform: translateX(0);
                    }
                    25% {
                        transform: translateX(-4px);
                    }
                    75% {
                        transform: translateX(4px);
                    }
                }

                .animate-fade-in {
                    animation: fade-in 0.3s ease-out;
                }

                .animate-scale-in {
                    animation: scale-in 0.3s ease-out;
                }

                .animate-wiggle {
                    animation: wiggle 1s ease-in-out infinite;
                }
            `}</style>
        </div>
    );
}