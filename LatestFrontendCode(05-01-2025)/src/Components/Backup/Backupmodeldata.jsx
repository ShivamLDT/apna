import React, { useState, useEffect, useContext } from "react";
import "./BackupModal.css";
import driveIcon from "../../assets/drive.png";
import foldericon from "../../assets/folder.png";
import { Backupindex } from '../../Context/Backupindex';
import Endpoint from "./Endpoint";
import LoadingBar from "../../assets/Loading.gif"
import config from "../../config"
import axios from 'axios';
import axiosInstance from "../../axiosinstance";
import { UIContext } from "../../Context/UIContext";
import LoadingComponent from "../../LoadingComponent";
const Backupmodeldata = ({ setShowpopup, setSourceCheck }) => {
  const [path, setPath] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [isVisible, setIsVisible] = useState(true);
  const [serverData, setServerData] = useState();
  const [selectedPaths, setSelectedPaths] = useState([]);
  const { setSourceData, endPointAgentName } = useContext(Backupindex);
  const [loadingBar, setLoadingBar] = useState(true);
  const { setPopupEnable, setfolderlist, onechecktable, setonechecktable, setonecheckendpointlisttable, showEndpointBackup, setShowEndpointBackup } = useContext(UIContext);

  const handleClose = () => {
    setIsVisible(false);
    setShowpopup(false);
    setPopupEnable(false)
    // setSourceCheck(false);
    // setShowEndpointBackup(false)
  };



  useEffect(() => {
    const fetchData = async () => {
      try {
        const accessToken = localStorage.getItem("AccessToken");

        const response = await axiosInstance.post(`${config.API.Server_URL}/browse`, {
          path: path || "",
          node: endPointAgentName
        }, {
          headers: {
            "Content-Type": "application/json",
            token: accessToken,
          }
        });

        setServerData(response.data);
        setLoadingBar(false);
      } catch (error) {
        // Handle 500 status specifically
        if (error.response?.status === 500) {
          return;
        }
        console.error("An error occurred:", error);
      }
    };

    fetchData();
  }, [path]);

  const handleSvgclick = (pathName) => {
    setPath(pathName);
  };




  const handleCheckboxChange = (path) => {
    const isChecked = selectedPaths.includes(path);
    const normalizedPath = path.endsWith('/') ? path : `${path}/`;

    if (isChecked) {
      setSelectedPaths(prev =>
        prev.filter(p => !(p === path || p.startsWith(normalizedPath)))
      );
    } else {
      const nestedPaths = serverData?.paths
        ?.flatMap(d => [d.path, ...(d.contents?.map(c => c.path) || [])])
        ?.filter(p => p === path || p.startsWith(normalizedPath)) || [];

      setSelectedPaths(prev => [...new Set([...prev, ...nestedPaths])]);
    }
  };

  const handleSave = () => {
    setShowpopup(false);
    setSourceData((prevData) => [...prevData, ...selectedPaths]);
    setSourceCheck(true);
    setPopupEnable(false);
    // true for showendpoint seclted folder listr 
    setfolderlist(true);
    setonechecktable(false);
    setonecheckendpointlisttable(false);
    setShowEndpointBackup(true)
  };

  // if (!isVisible) return null;

  // if (loadingBar) return <div className="popup-overlayT">
  //   <div className="modal">
  //     <div className="flex items-center justify-center h-full">
  //       <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
  //         <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
  //           style={{ animation: 'oceanSlide 3s infinite' }} />
  //         <style>{`
  //     @keyframes oceanSlide {
  //       0% { transform: translateX(-150%); }
  //       66% { transform: translateX(0%); }
  //       100% { transform: translateX(150%); }
  //     }
  //   `}</style>
  //       </div>
  //     </div>
  //   </div>
  // </div>


  if (loadingBar) return <div className="popup-overlayT">
    <div className="modal">
      <LoadingComponent />
    </div>
  </div>



  return (
    <div className="popup-overlayT">
      <div className="modal">
        <div className="modal-header">
          <div className="modal-title">
            Select your data for backup
            <svg className="refresh-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <button className="close-button" onClick={handleClose}>
            <svg className="close-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="modal-content">
          <div className="search-container">
            <input
              type="text"
              className="search-input"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <div className="file-tree">
            {serverData?.paths?.map((drive, index) => {
              const filteredContents = drive.contents?.filter((item) =>
                item.name.toLowerCase().includes(searchTerm.toLowerCase())
              );
              if (!filteredContents?.length && searchTerm) return null;

              return (
                <div className="file-tree-container" key={index}>
                  {filteredContents?.length > 0 ? (
                    filteredContents.map((item, subIndex) => (
                      <div key={subIndex} className="main-icon-container">
                        <div className="img-lable-container">
                          <div className="flex items-center mr-2">
                            <input
                              type="checkbox"
                              checked={selectedPaths.includes(item.path)}
                              onChange={() => handleCheckboxChange(item.path)}
                              className="w-4 h-4 text-blue-600"
                            />
                          </div>
                          <div className="check-img-container" onClick={() => handleSvgclick(item.path)}>
                            <div className="icon-container">
                              <img className="icon-container-img" src={foldericon} alt="folder" />
                            </div>
                          </div>
                        </div>
                        <div className="name-container">
                          <span className="name-container-name">{item.name}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="main-icon-container">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={selectedPaths.includes(drive.path)}
                          onChange={() => handleCheckboxChange(drive.path)}
                          className="w-4 h-4 text-blue-600"
                        />
                      </div>
                      <div className="check-img-container" onClick={() => handleSvgclick(drive.path)}>
                        <div className="icon-container">
                          <img className="icon-container-img" src={driveIcon} alt="drive" />
                        </div>
                      </div>
                      <div className="name-container">
                        <span className="name-container-name">{drive.path}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <button onClick={handleSave} className="save-btn-1" type="button">Save</button>
        </div>
      </div>
    </div>
  );
};

export default Backupmodeldata;



