import { useState, useContext, useEffect, } from "react";
import { Backupindex } from "../../Context/Backupindex";
import { tr } from "date-fns/locale/tr";
import { UIContext } from "../../Context/UIContext";

const Dialogbox = ({ setShowAlertPopup, }) => {
   const {setDialogBox,setonecheckendpointlisttable,setShowEndpointBackup} = useContext(UIContext)
  const {  sourceData, setEndPointAgentName,setEndpointagentname, endPointAgentName, setSourceData } = useContext(Backupindex)

  const [isOpen, setIsOpen] = useState(true);

  const handleClose = () => {
    setShowAlertPopup(false);
    setIsOpen(true);
    setDialogBox(false);
  };



  const handleConfrim = () => {
    setShowAlertPopup(false);
    setIsOpen(false);
    setDialogBox(true);
    setonecheckendpointlisttable(true)
    setShowEndpointBackup(false);
    setSourceData('');
    setEndPointAgentName('');
    setEndpointagentname(" ")
  };

  return (
    <div>
      {isOpen && (
        <div
          onClick={handleClose}
          className="fixed inset-0 z-[999] grid h-screen w-screen place-items-center bg-black bg-opacity-60 backdrop-blur-sm transition-opacity duration-300"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="relative m-4 p-4 w-2/5 min-w-[40%] max-w-[40%] rounded-lg bg-white shadow-sm"
          >
            <div className="flex items-center pb-4 text-xl font-medium text-slate-800">
              Are You Sure
            </div>
            <div className="relative border-t border-slate-200 py-4 leading-normal text-slate-600 font-light">
              If you click the Confirm button, all selected folders will be deleted. Are you sure?
            </div>
            <div className="flex flex-wrap items-center pt-4 justify-end">
              <button
                onClick={handleClose}
                className="rounded-md border border-transparent py-2 px-4 text-center text-sm transition-all text-slate-600 hover:bg-slate-100 focus:bg-slate-100 active:bg-slate-100 disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
                type="button"
              >
                Cancel
              </button>
              <button
                onClick={handleConfrim}
                className="rounded-md bg-green-600 py-2 px-4 border border-transparent text-center text-sm text-white transition-all shadow-md hover:shadow-lg focus:bg-green-700 focus:shadow-none active:bg-green-700 hover:bg-green-700 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none ml-2"
                type="button"
                style={{ backgroundColor: "red" }}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dialogbox;
