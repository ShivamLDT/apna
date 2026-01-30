#app-->after_requesta and socketio default headers
from fClient import app


def post_process_context(context=None, data=None, *, is_socket=False):
    from flask import request #, current_app as app
    with app.app_context:
        print("request.remote_addr)")
    xserver = str(app.config.get("server_ip", ""))
    xcode = str(app.config.get("getCode", ""))
    # Socket.IO context — 'data' is a dictionary
    if isinstance(data, dict):
        data.update({
            "XRefServer" :request.remote_addr,
            "XServer": xserver,
            "XIDX": xcode
        })
    return data
    # if not is_socket:
    #     # Flask HTTP context
    #     response = data
    #     response.headers["XRefServer"] = request.remote_addr
    #     response.headers["XServer"] = xserver
    #     response.headers["XIDX"] = xcode

    #     if request.path.endswith("/restoretest"):
    #         try:
    #             json_data = response.get_json() or {}
    #         except Exception:
    #             json_data = {}

    #         headers = response.headers
    #         from sqlalchemy.orm import sessionmaker
    #         from runserver import engine
    #         session = sessionmaker(bind=engine)()

    #         try:
    #             restore_data = {
    #                 "RestoreLocation": headers.get("RestoreLocation"),
    #                 "backup_file_id": headers.get("id"),
    #                 "backup_id": headers.get("backup_id"),
    #                 "backup_pid": headers.get("backup_pid"),
    #                 "backup_name": headers.get("backup_name"),
    #                 "backup_name_id": headers.get("backup_name_id"),
    #                 "file": json_data.get("file", ""),
    #                 "reason": json_data.get("reason", ""),
    #                 "restore": json_data.get("restore", ""),
    #                 "file_restore_time": headers.get("file_restore_timetaken"),
    #                 "file_start": headers.get("file_start_time"),
    #                 "file_end": headers.get("file_start_end"),
    #                 "from_backup_pc": headers.get("frombackup_computer_name"),
    #                 "torestore_pc": headers.get("torestore_computer_name"),
    #                 "storage_type": headers.get("selectedStorageType"),
    #                 "t14": headers.get("t14"),
    #                 "targetlocation": headers.get("targetLocation"),
    #             }

    #             if restore_data["backup_id"]:
    #                 exists = session.query(restore_parent).filter_by(
    #                     RestoreLocation=restore_data["RestoreLocation"],
    #                     backup_id=restore_data["backup_pid"],
    #                     storage_type=restore_data["storage_type"],
    #                     backup_name=restore_data["backup_name"],
    #                     p_id=restore_data["backup_name_id"],
    #                     t14=restore_data["t14"],
    #                     from_backup_pc=restore_data["from_backup_pc"],
    #                     targetlocation=restore_data["targetlocation"],
    #                     torestore_pc=restore_data["torestore_pc"],
    #                 ).first()

    #                 if not exists:
    #                     session.add(restore_parent(
    #                         RestoreLocation=restore_data["RestoreLocation"],
    #                         backup_id=restore_data["backup_pid"],
    #                         storage_type=restore_data["storage_type"],
    #                         backup_name=restore_data["backup_name"],
    #                         p_id=restore_data["backup_name_id"],
    #                         t14=float(restore_data["t14"] or 0),
    #                         from_backup_pc=restore_data["from_backup_pc"],
    #                         targetlocation=restore_data["targetlocation"],
    #                         torestore_pc=restore_data["torestore_pc"],
    #                     ))
    #                     session.commit()

    #                 session.add(restore_child(
    #                     RestoreLocation=restore_data["RestoreLocation"],
    #                     backup_id=float(restore_data["backup_pid"]),
    #                     backup_file_id=float(restore_data["backup_file_id"]),
    #                     backup_name=restore_data["backup_name"],
    #                     p_id=restore_data["backup_name_id"],
    #                     file=restore_data["file"],
    #                     file_restore_time=0,
    #                     file_start=restore_data["file_start"],
    #                     file_end=restore_data["file_end"],
    #                     from_backup_pc=restore_data["from_backup_pc"],
    #                     reason=restore_data["reason"],
    #                     restore=restore_data["restore"],
    #                     storage_type=restore_data["storage_type"],
    #                     t14=float(restore_data["t14"] or 0),
    #                     targetlocation=restore_data["targetlocation"],
    #                     torestore_pc=restore_data["torestore_pc"],
    #                 ))
    #                 session.commit()

    #         finally:
    #             session.close()

    #     #return sanitize_response(response)
    #     return response

    # else:
    #     # Socket.IO context — `data` is a dictionary
    #     if isinstance(data, dict):
    #         data.update({
    #             "XRefServer" :request.remote_addr,
    #             "XServer": xserver,
    #             "XIDX": xcode
    #         })
    #     return data

