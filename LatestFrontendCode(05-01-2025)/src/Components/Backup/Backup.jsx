import React, { useState } from 'react';
import ProgressTracker from './ProgressTracker';
import Tasks from './Tasks';
import Checklist from './Checklist';
import Financials from './Financials';
import Calendar from './Calendar';
import { decryptData, encryptData } from "./encryptionUtils";
export default function Backup() {

    const getInitialData = () => {
        const encrypted = localStorage.getItem("encryptedBackupData");
        if (encrypted) {
            const decrypted = decryptData(encrypted);
            return decrypted || {};
        }
        return {};
    };

    const initialData = getInitialData();
    // const [backupName, setBackupName] = useState('');
    // const [selectedDestination, setSelectedDestination] = useState('On-Premise');
    // const [backupType, setBackupType] = useState('Full Backup');
    const [backupName, setBackupName] = useState(initialData.backupName || "");
    const [selectedDestination, setSelectedDestination] = useState(initialData.selectedDestination || "On-Premise");
    const [backupType, setBackupType] = useState(initialData.backupType || "Full Backup");
    const [fileExtension, setFileExtension] = useState('');
    const [endPoint, setEndPoint] = useState('');
    const [schedule, setSchedule] = useState('');
    const [scheduleType, setScheduleType] = useState('');
    const [profileEndPoint, setProfileEndPoint] = useState('');
    const [nextRunTime, setNextRunTime] = useState('');
    const [sourceCheck, setSourceCheck] = useState();


    return (
        <div className="flex-1 p-6 backup-content">
  <div className="w-full">
    <Tasks
      backupName={backupName}
      setBackupName={setBackupName}
      selectedDestination={selectedDestination}
      setSelectedDestination={setSelectedDestination}
      backupType={backupType}
      setBackupType={setBackupType}
      setFileExtension={setFileExtension}
      setEndPoint={setEndPoint}
      setSchedule={setSchedule}
      setScheduleType={setScheduleType}
      setProfileEndPoint={setProfileEndPoint}
      setNextRunTime={setNextRunTime}
      setSourceCheck={setSourceCheck}
      endPoint={endPoint}
      setNext
    />
  </div>
</div>

    );
}