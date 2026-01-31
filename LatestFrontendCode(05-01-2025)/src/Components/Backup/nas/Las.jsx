/**19/03 */
import React, { useState, useEffect, useRef } from "react";
// import NAS from "../../../../Image/nas.png";
import NAS from "../../../Image/nas.png"
import { RxCross2 } from "react-icons/rx";
import PC from "../../../Image/desktop.png";
import FOLDER from "../../../Image/folder.png";
import Loader from "../../../Image/RD.gif";
import "./Nas.css";
import { IoMdClose, IoMdRefresh } from "react-icons/io";
import config from "../../../config";
import axios from "axios";
import Loaderr from "../../../Image/loader2.gif";
import { FaEye, FaEyeSlash } from 'react-icons/fa'; // Import eye icons
import axiosInstance from "../../../axiosinstance";
const LAN = ({ onClose, setShowNasPopup, setDestinationName, setSelectedDestination, setDestinationNamePayload }) => {
  const [path, setPath] = useState("");
  const [displayIP, setDisplayIP] = useState("");
  const [displayPath, setDisplayPath] = useState(""); // New state for displaying selected folder
  const [node, setNode] = useState(null);
  // const [port, setPort] = useState("22");
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const [data, setData] = useState([]);
  const [showLanPopup, setShowLanPopup] = useState(false);
  const [showComputerPopup, setShowComputerPopup] = useState(false); // New state for computer name popup
  const [computerNames, setComputerNames] = useState([]); // New state for computer names
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [selectedComputer, setSelectedComputer] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingComputers, setIsLoadingComputers] = useState(false); // State for loading computers
  const [error, setError] = useState(null)
  const [pathUNC, setPathUNC] = useState(null)
  const [nodeIdCheck, setNodeIdCheck] = useState(null)
  const [nodeCheck, setNodeCheck] = useState(null)
  // const [portCheck, setPortCheck] = useState(null)
  const [nodePathCheck, setNodePathCheck] = useState(null)
  const [passwordCheck, setPasswordCheck] = useState(null)

  const accessToken = localStorage.getItem('AccessToken')
  useEffect(() => {
    if (showComputerPopup) {
      handleFetchComputers();
    }
  }, [showComputerPopup]);

  const handleTestConnection = async (method) => {
    setIsLoading(true);

    if (!node) {
      setError('Computer Name is required!');
      setNodeCheck(true);
      setNodeIdCheck(false);
      setNodePathCheck(false);
      setPasswordCheck(false);
      setIsLoading(false);
      return;
    }

    // if (!port) {
    //   setError('Port is required!');
    //   setPortCheck(true);
    //   setNodeCheck(false);
    //   setNodeIdCheck(false);
    //   setNodePathCheck(false);
    //   setPasswordCheck(false);
    //   setIsLoading(false);
    //   return;
    // }

    const updatedData = data.map((folder) => {
      if (folder.path === clickedItem.path) {
        folder.isOpen = !folder.isOpen;
      }
      return folder;
    });

    const payload = {
      path: path,
      node: node,
      // port: port,
      noidadd: userId,
      noidacc: password,
      method: method,
      donl: true,
    };

    if (method === ".") {
      payload.noidadd = "UID";
      payload.node = "CN";
      payload.noidacc = "PASS";
    }

    try {
      const response = await axiosInstance.post(`${config.API.Server_URL}/api/browseUNC`, payload, {
        headers: {
          "Content-Type": "application/json",
          token: accessToken,
        },
      });

      const result = response.data;

      if (result.message !== undefined) {
        setResponseMessage(result.message || JSON.stringify(result.message));
        setShowLanPopup(false);
        setShowComputerPopup(false);
      } else if (method === "browse") {
        setData(result.paths || []);
        setShowLanPopup(true);
      } else if (method === "trace") {
        setResponseMessage(result.message || JSON.stringify(result.message));
      } else if (method === ".") {
        setComputerNames(result.nodes || []);
        setShowComputerPopup(true);
      } else {
        setResponseMessage("Unexpected response received.");
        alert("Unexpected response received.");
      }

    } catch (error) {
      console.error("Connection test failed:", error);

      // Handle different types of errors
      let errorMessage = "Connection test failed";
      if (error.response) {
        // Server responded with error status
        errorMessage = error.response.data?.message || `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Network error
        errorMessage = "Network error - please check your connection";
      }

      setError(errorMessage);
      setResponseMessage(errorMessage);

    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!isLoadingComputers && data.length === 0 && showLanPopup) {
      setResponseMessage("Check your Internet/Credentials for Configuration.");
    } else {
      setResponseMessage("");
    }
  }, [data, showLanPopup, isLoadingComputers]);



  const handleToggleFolder = async (clickedItem) => {
    const updatedData = data.map((folder) => {
      if (folder.path === clickedItem.path) {
        folder.isOpen = !folder.isOpen;
      }
      return folder;
    });

    setData(updatedData);

    if (!clickedItem.isOpen) {
      const payload = {
        path: clickedItem.path,
        node: node,
        // port: port,
        noidadd: userId,
        noidacc: password,
        method: "browse",
        donl: true,
      };

      setData([]);

      try {
        const response = await axiosInstance.post(`${config.API.Server_URL}/api/browseUNC`, payload, {
          headers: {
            "Content-Type": "application/json",
            token: accessToken
          }
        });

        const result = response.data;
        const updatedFolders = data.map((folder) => {
          if (folder.path === clickedItem.path) {
            return { ...folder, contents: result.paths || [] };
          }
          return folder;
        });
        setData(updatedFolders);

      } catch (error) {
        console.error("Error fetching folder contents:", error);

        // Handle different error types
        if (error.response) {
          console.error("Server error:", error.response.status, error.response.data);
        } else if (error.request) {
          console.error("Network error - no response received");
        } else {
          console.error("Request setup error:", error.message);
        }

        // Optionally revert the folder state on error
        const revertedData = data.map((folder) => {
          if (folder.path === clickedItem.path) {
            folder.isOpen = false; // Close the folder on error
          }
          return folder;
        });
        setData(revertedData);
      }
    }
  };

  const handleFetchComputers = async () => {
    setIsLoadingComputers(true);
    try {
      const response = await axiosInstance.get(`${config.API.Server_URL}/api/getComputers`, {
        headers: {
          "Content-Type": "application/json",
          token: accessToken
        },
      });

      setComputerNames(response.data.nodes || []);

    } catch (error) {
      console.error("Error fetching computers:", error);

      // Enhanced error handling
      if (error.response) {
        console.error("Server error:", error.response.status, error.response.data);
      } else if (error.request) {
        console.error("Network error - no response received");
      } else {
        console.error("Request setup error:", error.message);
      }

    } finally {
      setIsLoadingComputers(false);
    }
  };

  const handleSelectFolder = (folder) => {
    setDisplayPath(folder.path);
    setSelectedFolder(folder.path);
    setShowLanPopup(false);

    // Save payload in localStorage
    const payloadToSave = {
      loc: folder.path,
      ipc: node,
      // port: port,
      uid: userId,
      idn: password,
    };
    localStorage.setItem("storage", JSON.stringify(payloadToSave));
  };

  const handleSelectComputer = (computer) => {
    setDisplayIP(computer.ip);
    setNode(computer.ip);
    setSelectedComputer(computer.ip);
    setShowComputerPopup(false);

    // Save entire payload in localStorage
    const payloadToSave = {
      loc: path,
      ipc: node,
      // port: port,
      uid: userId,
      idn: password,
    };
    localStorage.setItem("storage", JSON.stringify(payloadToSave));

    if (userId !== "" && password !== "") handleTestConnection("browse");
  };


  const renderFolders = (folders) => {
    if (!Array.isArray(folders)) {
      return null;
    }

    return folders.map((folder) => (
      <div
        key={folder.path}
        className={`folder-item ${selectedFolder === folder.path ? "selected-folder" : ""}`}
        onClick={() => handleSelectFolder(folder)}
      >
        <div className="Nas_lanfolder-content">
          <img src={FOLDER} alt="Folder" className="Nas_folder-icon" />
          <span>{folder.path}</span>
        </div>
      </div>
    ));
  };

  const renderComputers = (computers) => {
    if (!Array.isArray(computers)) {
      return null;
    }

    return computers.map((computer) => (
      <div
        key={computer.ip}
        className={`Nas_computer-item ${selectedComputer === computer.ip ? "Nas_selected-computer" : ""}`}
        onClick={() => handleSelectComputer(computer)}
      >
        <div className="Nas_lancomputer-content">
          <img src={PC} className="Nas_computer-icon" alt="Computer" />
          <span>{computer.hostname}</span>
          <span>({computer.ip})</span>
        </div>
      </div>
    ));


  };

  const handleClose = () => {
    onClose();
  };

  const closeUNC = () => {
    if (!node) {
      setError('Computer Name is required!');
      setNodeCheck(true);
      setNodeIdCheck(false);
      setNodePathCheck(false);
      setPasswordCheck(false);
      alert('Computer Name is required!'); // Show alert here
      return;
    }
    // else if (!port) {
    //   setError('Port is required!');
    //   setPortCheck(true);
    //   setNodeCheck(false);
    //   setNodeIdCheck(false);
    //   setNodePathCheck(false);
    //   setPasswordCheck(false);
    //   alert('Port is required!');
    //   return;
    // } 
    else if (!password) {
      setError('Password is required!');
      setNodeCheck(false);
      setNodeIdCheck(false);
      setNodePathCheck(false);
      setPasswordCheck(true);
      alert('Password is required!'); // Show alert here
      return;
    } else if (!userId) {
      setError('User Id is required!');
      setNodeCheck(false);
      setNodeIdCheck(true);
      setNodePathCheck(false);
      setPasswordCheck(false);
      alert('User Id is required!'); // Show alert here
      return;
    } else if (!(displayPath || pathUNC)) {
      setError('Path is required!');
      setNodeCheck(false);
      setNodeIdCheck(false);
      setNodePathCheck(true);
      setPasswordCheck(false);
      alert('Path is required!'); // Show alert here
      return;
    }

    setDestinationNamePayload("UNC");
    setDestinationName("NAS/UNC");
    setSelectedDestination("NAS/UNC");

    const payloadToSave = {
      loc: displayPath,
      ipc: node,
      // port: port,
      uid: userId,
      idn: password,
    };
    localStorage.setItem("storage", JSON.stringify(payloadToSave));

    onClose();
  };
  useEffect(() => {
    if (showLanPopup) {
      setIsLoadingComputers(true);

      setTimeout(() => {
        fetchFolders();
      }, 700);
    }
  }, [showLanPopup]);

  const fetchFolders = async () => {
    try {
      const response = await axiosInstance.get(`${config.API.Server_URL}/api/folders`);
      setData(response.data);
    } catch (error) {
      console.error("Error loading folders:", error);

      // Enhanced error handling
      if (error.response) {
        console.error("Server error:", error.response.status, error.response.data);
      } else if (error.request) {
        console.error("Network error - no response received");
      } else {
        console.error("Request setup error:", error.message);
      }
    } finally {
      setIsLoadingComputers(false);
    }
  };

  const handleCloses = () => {
    setShowComputerPopup(false);
  };

  const handleClosePopup = () => {
    setShowLanPopup(false);
  };

  const handleCloseComputerPopup = () => {
    setShowComputerPopup(false);
  };

  const handleInputChange = (e) => {
    setDisplayIP(e.target.value);
  };


  const passwordInputRef = useRef(null);
  const UserInputRef = useRef(null);
  const PathInputRef = useRef(null);
  // const portInputRef = useRef(null);

  // Function to handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (passwordInputRef.current) {
        passwordInputRef.current.focus();
      }
    }
  };
  const handleKeyUser = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (UserInputRef.current) {
        UserInputRef.current.focus();
      }
    }
  };

  // const handleKeyPort = (e) => {
  //   if (e.key === 'Enter') {
  //     e.preventDefault();
  //     if (portInputRef.current) {
  //       portInputRef.current.focus();
  //     }
  //   }
  // };

  const handleKeyPath = (e) => {
    if (e.key === 'Enter') {
      handleTestConnection("browse");
      e.preventDefault();
      if (PathInputRef.current) {
        PathInputRef.current.focus();
      }
    }
  };


  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  // Function to handle the toggle of password visibility
  const togglePasswordVisibility = () => {
    setIsPasswordVisible(prevState => !prevState);
  };


  return <>

    <div className="Nas_blur-background" style={{ marginTop: "0px" }}>
      <div className="Nas_popup-containerglan">
        <div className="Nas_popup-headerlan">
          <img src={NAS} alt="NAS" />
          <div className="Nas_popup-titlelan">NAS/UNC</div>

          <button className="Nas_close-button" onClick={handleClose}>
            <IoMdClose onClick={handleClose} />
          </button>
        </div>
        <div className="Nas_popup-contentnas">
          <div className="Nas_form-row">
            <div className="Nas_form-group Nas_form-group-half">
              <label htmlFor="node" className="Nas_node-label">Computer Name</label>
              <input className="Nas_input"
                type="text"
                placeholder="Type your Ip address"
                id="node"
                value={node}
                onChange={(e) => setNode(e.target.value)}
                onKeyPress={(e) => handleKeyUser(e, UserInputRef)}
                required
              />
            </div>
            {/* <div className="Nas_form-group Nas_form-group-half">
              <label htmlFor="port" className="Nas_node-label">Port</label>
              <input
                className="Nas_input"
                ref={portInputRef}
                type="text"
                placeholder="22"
                id="port"
                value={port}
                onChange={(e) => setPort(e.target.value)}
                onKeyPress={(e) => handleKeyUser(e, UserInputRef)}
                required
              />
            </div> */}
          </div>

          {nodeCheck && (
            <div className="Nas_unc-error-container">
              <div className="Nas_unc-error">{error}</div>
            </div>
          )}
          {/* {portCheck && (
            <div className="Nas_unc-error-container">
              <div className="Nas_unc-error">{error}</div>
            </div>
          )} */}
          <div className="Nas_form-group">
            <label htmlFor="userId" className="Nas_node-label">User ID:</label>
            <input
              className="Nas_input"
              ref={UserInputRef}
              type="text"
              placeholder="User ID"
              id="userId"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e, passwordInputRef)}
              required
            />
          </div>

          {nodeIdCheck && (
            <div className="Nas_unc-error-container">
              <div className="Nas_unc-error">{error}</div>
            </div>
          )}

          <div className="Nas_form-group">
            <label htmlFor="password" className="Nas_node-label">Password:</label>
            <div className="Nas_password-input-container">
              <input
                ref={passwordInputRef}
                type={isPasswordVisible ? "text" : "password"}
                placeholder="Password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={(e) => handleKeyPath(e, PathInputRef)}
                required
                className="Nas_input"
              />
              <span
                type="button"
                className="Nas_eye-icond"
                onClick={togglePasswordVisibility}
              >
                {isPasswordVisible ? <FaEyeSlash /> : <FaEye />}
              </span>
            </div>
          </div>

          {passwordCheck && (
            <div className="Nas_unc-error-container">
              <div className="Nas_unc-error">{error}</div>
            </div>
          )}

          <div className="Nas_form-group">
            <label htmlFor="path" className="Nas_node-label">Path</label>
            <input
              ref={PathInputRef}
              type="text"
              id="path"
              value={displayPath}
              readOnly
              placeholder="Select Path From Destination Folder"
              onKeyPress={(e) => handleKeyPath(e, PathInputRef)}
              required
              className="Nas_input"
            />
          </div>

          {nodePathCheck && (
            <div className="Nas_unc-error-container">
              <div className="Nas_unc-error">{error}</div>
            </div>
          )}

          <div className="Nas_lanform-btns">
            <button type="button" className="Nas_test-connection-button" onClick={closeUNC}>
              Save
            </button>
            <button
              type="button"
              className="Nas_test-connection-button"
              onClick={() => handleTestConnection("browse")}
            >
              {isLoading ? (
                <span className="Nas_searching-text">
                  Searching....<span className="Nas_animated-dots">...</span>
                </span>
              ) : (
                "Select Destination Folder"
              )}
            </button>
          </div>
        </div>

        {responseMessage && (
          <div className="Nas_alert-overlay">
            <div className="Nas_alert-status">{responseMessage}</div>
          </div>
        )}

        {showLanPopup && (
          <div className="Nas_popup-overlay">
            <div className="Nas_popup-Lanbrowse">
              <h2 className="Nas_backup-h2">Select Your Destination</h2>
              <div className="Nas_popup-actions">
                <button className="Nas_popup-action-button" onClick={handleClosePopup}>
                  <RxCross2 />
                </button>
              </div>
              <div className="Nas_file-browserlan">
                {isLoadingComputers ? (
                  <div className="Nas_loading-overlay">
                    <img className="Nas_loading-indicator" src={Loader} alt="loading indicator" />
                  </div>
                ) : (
                  renderFolders(data)
                )}
              </div>
              <p>{responseMessage}</p>
            </div>
          </div>
        )}

        {showComputerPopup && (
          <div className="Nas_popup-overlay">
            <div className="Nas_popup-Lanbrowse">
              <button className="Nas_close-button" onClick={handleCloses}>
                <IoMdClose onClick={handleCloses} />
              </button>
              <h2 className="Nas_backup-h2">
                Select Your Computer
                <button
                  className="Nas_refresh-button"
                  onClick={handleFetchComputers}
                  disabled={isLoadingComputers}
                >
                  {isLoadingComputers ? <i className="bx bx-refresh bx-spin"></i> : <IoMdRefresh />}
                </button>
              </h2>
              <div className="Nas_popup-actions"></div>
              <div className="Nas_file-browserlan">
                {isLoadingComputers ? (
                  <div className="Nas_loading-overlay">
                    <img className="Nas_loading-indicator" src={Loaderr} alt="loading indicator" />
                  </div>
                ) : (
                  renderComputers(computerNames)
                )}
              </div>
            </div>
          </div>
        )}
      </div>

    </div>



  </>

};

export default LAN;