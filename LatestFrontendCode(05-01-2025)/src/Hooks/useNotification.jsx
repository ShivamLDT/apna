import axiosInstance from "../axiosinstance";
import config from "../config";

export const sendNotification = async (message) => {
    try {
        const accessToken = localStorage.getItem("AccessToken");
        if (!accessToken) {
            throw new Error("No token found in localStorage");
        }

        const timestamp = new Date().toISOString();

        const response = await axiosInstance.post(
            `${config.API.FLASK_URL}/eventnotifications`,
            { message, timestamp },
            {
                headers: {
                    "Content-Type": "application/json",
                    token: accessToken,
                },
            }
        );

        return response.data;
    } catch (error) {
        console.error("Error sending notification:", error);
        throw error;
    }
};
