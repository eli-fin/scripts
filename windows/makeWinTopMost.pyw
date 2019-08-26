'''
When running this, press CRRL+F1 to keep the foreground windows on top at all times (press again to undo)
You'll also get an icon in the taskbar, which you can use to exit.
(set the ICON_PATH value)

Author: Eli Finkel - eyfinkel@gmail.com
'''

from ctypes import *
from ctypes import wintypes
import os

# WINAPI functions
GetLastError        = windll.kernel32.GetLastError
GetMessageA         = windll.user32.GetMessageA
MessageBoxA         = windll.user32.MessageBoxA
GetCursorPos        = windll.user32.GetCursorPos
CreatePopupMenu     = windll.user32.CreatePopupMenu
DestroyMenu         = windll.user32.DestroyMenu
InsertMenuA         = windll.user32.InsertMenuA
GetForegroundWindow = windll.user32.GetForegroundWindow
SetForegroundWindow = windll.user32.SetForegroundWindow
TrackPopupMenu      = windll.user32.TrackPopupMenu
GetWindowTextA      = windll.user32.GetWindowTextA
GetWindowLongA      = windll.user32.GetWindowLongA
SetWindowPos        = windll.user32.SetWindowPos
RegisterHotKey      = windll.user32.RegisterHotKey
UnregisterHotKey    = windll.user32.UnregisterHotKey
PostQuitMessage     = windll.user32.PostQuitMessage
LoadImageA          = windll.user32.LoadImageA
DestroyIcon         = windll.user32.DestroyIcon
Shell_NotifyIconA   = windll.Shell32.Shell_NotifyIconA
RegisterClassExA    = windll.user32.RegisterClassExA
CreateWindowExA     = windll.user32.CreateWindowExA
DispatchMessageA    = windll.user32.DispatchMessageA
DefWindowProcA      = windll.user32.DefWindowProcA
# It was needed to set argtypes for this, because
# args are c_int by default and larger pointers were being processed.
DefWindowProcA.argtypes = [
	wintypes.HWND,
	c_uint,
	wintypes.WPARAM,
	wintypes.LPARAM
]

# WINAPI defines
EXIT_FAILURE       = 1
TRUE               = 1
WM_APP             = 0x8000
WM_QUIT            = 0x12
WM_HOTKEY          = 0x0312
WM_RBUTTONDOWN     = 0x204
WM_CONTEXTMENU     = 0x7b
WM_COMMAND         = 0x111
MF_BYPOSITION      = 0x400
MF_STRING          = 0x0
TPM_BOTTOMALIGN    = 0x20
TPM_LEFTALIGN      = 0x0
MOD_CONTROL        = 0x0002
VK_F1              = 0x70
GWL_EXSTYLE        = (-20)
WS_EX_TOPMOST      = 0x0008
HWND_TOPMOST       = (-1)
HWND_NOTOPMOST     = (-2)
SWP_NOSIZE         = 0x0001
SWP_NOMOVE         = 0x0002
IMAGE_ICON         = 1
LR_LOADFROMFILE    = 0x10
NIF_ICON           = 0x2
NIF_TIP            = 0x4
NIF_INFO           = 0x10
NIF_MESSAGE        = 0x1
NIF_REALTIME       = 0x40
NOTIFYICON_VERSION = 3
NIIF_INFO          = 0x1
NIM_ADD            = 0x0
NIM_SETVERSION     = 0x4
NIM_MODIFY         = 0x1
NIM_DELETE         = 0x2
HWND_MESSAGE       = -3

# App defines

# // Notify icon callback message identifier
MY_APP_NOTIFY_ICON        = (WM_APP + 1)

# Menu items identifiers
MY_APP_CONTEXT_MENU_ABOUT = 0
MY_APP_CONTEXT_MENU_EXIT  = 1

# Other
TITLE_BUFFER_SIZE         = 100
ICON_PATH                 = b"icon.ico"

# This returns a ctypes struct to be used as a 'NOTIFYICONDATAA'
# (note the additional 'A' at the end)
# Followed is the struct used as a model (vs2017x64, defines removed)
# typedef struct {
#     DWORD cbSize;
#     HWND hWnd;
#     UINT uID;
#     UINT uFlags;
#     UINT uCallbackMessage;
#     HICON hIcon;
#     CHAR   szTip[128];
#     DWORD dwState;
#     DWORD dwStateMask;
#     CHAR   szInfo[256];
#     union {
#         UINT  uTimeout;
#         UINT  uVersion;
#     };
#     CHAR   szInfoTitle[64];
#     DWORD dwInfoFlags;
#     GUID guidItem;
#     HICON hBalloonIcon;
# } NOTIFYICONDATAA;
def NotifyIconStructCreator():
	# This sub class is one of the members of NOTIFYICONDATA
	# Copied from this:
	# typedef struct _GUID {
    # 	unsigned long  Data1;
    # 	unsigned short Data2;
    # 	unsigned short Data3;
    # 	unsigned char  Data4[ 8 ];
	# } GUID;
	class _GUID(Structure):
		_fields_ = [
			('Data1', c_ulong),
			('Data2', c_ushort),
			('Data3', c_ushort),
			('Data4', c_ubyte * 8)
		]

	class _tmp_union(Union):
		_fields_ = [
			('uTimeout', wintypes.UINT),
			('uVersion', wintypes.UINT)
		]
	
	class _NOTIFYICONDATA(Structure):
		_fields_ = [
			('cbSize', wintypes.DWORD),
			('hWnd', wintypes.HWND),
			('uID', wintypes.UINT),
			('uFlags', wintypes.UINT),
			('uCallbackMessage', wintypes.UINT),
			('hIcon', wintypes.HICON),
			('szTip', wintypes.CHAR * 128),
			('dwState', wintypes.DWORD),
			('dwStateMask', wintypes.DWORD),
			('szInfo', wintypes.CHAR * 256),
			('union', _tmp_union),
			('szInfoTitle', wintypes.CHAR * 64),
			('dwInfoFlags', wintypes.DWORD),
			('guidItem', _GUID),
			('hBalloonIcon', wintypes.HICON)
		]
	
	return _NOTIFYICONDATA()

# The WndProc type on vs2017x64
_WNDPROCTYPE = CFUNCTYPE(c_longlong, wintypes.HANDLE, c_uint, wintypes.WPARAM, wintypes.LPARAM)

# This returns a ctypes struct to be used as a 'WNDCLASSEXA'
# (note the additional 'A' at the end)
# Followed is the struct used as a model (vs2017x64, defines removed)
# typedef struct {
#     UINT        cbSize;
#     UINT        style;
#     WNDPROC     lpfnWndProc;
#     int         cbClsExtra;
#     int         cbWndExtra;
#     HINSTANCE   hInstance;
#     HICON       hIcon;
#     HCURSOR     hCursor;
#     HBRUSH      hbrBackground;
#     LPCSTR      lpszMenuName;
#     LPCSTR      lpszClassName;
#     HICON       hIconSm;
# } WNDCLASSEXA
def WndClassStructCreator():
	class _WNDCLASSEXA(Structure):
		_fields_ = [
			("cbSize", wintypes.UINT),
			("style", wintypes.UINT),
			("lpfnWndProc", _WNDPROCTYPE),
			("cbClsExtra", c_int),
			("cbWndExtra", c_int),
			("hInstance", wintypes.HINSTANCE),
			("hIcon", wintypes.HICON),
			("hCursor", wintypes.HICON),
			("hbrBackground", wintypes.HBRUSH),
			("lpszMenuName", wintypes.LPCSTR),
			("lpszClassName", wintypes.LPCSTR),
			("hIconSm", wintypes.HICON)
		]
	
	return _WNDCLASSEXA()

# Global vars
g_retcode    = None
g_MainhWnd   = None
g_niData     = NotifyIconStructCreator()
g_appIcon    = None
g_hPopupMenu = None

# This function expects a retcode and function name
# If retcode zero, a messagebox with GetLastError() value and funcName will be shown and exit(EXIT_FAILURE) will be called
def WINAPI_RETCODE_CHECK(ret, funcName):
	if ret == 0:
		err = GetLastError()
		msg = b"WINAPI Error: func:" + funcName + b", error:" + str(err).encode('ascii')
		MessageBoxA(None, msg, b"Error", None)
		exit(EXIT_FAILURE)

# Show the notifyicon context menu
# Expects the handle to which messages will be posted
def ShowContextMenu(hWnd):
	global g_retcode, g_hPopupMenu
	
	# Return if a menu is currently present
	if (g_hPopupMenu != None):
		return;

	# Create menu and add items
	g_hPopupMenu = CreatePopupMenu()
	WINAPI_RETCODE_CHECK(g_hPopupMenu, b"CreatePopupMenu")
	g_retcode = InsertMenuA(g_hPopupMenu, 0, MF_BYPOSITION | MF_STRING, MY_APP_CONTEXT_MENU_ABOUT, b"About")
	WINAPI_RETCODE_CHECK(g_retcode, b"InsertMenuA")
	g_retcode = InsertMenuA(g_hPopupMenu, 1, MF_BYPOSITION | MF_STRING, MY_APP_CONTEXT_MENU_EXIT, b"Exit")
	WINAPI_RETCODE_CHECK(g_retcode, b"InsertMenuA")

	# Get cursor position to display menu there
	p = wintypes.POINT()
	g_retcode = windll.user32.GetCursorPos(byref(p))
	WINAPI_RETCODE_CHECK(g_retcode, b"GetCursorPos")
	
	# Show menu
	g_retcode = SetForegroundWindow(hWnd)
	WINAPI_RETCODE_CHECK(g_retcode, b"SetForegroundWindow")
	g_retcode = TrackPopupMenu(g_hPopupMenu, TPM_BOTTOMALIGN | TPM_LEFTALIGN, p.x, p.y, 0, hWnd, None)
	WINAPI_RETCODE_CHECK(g_retcode, b"TrackPopupMenu")
	
	# Destroy menu
	g_retcode = DestroyMenu(g_hPopupMenu)
	WINAPI_RETCODE_CHECK(g_retcode, b"DestroyMenu")
	g_hPopupMenu = None

# This function will be called when the hotkey is pressed
# It will handle setting or unsetting a window topmost
def HandleWindowTopMostState():
	global g_retcode, g_niData
	
	# Get current active window
	currWin = GetForegroundWindow()

	# Get window title
	winTitle = (c_char*TITLE_BUFFER_SIZE)()
	GetWindowTextA(currWin, byref(winTitle), TITLE_BUFFER_SIZE)

	# If currently not top most
	if (GetWindowLongA(currWin, GWL_EXSTYLE) & WS_EX_TOPMOST) == 0:
		# Set as topmost
		SetWindowPos(currWin, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

		# Set baloon tip info
		g_niData.szInfo = b"'" + winTitle.value + b"'\nmade topmost"

		# If currently top most
	else:
		# Set as not top most
		SetWindowPos(currWin, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

		# Set baloon tip info
		g_niData.szInfo = b"'" + winTitle.value + b"'\nmade not topmost"
	
	# Show baloon tip
	g_retcode = Shell_NotifyIconA(NIM_MODIFY, byref(g_niData))
	WINAPI_RETCODE_CHECK(g_retcode, b"Shell_NotifyIconA_MODIFY")


# Register to get messages when ctrl+f1 is pressed
def RegisterAppHotKey():
	global g_retcode, g_MainhWnd
	
	g_retcode = RegisterHotKey(g_MainhWnd, 0, MOD_CONTROL, VK_F1)
	WINAPI_RETCODE_CHECK(g_retcode, b"RegisterHotKey")

def UnregisterAppHotKey():
	global g_retcode, g_MainhWnd
	
	g_retcode = UnregisterHotKey(g_MainhWnd, 0)
	WINAPI_RETCODE_CHECK(g_retcode, b"UnregisterHotKey")

# Handle messages
def WndProc(hWnd, uMsg, wParam, lParam):
	# Switch message type
	
	# Hotkey message
	if uMsg == WM_HOTKEY:
		HandleWindowTopMostState()

	# Notifyicon message
	elif uMsg == MY_APP_NOTIFY_ICON:
		# Both messages will open context menu
		if (lParam == WM_RBUTTONDOWN) or (lParam == WM_CONTEXTMENU):
			ShowContextMenu(hWnd)

		else:
			return DefWindowProcA(hWnd, uMsg, wParam, lParam)

	# Context menu messages
	elif uMsg == WM_COMMAND:
		if (wParam & 0xffff) == MY_APP_CONTEXT_MENU_ABOUT:
			MessageBoxA(None, b"About", b"TopMoster", None)

		elif (wParam & 0xffff) == MY_APP_CONTEXT_MENU_EXIT:
			PostQuitMessage(0)

	else:
		return DefWindowProcA(hWnd, uMsg, wParam, lParam)

	# Message handled
	return TRUE

def CreateNotifyIcon():
	global g_retcode, g_MainhWnd, g_appIcon, g_niData
	
	# Get icon
	g_appIcon = LoadImageA(None, ICON_PATH, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
	WINAPI_RETCODE_CHECK(g_appIcon, b"LoadImageA")

	# Populate ni fields
	g_niData.cbSize = sizeof(g_niData)
	g_niData.hWnd = g_MainhWnd
	g_niData.uID = 1
	g_niData.uFlags = NIF_ICON | NIF_TIP | NIF_INFO | NIF_MESSAGE | NIF_REALTIME
	g_niData.uCallbackMessage = MY_APP_NOTIFY_ICON
	g_niData.hIcon = g_appIcon
	g_niData.szTip = b"CTRL+F1 start/stop"
	g_niData.szInfo = b"Program started"
	g_niData.uVersion = NOTIFYICON_VERSION;
	g_niData.szInfoTitle = b"Topmost setter"
	g_niData.dwInfoFlags = NIIF_INFO;

	# Add field to tray
	g_retcode = Shell_NotifyIconA(NIM_ADD, byref(g_niData))
	WINAPI_RETCODE_CHECK(g_retcode, b"Shell_NotifyIconA_ADD")
	g_retcode = Shell_NotifyIconA(NIM_SETVERSION, byref(g_niData))
	WINAPI_RETCODE_CHECK(g_retcode, b"Shell_NotifyIconA_SET_VER")

def DeleteNotifyIcon():
	global g_retcode, g_appIcon, g_niData
	
	# Delete field and destroy icon
	g_retcode = Shell_NotifyIconA(NIM_DELETE, byref(g_niData))
	WINAPI_RETCODE_CHECK(g_retcode, b"Shell_NotifyIconA_DELETE")
	g_retcode = DestroyIcon(g_appIcon)
	WINAPI_RETCODE_CHECK(g_retcode, b"DestroyIcon")

def Main():
	global g_retcode, g_MainhWnd
	
	# Define window class
	wcex = WndClassStructCreator()
	wcex.cbSize = sizeof(wcex)
	wcex.lpfnWndProc = _WNDPROCTYPE(WndProc)
	wcex.lpszClassName = b"dummy_name"
	
	# Register window class
	wndClass = RegisterClassExA(byref(wcex))
	WINAPI_RETCODE_CHECK(wndClass, b"RegisterClassExA")
	
	# Create a message only window
	g_MainhWnd = CreateWindowExA(None, wcex.lpszClassName, None, None, None, None, None, None, HWND_MESSAGE, None, None, None)
	WINAPI_RETCODE_CHECK(g_MainhWnd, b"CreateWindowExA")

	# Icon and hotkey
	CreateNotifyIcon()
	RegisterAppHotKey()

	# Main message loop:  
	msg = wintypes.MSG()
	while TRUE:
		g_retcode = GetMessageA(pointer(msg), g_MainhWnd, 0, 0)
		if g_retcode > 0:
			if msg.message == WM_QUIT:
				break
			DispatchMessageA(byref(msg))
		elif g_retcode < 0:
			MessageBoxA(None, b"ERROR", b"Error in message loop", 0)
		else:
			break
	
	# Cleanup
	UnregisterAppHotKey()
	DeleteNotifyIcon()

	return msg.wParam

if __name__ == '__main__':
	Main()
