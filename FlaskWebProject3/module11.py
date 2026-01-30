# import win32api
# import win32con
# import win32process
# import win32file
# import win32pipe
# import win32console
# import pywintypes


# def find_process_id(name):
#     """Find the PID of a process by name."""
#     for proc in win32process.EnumProcesses():
#         try:
#             h_process = win32api.OpenProcess(
#                 win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
#                 False,
#                 proc,
#             )
#             exe = win32process.GetModuleFileNameEx(h_process, 0)
#             if name.lower() in exe.lower():
#                 return proc
#         except pywintypes.error:
#             pass
#     return None


# def read_from_pipe(pipe):
#     """Read data from a named pipe."""
#     while True:
#         try:
#             data = win32file.ReadFile(pipe, 4096)
#             if data:
#                 print(data[1].decode("utf-8"), end="")
#         except pywintypes.error as e:
#             if e.winerror == 109:  # ERROR_BROKEN_PIPE
#                 break
#             else:
#                 raise


# def attach_to_console(pid):
#     """Attach to the console of an existing process and read its output."""
#     # Create a named pipe
#     pipe_name = r"\\.\pipe\console_output"
#     pipe = win32pipe.CreateNamedPipe(
#         pipe_name,
#         win32pipe.PIPE_ACCESS_DUPLEX,
#         win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
#         1,
#         65536,
#         65536,
#         0,
#         None,
#     )

#     # Attach to the console
#     try:
#         win32console.AttachConsole(pid)
#         h = win32file.CreateFile(
#             pipe_name,
#             win32file.GENERIC_WRITE | win32file.GENERIC_READ,
#             0,
#             None,
#             win32file.OPEN_EXISTING,
#             0,
#             None,
#         )
#         win32pipe.ConnectNamedPipe(pipe, None)
#         read_from_pipe(pipe)
#     except pywintypes.error as e:
#         print(f"Failed to attach to console: {e}")
#     finally:
#         win32console.FreeConsole()
#         win32pipe.DisconnectNamedPipe(pipe)
#         win32file.CloseHandle(pipe)


# if __name__ == "__main__":
#     process_name = "winword.exe"  # Replace with your process name
#     pid = find_process_id(process_name)
#     if pid:
#         print(f"Found PID: {pid}")
#         attach_to_console(pid)
#     else:
#         print(f"Process '{process_name}' not found.")
