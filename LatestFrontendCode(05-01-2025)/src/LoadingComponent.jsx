export default function LoadingComponent() {
    return (
        <div className="flex items-center justify-center h-full bg-white">
            <div className="relative w-96 h-4 bg-gradient-to-r from-blue-100 to-blue-200 rounded-2xl overflow-hidden shadow-lg">
                <div
                    className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600 w-3/5 rounded-2xl transform -translate-x-full"
                    style={{ animation: 'oceanSlide 3s infinite' }}
                />

                <div className="absolute inset-0 flex items-center justify-center">
                    <p className="text-sm font-bold text-white tracking-wide z-10 mix-blend-difference">
                        LOADING
                        <span
                            className="inline-block ml-1"
                            style={{ animation: 'dots 1.5s infinite steps(3, end)' }}
                        >
                            ...
                        </span>
                    </p>
                </div>
            </div>

            <style>{`
        @keyframes oceanSlide {
          0% { transform: translateX(-150%); }
          66% { transform: translateX(0%); }
          100% { transform: translateX(150%); }
        }
        
        @keyframes dots {
          0% { content: ''; }
          33% { content: '.'; }
          66% { content: '..'; }
          100% { content: '...'; }
        }
      `}</style>
        </div>
    );
}