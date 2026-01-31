/* Modal.js*/
import React from "react";
import "./Popup.css";
const Popup = ({ children, onClose }) => {
  return (
    <div className="modal-overlayPop" onClick={onClose}>
      <div className="modal-contentPop" onClick={(e) => e.stopPropagation()}>
        <div className="popup-reset-text-align">
          <button className="modal-close-btnP" onClick={onClose}></button>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Popup;
