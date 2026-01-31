 seeing different “online/offline” logic between the Restore flow and the Endpoints page as refered to image1 and image2.

What’s happening in code
1) /refreshclientnodes doesn’t actually refresh anything

@app.route("/refreshclientnodes")
def refresh_client_nodes():
    sktio.emit("show_me", {"show_me": "s_starting"})
    return jsonify({"status": "success"}), 200
It only broadcasts a socket event. It does not update clientnodes_x or wait for clients to report back.

2) The “online” status used by /restore_nodes is just a stale timestamp

epoch_time = datetime.fromtimestamp(float(x['lastConnected']))
flag = (current_time - epoch_time).seconds > 120
endpoints.append({"lastConnected": str(flag)})
So if lastConnected hasn’t been updated recently, restore_nodes marks it offline.

3) The endpoints page (/clientnodes) uses a different live check /clientnodes calls:

is_less_than_2_minutes(ipAddress)
That function pings the agent (HTTP HEAD + socket fallback) and validates headers (XServer, XIDX).
So the Endpoints page can show Online even when lastConnected is stale.


to fix this I updated /restore_nodes to use the same live connectivity check as /clientnodes, so the Restore page now reflects the same online/offline logic as the Endpoints page.

What changed

FlaskWebProject3/FlaskWebProject3/views.py
restore_nodes() now uses:
flag = is_less_than_2_minutes(str(x["ipAddress"]))
instead of stale lastConnected timestamps.
Result

Restore page should now show the same Online/Offline status as the Endpoints page.