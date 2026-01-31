import { useEffect, useRef, useCallback, useState } from "react";
import { useAuth } from "./AuthContext";

const INACTIVITY_LIMIT = 3 * 60 * 1000; // 3 minutes total
const WARNING_DURATION = 30 * 1000;     // last 30 seconds warning

export default function useInactivityLogout() {
    const { logout, isLoggedIn } = useAuth();

    const inactivityTimeoutRef = useRef(null);
    const countdownIntervalRef = useRef(null);

    const [showWarning, setShowWarning] = useState(false);
    const [secondsLeft, setSecondsLeft] = useState(30);

    // ---------- Utility ----------
    const clearAllTimers = () => {
        if (inactivityTimeoutRef.current) {
            clearTimeout(inactivityTimeoutRef.current);
            inactivityTimeoutRef.current = null;
        }
        if (countdownIntervalRef.current) {
            clearInterval(countdownIntervalRef.current);
            countdownIntervalRef.current = null;
        }
    };

    // ---------- Start Warning ----------
    const startWarningCountdown = useCallback(() => {
        setShowWarning(true);
        setSecondsLeft(30);

        countdownIntervalRef.current = setInterval(() => {
            setSecondsLeft(prev => {
                if (prev <= 1) {
                    clearAllTimers();
                    logout();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
    }, [logout]);

    // ---------- Reset Timer ----------
    const resetTimer = useCallback(() => {
        setShowWarning(false);
        clearAllTimers();

        if (isLoggedIn) {
            inactivityTimeoutRef.current = setTimeout(
                startWarningCountdown,
                INACTIVITY_LIMIT - WARNING_DURATION
            );
        }
    }, [isLoggedIn, startWarningCountdown]);

    // ---------- Visibility Change ----------
    const handleVisibilityChange = useCallback(() => {
        if (document.hidden) {
            clearAllTimers();
            startWarningCountdown();
        } else {
            resetTimer();
        }
    }, [resetTimer, startWarningCountdown]);

    // ---------- Window Blur / Focus ----------
    // const handleWindowBlur = useCallback(() => {
    //     clearAllTimers();
    //     startWarningCountdown();
    // }, []);

    const handleWindowFocus = useCallback(() => {
        resetTimer();
    }, [resetTimer]);

    // ---------- Browser Close / Tab Close ----------
    const handleUnload = useCallback(() => {
        try {
            const token = localStorage.getItem("AccessToken");
            if (token) {
                navigator.sendBeacon(
                    "/logout",
                    JSON.stringify({ token })
                );
            }
        } catch {
            // Ignore – browser is closing
        }
    }, []);

    // ---------- Effect ----------
    useEffect(() => {
        if (!isLoggedIn) {
            clearAllTimers();
            setShowWarning(false);
            return;
        }

        const activityEvents = [
            "mousemove",
            "mousedown",
            "keydown",
            "touchstart",
            "scroll"
        ];

        activityEvents.forEach(event =>
            document.addEventListener(event, resetTimer, { passive: true })
        );

        document.addEventListener("visibilitychange", handleVisibilityChange);
        // window.addEventListener("blur", handleWindowBlur);
        window.addEventListener("focus", handleWindowFocus);
        window.addEventListener("beforeunload", handleUnload);

        resetTimer();

        return () => {
            activityEvents.forEach(event =>
                document.removeEventListener(event, resetTimer)
            );
            document.removeEventListener("visibilitychange", handleVisibilityChange);
            // window.removeEventListener("blur", handleWindowBlur);
            window.removeEventListener("focus", handleWindowFocus);
            window.removeEventListener("beforeunload", handleUnload);
            clearAllTimers();
        };
    }, [
        isLoggedIn,
        resetTimer,
        handleVisibilityChange,
        // handleWindowBlur,
        handleWindowFocus,
        handleUnload
    ]);

    return { showWarning, secondsLeft };
}
