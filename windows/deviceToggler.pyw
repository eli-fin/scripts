'''
Shows a notification icon, which when clicked twice, will toggle (enbable/disable)
the state of the device device_name, which is the name of the device as shown
in the windows device manager (this will not work well if the name isn't unique)
Enabling and disabling devices this way requires administrative rights.
To exit, double right click

Author: Eli Finkel - eyfinkel@gmail.com
'''

def main():
    from winapi_lib.device_manager import DeviceManager
    from winapi_lib.message_window import MessageWindow
    from winapi_lib.notify_icon import NotifyIcon
    from ctypes import windll
    from time import sleep
    import os
    
    def assert_admin():
        import sys
        if windll.shell32.IsUserAnAdmin() == 0:
            args = ' '.join([f'"{arg}"' for arg in sys.argv])
            windll.shell32.ShellExecuteW(0, "runas", sys.executable, args, 0, 0, 0)
            sys.exit()
    assert_admin()
    
    my_app_message_id = 0x8000+1 # WM_APP+1
    my_icon_path_on = os.path.dirname(os.path.realpath(__file__)) + '/_icons/touchscreen-on.ico' # Relative to script dir
    my_icon_path_off = os.path.dirname(os.path.realpath(__file__)) + '/_icons/touchscreen-off.ico' # Relative to script dir
    my_icon_title = 'My device toggler'
    device_name = 'HID-compliant touch screen'
    my_icon_tip = f'Device toggler for "{device_name}"\n(double click to toggle,\n double rclick to exit)'
    
    def WndProc(hWnd, uMsg, wParam, lParam):
        nonlocal is_enabled
        
        try:
            if uMsg == my_app_message_id:
                if  lParam == 0x203: # WM_LBUTTONDBLCLK
                    if is_enabled:
                        manager.disable_device(device)
                        icon.popup('Disabling', my_icon_title)
                        icon.update_icon(my_icon_path_off)
                    else:
                        manager.enable_device(device)
                        icon.popup('Enabling', my_icon_title)
                        icon.update_icon(my_icon_path_on)
                    is_enabled = not is_enabled
                
                elif lParam == 0x206: # WM_RBUTTONDBLCLK
                    sleep(0.2) # Sleep for a little, so the double click ends before the icon is deleted
                               # (otherwise the second right mouse up will cause the taskbar context menu to show)
                    icon.popup('Exiting...', my_icon_title)
                    windll.user32.PostQuitMessage(0)
                
                return 1 # Handled
        except:
            windll.user32.PostQuitMessage(1)
            raise
                
        return windll.user32.DefWindowProcW(hWnd, uMsg, wParam, lParam)
    
    manager=DeviceManager()
    try:
        device = (d for d in manager.enumerate() if device_name == manager.get_device_name(d)).__next__()
    except StopIteration:
        raise Exception(f'Can\'t find device "{device_name}"')
    is_enabled = manager.get_device_status(device)
    window=MessageWindow(WndProc)
    icon=NotifyIcon(my_icon_path_on if is_enabled else my_icon_path_off, window.hWnd, 0, my_app_message_id, my_icon_tip, 'Starting', my_icon_title)
    
    window.loop()
    
    del manager
    del window
    del icon

if __name__ == '__main__':
    main()
    