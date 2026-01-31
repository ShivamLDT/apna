import  { useEffect, useState } from 'react';
import './RestoreModal.css';

const RestoreProgressPopup = () => {
    const [visible, setVisible] = useState(true);
    const [progress, setProgress] = useState(0);
    const [processing, setProcessing] = useState(false);
    const [btnText, setBtnText] = useState('Proceed with Restore');

    const closeModal = () => {
        setVisible(false);
    };

    const proceedRestore = () => {
        setProcessing(true);
        setBtnText('');
        let p = 0;
        const interval = setInterval(() => {
            p += 10;
            setBtnText(<><div className="restore-popup-model-overlay-loading"></div>Processing... {p}%</>);
            if (p >= 100) {
                clearInterval(interval);
                setBtnText('✅ Restore Complete!');
                setTimeout(() => {
                    setBtnText('Proceed with Restore');
                    setProcessing(false);
                }, 2000);
            }
        }, 200);
    };

    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape') closeModal();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, []);

    if (!visible) return null;

    return (
        <>
            <div className="restore-popup-model-overlay-background-particles">
                <div className="restore-popup-model-overlay-particle"></div>
                <div className="restore-popup-model-overlay-particle"></div>
                <div className="restore-popup-model-overlay-particle"></div>
                <div className="restore-popup-model-overlay-particle"></div>
            </div>

            <div className="restore-popup-model-overlay-background-blur" ></div>

            <div className="restore-popup-model-overlay-modal">
                <div className="restore-popup-model-overlay-modal-header">
                    <h2 className="restore-popup-model-overlay-modal-title">Restore Progress Test</h2>
                    <button className="restore-popup-model-overlay-close-btn">×</button>
                </div>

                <div className="restore-popup-model-overlay-modal-body">
                    <div className="restore-popup-model-overlay-backup-info">
                        <div className="restore-popup-model-overlay-backup-date">Backup Taken On</div>
                        <div className="restore-popup-model-overlay-backup-time">27/06/2025, 03:53:48 PM</div>
                        <div className="restore-popup-model-overlay-status-badge">
                            <div className="restore-popup-model-overlay-pulse"></div>
                            Ready
                        </div>
                    </div>

                    <div className="restore-popup-model-overlay-source-section">
                        <div className="restore-popup-model-overlay-source-item restore-popup-model-overlay-local-storage">
                            <div className="restore-popup-model-overlay-source-icon">📁</div>
                            <div className="restore-popup-model-overlay-source-title">Local Storage</div>
                            <div className="restore-popup-model-overlay-source-path">C:\\25_gb_data_123</div>
                        </div>

                        <div className="restore-popup-model-overlay-source-item restore-popup-model-overlay-source-data">
                            <div className="restore-popup-model-overlay-source-icon">📊</div>
                            <div className="restore-popup-model-overlay-source-title">Source</div>
                            <div className="restore-popup-model-overlay-source-path">AB-Test1</div>
                        </div>
                    </div>

                    <div className="restore-popup-model-overlay-section">
                        <div className="restore-popup-model-overlay-section-title">🎯 Target Endpoint</div>
                        <div className="restore-popup-model-overlay-target-endpoint">
                            <input type="text" className="restore-popup-model-overlay-endpoint-input" placeholder="Please select target endpoint" readOnly />
                            <button className="restore-popup-model-overlay-select-btn"><span>🖥️</span> Select Endpoint</button>
                        </div>
                    </div>

                    <div className="restore-popup-model-overlay-section">
                        <div className="restore-popup-model-overlay-section-title">📍 Target Location</div>
                        <div className="restore-popup-model-overlay-target-location">
                            <input type="checkbox" className="restore-popup-model-overlay-checkbox" defaultChecked />
                            <input type="text" className="restore-popup-model-overlay-location-input" value="C:\\25_gb_data_123" readOnly />
                        </div>
                    </div>

                    <div className="restore-popup-model-overlay-section">
                        <div className="restore-popup-model-overlay-section-title">🔍 File Extensions</div>
                        <input type="text" className="restore-popup-model-overlay-extension-input" placeholder="Search Extensions (leave blank for all files)" />
                    </div>
                </div>

                <div className="restore-popup-model-overlay-modal-footer">
                    <button className="restore-popup-model-overlay-proceed-btn" onClick={proceedRestore} disabled={processing}>
                        <span className="btn-text">{btnText}</span>
                    </button>
                </div>
            </div>
        </>
    );
};

export default RestoreProgressPopup;
