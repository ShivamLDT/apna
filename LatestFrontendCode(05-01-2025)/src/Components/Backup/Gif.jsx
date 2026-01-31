import SubmitGif from "../../assets/uploading.gif"
import "./Gif.css";
const Gif = () => {
  return <div className="submit_overlayb">
    <div className="submit_alert-containerb">
      <img src={SubmitGif} alt="Loading..." style={{ minWidth: "80%" }} />
      <div className="submit_alertb">
        <div className="submit_innerb">
          <div className="submit_titleb">Submitting....</div>
        </div>
      </div>
    </div>
  </div>
}

export default Gif