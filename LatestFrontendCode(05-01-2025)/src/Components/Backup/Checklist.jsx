import React, { useState, useEffect } from 'react';
import { Backupindex } from '../../Context/Backupindex';
import { useContext } from 'react';
import foldericon from "../../assets/folder.png";
import { decryptData } from "./encryptionUtils";
import pdfIcon from "./ExtensionIcon/pdf.png";
import excelIcon from "./ExtensionIcon/excel.png";
import docxIcon from "./ExtensionIcon/docx.png";
import pptIcon from "./ExtensionIcon/ppt.png";
import exeIcon from "./ExtensionIcon/exe.png";
import textIcon from "./ExtensionIcon/text.png";
import jpgIcon from "./ExtensionIcon/jpg.png";
import pngIcon from "./ExtensionIcon/png.png";
import jpegIcon from "./ExtensionIcon/jpeg.png";
import gifIcon from "./ExtensionIcon/gif.png";
import zipIcon from "./ExtensionIcon/zip.png";
import mp3Icon from "./ExtensionIcon/mp3.png";
import mp4Icon from "./ExtensionIcon/mp4.png";
import rarIcon from "./ExtensionIcon/rar.png";
import csvIcon from "./ExtensionIcon/csv.png";
import sqlIcon from "./ExtensionIcon/sql.png";
import emlIcon from "./ExtensionIcon/eml.png";
import aiIcon from "./ExtensionIcon/ai.png";
import xmlIcon from "./ExtensionIcon/xml.png";


const iconMap = {
  "./ExtensionIcon/pdf.png": pdfIcon,
  "./ExtensionIcon/excel.png": excelIcon,
  "./ExtensionIcon/docx.png": docxIcon,
  "./ExtensionIcon/ppt.png": pptIcon,
  "./ExtensionIcon/exe.png": exeIcon,
  "./ExtensionIcon/text.png": textIcon,
  "./ExtensionIcon/jpg.png": jpgIcon,
  "./ExtensionIcon/png.png": pngIcon,
  "./ExtensionIcon/jpeg.png": jpegIcon,
  "./ExtensionIcon/gif.png": gifIcon,
  "./ExtensionIcon/zip.png": zipIcon,
  "./ExtensionIcon/mp3.png": mp3Icon,
  "./ExtensionIcon/mp4.png": mp4Icon,
  "./ExtensionIcon/rar.png": rarIcon,
  "./ExtensionIcon/csv.png": csvIcon,
  "./ExtensionIcon/sql.png": sqlIcon,
  "./ExtensionIcon/eml.png": emlIcon,
  "./ExtensionIcon/ai.png": aiIcon,
  "./ExtensionIcon/xml.png": xmlIcon,

};

export default function Checklist({ backupName, selectedDestination, backupType, fileExtension, endPoint, sourceCheck }) {

  const now = new Date();
  now.setMinutes(now.getMinutes() + 1); // Add 1 minute
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const formattedTime = `${hours}:${minutes}`;

  const getNameFromPath = (path) => {
    const parts = path.split("\\");
    return parts[parts.length - 1] || "C:";
  };

  const [backupItems, setBackupItems] = useState([]);
  const [folderPath, setFolderPath] = useState();
  const [file, setFile] = useState('');
  const { itemToDeleteFileExtension, setItemToDeleteFileExtension, checkBoxData, setCheckBoxData, backupIndex, setBackupIndex, sourceData, setSourceData, nextruntimeCheckList, endPointAgentName, setEndPointAgentName, fileExtensionData, setfileExtensionData } = useContext(Backupindex);

  useEffect(() => {
    const items = [
      { label: `Backup Name: ${backupName}`, done: !!backupName },
      { label: `Destination: ${selectedDestination}`, done: !!selectedDestination },
      { label: `Backup Type: ${backupType}`, done: !!backupType },
      // { label: `File Extension: ${fileExtension}`, done: !!fileExtension },
      { label: `EndPoint: ${endPointAgentName}`, done: !!endPoint },
      // { label: `Next Run Time: ${nextruntimeCheckList}`, done: !!formattedTime }
    ];

    setBackupItems(items);
  }, [backupName, selectedDestination, backupType, fileExtension, endPointAgentName]);

  useEffect(() => {
    setCheckBoxData(true);
    // Cleanup function runs when component unmounts
    return () => {
      setCheckBoxData(false);
    };
  }, []);

  const HandleListClick = (name) => {
    const form_val = sessionStorage.getItem("encryptedBackupData");
    const decrypted = decryptData(form_val);
    const backupName1 = decrypted?.backupName;
    const selectedDestination1 = decrypted?.selectedDestination;
    const backupType1 = decrypted?.backupType;
    if (name.includes("Backup Name")) {
      setBackupIndex({ step: 0, updatedAt: Date.now() });
    }
    else if (name.includes("FileExtension")) {
      if (backupName1) {
        setBackupIndex({ step: 1, updatedAt: Date.now() });
      }
    }
    else if (name.includes("EndPoint")) {
      if (backupName1) {
        setBackupIndex({ step: 2, updatedAt: Date.now() });
      }
    }
  };




  useEffect(() => {
  }, [sourceData]);
  function handleDelete(path) {
    const deletedVal = fileExtensionData.filter((item) => item.fileExtensions !== path.fileExtensions);
   
    setfileExtensionData(deletedVal)
    setFile(deletedVal);
  }

  function handleDeleteFileExtenion(path) {
    setItemToDeleteFileExtension(path);
    const deletedVal = fileExtensionData.filter((item) => item.fileExtensions !== path.fileExtensions);
    setfileExtensionData(deletedVal)
    setFile(deletedVal);
  }

  function handleDeleteSource(path) {
    const deletedVal = sourceData.filter((item) => item !== path);
    setSourceData(deletedVal)
    // setfileExtensionData(deletedVal)
    // setFile(deletedVal);
  }

  useEffect(() => {
    if (sourceData) {
      const updatedEndpoints = sourceData?.map(path => ({
        path: path
      }));
      setFolderPath(updatedEndpoints);
    }
  }, [sourceData]);

  function HandleSourceClick() {
    setBackupIndex({ step: 1, updatedAt: Date.now() });
  }
  return (
    <div className="bg-white p-4 rounded shadow" style={{ height: '500px', overflow: 'scroll', overflowX: 'auto' }}>
      <div className="flex justify-between items-center mb-2">
        <h2 className="font-semibold">Checklist</h2>
      </div>

      <ul className="space-y-7">
        {backupItems.map((item, i) => (
          <li key={i} className="flex items-center space-x-3">
            <input type="checkbox" checked={item.done} readOnly />
            <span onClick={() => HandleListClick(item.label)} className={`${item.done ? 'text-black-500' : ''} cursor-pointer`}>{item.label}</span>
          </li>
        ))}
      </ul>

      <div className="main_div_folder">
        {fileExtensionData.length > 0 && (
          <>
            {/* Source line with checkbox */}
            <div className="source-name">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={fileExtension}
                  // onChange={() => handleCheckboxChange(sourceData[0])}
                  className="w-4 h-4"
                />
                <span onClick={HandleSourceClick}>FileExtension:</span>
              </label>
            </div>

            {/* Subfolders */}
            <div className="folder-list">
              {fileExtensionData?.map((path, index) => (
                <div key={index} className="folder-item flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <img src={path?.fileIcon} alt="folder" className="folder-icon w-5 h-5" />
                    <span className="folder-name">{path?.fileExtensions}</span>
                  </div>
                  <button
                    onClick={() => handleDeleteFileExtenion(path)}
                    className="text-red-500 hover:text-red-700 delete-btn-icon"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
      <div className="main_div_folder">
        {sourceData.length > 0 && (
          <>
            {/* Source line with checkbox */}
            <div className="source-name">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={sourceCheck}
                  // onChange={() => handleCheckboxChange(sourceData[0])}
                  className="w-4 h-4"
                />
                <span onClick={HandleSourceClick}>Source:</span>
              </label>
            </div>

            {/* Subfolders */}
            <div className="folder-list">
              {sourceData?.map((path, index) => (
                <div key={index} className="folder-item flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <img src={foldericon} alt="folder" className="folder-icon w-5 h-5" />
                    <span className="folder-name">{path}</span>
                  </div>
                  <button
                    onClick={() => handleDeleteSource(path)}
                    className="text-red-500 hover:text-red-700 delete-btn-icon"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}