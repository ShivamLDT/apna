import React from "react";
import { RestoreProvider } from "./RestoreContext";
import { UIProvider } from "./UIContext";
import { NotificationProvider } from "./NotificationContext";

const AppProviders = ({ children }) => (
  <RestoreProvider>
    <UIProvider>
      <NotificationProvider>
        {children}
      </NotificationProvider>
    </UIProvider>
  </RestoreProvider>
);  

export default AppProviders;
