import React from 'react';
import "./Backup.css";

export default function Calendar() {
  const days = [...Array(31).keys()].map(d => d + 1);

  return (
    
    <div className="bg-white p-4 rounded shadow" style={{ marginTop: "5px" }}>
      <div className="toggle-btn-main-container p-4">
        <div className='toggle-btn-container'>
          <div className="toggle-btn-local-container flex justify-between">
            <div className="local_storage_heading">
              <h3>On-Premise</h3>
            </div>
            <div className="local_storage_container">
              <label className="checkbox_wrap">
                <input type="checkbox" name="checkbox" className="checkbox_inp"/>
                  <span className="checkbox_mark"></span>
              </label>
            </div>

          </div>

          <div className="toggle-btn-local-container flex justify-between pt-3">
            <div className="local_storage_heading">
              <h3>Google Drive</h3>
            </div>
            <div className="local_storage_container">
               <label className="checkbox_wrap">
                <input type="checkbox" name="checkbox" className="checkbox_inp"/>
                  <span className="checkbox_mark"></span>
              </label>
            </div>

          </div>

          <div className="toggle-btn-local-container flex justify-between pt-3">
            <div className="local_storage_heading">
              <h3>One Drive</h3>
            </div>
            <div className="local_storage_container">
              <label className="checkbox_wrap">
                <input type="checkbox" name="checkbox" className="checkbox_inp"/>
                  <span className="checkbox_mark"></span>
              </label>
            </div>

          </div>


          <div className="toggle-btn-local-container flex justify-between pt-3">
            <div className="local_storage_heading">
              <h3>AWS</h3>
            </div>
            <div className="local_storage_container">
              <label className="checkbox_wrap">
                <input type="checkbox" name="checkbox" className="checkbox_inp"/>
                  <span className="checkbox_mark"></span>
              </label>
            </div>

          </div>


          <div className="toggle-btn-local-container flex justify-between pt-3">
            <div className="local_storage_heading">
              <h3>Azure</h3>
            </div>
            <div className="local_storage_container">
              <label className="checkbox_wrap">
                <input type="checkbox" name="checkbox" className="checkbox_inp"/>
                  <span className="checkbox_mark"></span>
              </label>
            </div>

          </div>


          <div className="toggle-btn-local-container flex justify-between pt-3">
            <div className="local_storage_heading">
              <h3>NAS/UNC</h3>
            </div>
            <div className="local_storage_container">
             <label className="checkbox_wrap">
                <input type="checkbox" name="checkbox" className="checkbox_inp"/>
                  <span className="checkbox_mark"></span>
              </label>
            </div>

          </div>
        </div>
      </div>


    </div>
  );
}
