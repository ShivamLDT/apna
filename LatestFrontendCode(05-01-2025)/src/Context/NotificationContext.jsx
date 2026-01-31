import React, { createContext, useState, useMemo } from "react";

export const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notificationData, setNotificationData] = useState([]);
  const [jobNotificationName, setJobNotificationName] = useState("");
  const [resultCount, setResultCount] = useState(0);
  const [checkApi, setCheckApi] = useState(false);

  const value = useMemo(
    () => ({
      notificationData, setNotificationData,
      jobNotificationName, setJobNotificationName,
      resultCount, setResultCount,
      checkApi, setCheckApi
    }),
    [notificationData, jobNotificationName, resultCount, checkApi]
  );

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};
