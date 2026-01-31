import { useEffect, useState } from 'react';
import axiosInstance from '../../../axiosinstance';
import config from '../../../config';
import './GDriveModal.css';

const GDriveModal = ({
  closeGdrivePopup,
  gdriveModelData,
  setDestinationName,
  setSelectedDestination,
  setDestinationNamePayload,
  destinationPayload
}) => {
  const [serverMsg, setServerMsg] = useState("");
  const [loadingMsg, setLoadingMsg] = useState(false);
  const [isConfigured, setIsConfigured] = useState(false);
  const accessToken = localStorage.getItem("AccessToken");

  const fetchServerStatus = async () => {
    try {
      setLoadingMsg(true);

      // Determine the correct repo name for the API
      let repoName = gdriveModelData?.name;
      if (gdriveModelData?.name === "Google Drive") {
        repoName = "GDRIVE";
      } else if (gdriveModelData?.name === "One Drive") {
        repoName = "ONEDRIVE";
      } else if (gdriveModelData?.name === "AWS") {
        repoName = "AWS";
      } else if (gdriveModelData?.name === "Azure") {
        repoName = "AZURE";
      }

      const response = await axiosInstance.post(
        `${config.API.Server_URL}/validate_cred`,
        {
          action: "repo_check",
          rep: repoName
        },
        {
          headers: {
            "Content-Type": "application/json",
            token: `${accessToken}`,
          }
        }
      );

      const isValid = response?.data?.valid;
      setIsConfigured(isValid);

      if (isValid) {
        setServerMsg("✅ Configuration verified successfully! You can proceed with this destination.");

        // ✅ Set all destination data when configuration is valid
        const payloadMap = {
          "Google Drive": "GDRIVE",
          "One Drive": "ONEDRIVE",
          "AWS": "AWSS3",
          "Azure": "AZURE"
        };

        setDestinationNamePayload(payloadMap[gdriveModelData?.name]);
        setDestinationName(gdriveModelData?.name);
        setSelectedDestination(gdriveModelData?.name);

      } else {
        setServerMsg("❌ Configuration not found or invalid. Please configure your credentials first.");
        // Clear any existing selections
        setDestinationNamePayload("");
        setDestinationName("");
        setSelectedDestination("");
      }
    } catch (err) {
      console.error("Failed to fetch status:", err);
      setIsConfigured(false);
      setServerMsg("❌ Failed to verify configuration. Please try again or check your credentials.");
      // Clear selections on error
      setDestinationNamePayload("");
      setDestinationName("");
      setSelectedDestination("");
    } finally {
      setLoadingMsg(false);
    }
  };

  useEffect(() => {
    fetchServerStatus();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        const infoPopup = document.getElementById('GDriveModal-infoPopup');
        if (infoPopup?.classList.contains('GDriveModal-show')) {
          closeInfoPopup();
        } else {
          handleClose();
        }
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleClose = () => {
    // ❌ Don't set destination when closing without valid configuration
    if (!isConfigured) {
      // Clear any selections made before validation
      setDestinationName('');
      setSelectedDestination('');
      setDestinationNamePayload('');
    }
    closeGdrivePopup();
  };

  const showInfoPopup = () => {
    document.getElementById('GDriveModal-infoOverlay')?.classList.add('GDriveModal-show');
    document.getElementById('GDriveModal-infoPopup')?.classList.add('GDriveModal-show');
  };

  const closeInfoPopup = () => {
    document.getElementById('GDriveModal-infoOverlay')?.classList.remove('GDriveModal-show');
    document.getElementById('GDriveModal-infoPopup')?.classList.remove('GDriveModal-show');
  };

  const handleOkClick = () => {
    if (isConfigured) {
      // Configuration is valid, close and keep selection
      closeGdrivePopup();
    } else {
      // Configuration is invalid, clear selection and close
      setDestinationName('');
      setSelectedDestination('');
      setDestinationNamePayload('');
      closeGdrivePopup();
    }
  };

  return (
    <div className="GDriveModal-mainGDrive-container">
      <div className="GDriveModal-background-content" />

      <div className="GDriveModal-overlay" onClick={handleClose} />

      <div className="GDriveModal-modal">
        <div className="GDriveModal-modal-header">
          <div className="GDriveModal-modal-title-section">
            <div className="GDriveModal-gdrive-logo">
              <img src={gdriveModelData?.image} alt={gdriveModelData?.name} />
            </div>
            <h2 className="GDriveModal-modal-title">{gdriveModelData?.name}</h2>
          </div>
          <div className="GDriveModal-header-icons">
            <div className="GDriveModal-info-icon" onClick={showInfoPopup}>i</div>
            <button className="GDriveModal-close-btn" onClick={handleClose}>&times;</button>
          </div>
        </div>

        <div className="GDriveModal-modal-body">
          <h3 className="GDriveModal-main-heading">
            {gdriveModelData?.name} Configuration Status
          </h3>
          {loadingMsg ? (
            <p className="GDriveModal-description">
              Verifying configuration, please wait...
            </p>
          ) : (
            <p className="GDriveModal-description" style={{
              color: isConfigured ? '#1a7f37' : '#d1242f',
              fontWeight: '500'
            }}>
              {serverMsg}
            </p>
          )}
          {!loadingMsg && !isConfigured && (
            <p className="GDriveModal-description" style={{ fontSize: '13px', marginTop: '10px' }}>
              Click on the <span className="GDriveModal-inline-info-icon">i</span> icon for configuration instructions.
            </p>
          )}
        </div>

        <div className="GDriveModal-modal-footer">
          <button
            className="GDriveModal-ok-btn"
            onClick={handleOkClick}
            disabled={loadingMsg}
          >
            {loadingMsg ? 'Checking...' : 'OK'}
          </button>
        </div>
      </div>

      <div className="GDriveModal-info-overlay" id="GDriveModal-infoOverlay" onClick={closeInfoPopup} />

      <div className="GDriveModal-info-popup" id="GDriveModal-infoPopup" onClick={(e) => e.stopPropagation()}>
        <div className="GDriveModal-info-popup-header">
          <div className="GDriveModal-info-popup-title">
            <div className="GDriveModal-info-icon">i</div>
            <span>Configuration Instructions</span>
          </div>
          <button className="GDriveModal-info-popup-close" onClick={closeInfoPopup}>&times;</button>
        </div>

        <div className="GDriveModal-info-popup-body">
          <div className="GDriveModal-step-item">
            <div className="GDriveModal-step-header">Step 1:</div>
            <div className="GDriveModal-step-content">Navigate to ApnaBackupServer folder in C Drive</div>
          </div>
          <div className="GDriveModal-step-item">
            <div className="GDriveModal-step-header">Step 2:</div>
            <div className="GDriveModal-step-content">Run abrc.exe as Administrator</div>
          </div>
          <div className="GDriveModal-step-item">
            <div className="GDriveModal-step-header">Step 3:</div>
            <div className="GDriveModal-step-content">Configure your {gdriveModelData?.name} credentials and save</div>
          </div>
          <div className="GDriveModal-step-item">
            <div className="GDriveModal-step-header">Step 4:</div>
            <div className="GDriveModal-step-content">Return here and try again to verify the configuration</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GDriveModal;