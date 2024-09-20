import os
import base64
import subprocess
import shutil
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
import tkinter.ttk as ttk

# Global variables for the entry fields
app_name_entry = None
executable_name_entry = None
command_entry = None

# Set the theme name
theme_name = "aquativo"

def set_icon(window, icon_path):
    """Set the icon for a given Tkinter window."""
    if icon_path and os.path.isfile(icon_path):
        try:
            # For .ico files, use the file directly
            window.iconbitmap(icon_path)  # This works for ICO files
            return True
        except Exception as e:
            print(f"Error loading icon: {e}")
            return False
    else:
        print(f"Icon path is not valid: {icon_path}")
        return False

def show_splash_screen(theme_name="arc", icon_path=None):
    """Show a splash screen while the app is loading."""
    splash = ThemedTk(theme=theme_name)
    splash.title("Loading... Infinite Remote")
    splash.geometry("300x200")

    # Center splash screen
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (300 // 2)
    y = (screen_height // 2) - (200 // 2)
    splash.geometry(f"300x200+{x}+{y}")

    # Load icon for splash screen
    if not set_icon(splash, icon_path):
        print("Failed to set icon on splash screen.")

    label = ttk.Label(splash, text="Welcome to Infinite Remote", font=('Helvetica', 12))
    label.pack(expand=True)

    progress_bar = ttk.Progressbar(splash, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
    progress_bar.pack(pady=20)

    style = ttk.Style()
    style.theme_use(theme_name)
    style.configure("TProgressbar", troughcolor='gray', background='navy')

    # Start the progress bar
    progress_bar.start()
    splash.after(3000, lambda: (progress_bar.stop(), splash.destroy()))
    splash.protocol("WM_DELETE_WINDOW", splash.withdraw)
    splash.lift()
    return splash

def setup_window(root, icon_path):
    """Set up the main window with the specified icon."""
    if not set_icon(root, icon_path):
        print("Failed to set icon on main window.")

def select_file(title, filetypes):
    """Open a file dialog to select a file."""
    tk.Tk().withdraw()  # Prevents the root window from appearing
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return file_path

def select_directory(title):
    """Open a directory dialog to select a folder."""
    tk.Tk().withdraw()  # Prevents the root window from appearing
    folder_path = filedialog.askdirectory(title=title)
    return folder_path

def read_file(file_path):
    """Read a file and return its content as a list of lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"{file_path} file not found.")
        return None

def write_file(file_path, content):
    """Write a list of lines to a file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(content)

def update_generate_py(file_path, new_executable_name):
    """Update the generate.py file with the new executable name."""
    print(f"Updating {file_path} with the new executable name: {new_executable_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "executable_name" in line:
                lines[i] = f"executable_name = '{new_executable_name}'\n"
                break
        write_file(file_path, lines)

def convert_to_base64(image_path):
    """Convert an image file to a Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def update_build_py(file_path, new_app_name):
    """Update the build.py file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "app_name" in line:
                lines[i] = f"app_name = '{new_app_name}'\n"
                break
        write_file(file_path, lines)

def update_cargo_toml(file_path, new_app_name):
    """Update the Cargo.toml file to set name, default-run and modify features."""
    try:
        content = read_file(file_path)
        if content is None:
            return

        updated_content = []
        in_package_section = False
        in_metadata_section = False
        in_features_section = False
        
        for line in content:
            stripped_line = line.strip()
            if stripped_line == '[package]':
                in_package_section = True
            elif in_package_section and stripped_line.startswith('['):
                in_package_section = False
            
            # Update 'name' and 'default-run'
            if in_package_section:
                if stripped_line.startswith('name ='):
                    line = f'name = "{new_app_name}"\n'
                elif stripped_line.startswith('default-run ='):
                    line = f'default-run = "{new_app_name}"\n'

            # Update [package.metadata.winres]
            if stripped_line == '[package.metadata.winres]':
                in_metadata_section = True
            if in_metadata_section:
                if stripped_line.startswith('ProductName ='):
                    line = f'ProductName = "{new_app_name}"\n'
                elif stripped_line.startswith('OriginalFilename ='):
                    line = f'OriginalFilename = "{new_app_name.lower()}.exe"\n'

            # Update [features]
            if stripped_line == '[features]':
                in_features_section = True
            if in_features_section:
                if stripped_line.startswith('default ='):
                    line = 'default = ["use_dasp", "inline"]\n'
            elif in_features_section and stripped_line.startswith('['):
                in_features_section = False

            updated_content.append(line)

        write_file(file_path, updated_content)
        print("Updated Cargo.toml content:")
        print(''.join(updated_content))
    except FileNotFoundError:
        print("Cargo.toml file not found in the selected directory.")
    except Exception as e:
        print(f"An error occurred while updating Cargo.toml: {e}")

def update_native_model(file_path, new_app_name):
    """Update the native_model.dart file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "class NativeModel" in line:
                lines[i + 1] = f"  final String appName = '{new_app_name}';\n"
                break
        write_file(file_path, lines)

def update_platform_model(file_path, new_app_name):
    """Update the platform_model.dart file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "class PlatformModel" in line:
                lines[i + 1] = f"  final String appName = '{new_app_name}';\n"
                break
        write_file(file_path, lines)

def update_web_model(file_path, new_app_name):
    """Update the web_model.dart file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "class WebModel" in line:
                lines[i + 1] = f"  final String appName = '{new_app_name}';\n"
                break
        write_file(file_path, lines)

def update_bridge_file(file_path, new_app_name):
    """Update the bridge.dart file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "class Bridge" in line:
                lines[i + 1] = f"  final String appName = '{new_app_name}';\n"
                break
        write_file(file_path, lines)

def update_cmakelists(file_path, new_app_name):
    """Update the CMakeLists.txt file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "set(PROJECT_NAME" in line:
                lines[i] = f"set(PROJECT_NAME \"{new_app_name}\")\n"
                break
        write_file(file_path, lines)

def update_main_cpp(file_path, new_app_name):
    """Update the main.cpp file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "setAppName" in line:
                lines[i] = f"    setAppName(\"{new_app_name}\");\n"
                break
        write_file(file_path, lines)

def update_runner_rc(file_path, new_app_name):
    """Update the Runner.rc file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "FileVersion" in line:
                lines[i] = f"FileVersion 1.0.0.0\n"
                lines[i + 1] = f"ProductVersion 1.0.0.0\n"
                lines[i + 2] = f"ProductName \"{new_app_name}\"\n"
                break
        write_file(file_path, lines)

def update_portable_cargo_toml(file_path, new_app_name):
    """Update the Cargo.toml file in libs/portable to set the ProductName and OriginalFilename."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            content = file.readlines()

        print("Original libs/portable/Cargo.toml content:")
        print(''.join(content))

        updated_content = []
        in_winres_section = False

        for line in content:
            stripped_line = line.strip()

            if stripped_line == '[package.metadata.winres]':
                in_winres_section = True
                updated_content.append(line)
                continue
            
            elif in_winres_section and stripped_line.startswith('['):
                in_winres_section = False  

            if in_winres_section:
                if stripped_line.startswith('ProductName ='):
                    line = f'ProductName = "{new_app_name}"\n'
                elif stripped_line.startswith('OriginalFilename ='):
                    line = f'OriginalFilename = "{new_app_name.lower()}.exe"\n'

            updated_content.append(line)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(updated_content)

        print("Updated libs/portable/Cargo.toml content:")
        print(''.join(updated_content))

    except FileNotFoundError:
        print("libs/portable/Cargo.toml file not found in the selected directory.")
    except Exception as e:
        print(f"An error occurred while updating libs/portable/Cargo.toml: {e}")

def update_config_rs(file_path, new_app_name):
    """Update the config.rs file with the new application name."""
    try:
        lines = read_file(file_path)
        if lines is None:
            return

        for i in range(len(lines)):
            if "pub static ref APP_NAME: RwLock<String> = RwLock::new(" in lines[i]:
                lines[i] = f'pub static ref APP_NAME: RwLock<String> = RwLock::new("{new_app_name}".to_owned());\n'
        
        write_file(file_path, lines)
        print(f"Changed APP_NAME to '{new_app_name}'")
    
    except Exception as e:
        print(f"An error occurred: {e}")

def update_rust_file(file_path, new_app_name):
    """Update the main.rs file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "let app_name" in line:
                lines[i] = f"let app_name = \"{new_app_name}\";\n"
                break
        write_file(file_path, lines)

def update_rustdesk_desktop_file(file_path, new_app_name):
    """Update the rustdesk.desktop file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "Name=" in line:
                lines[i] = f"Name={new_app_name}\n"
                break
        write_file(file_path, lines)

def update_rustdesk_service(file_path, new_app_name):
    """Update the rustdesk.service file with the new application name."""
    print(f"Updating {file_path} with the new application name: {new_app_name}")
    lines = read_file(file_path)
    if lines is not None:
        for i, line in enumerate(lines):
            if "Description=" in line:
                lines[i] = f"Description={new_app_name} Service\n"
                break
        write_file(file_path, lines)

def update_ui_file_with_icon(base_directory, icon_base64):
    """Update the ui.rs file with the new Base64 encoded icon."""
    ui_path = os.path.join(base_directory, "src", "ui.rs")
    if not os.path.isfile(ui_path):
        print("ui.rs file not found. Exiting.")
        return

    with open(ui_path, "r", encoding="utf-8") as file:
        ui_content = file.readlines()

    line_indices_to_replace = [788, 792]  # Lines 789 and 793

    for index in line_indices_to_replace:
        if 0 <= index < len(ui_content):
            old_line = ui_content[index].strip()
            print(f"Updating line {index + 1}: {old_line}")
            new_line = f'        "data:image/png;base64,{icon_base64}".into()\n'
            ui_content[index] = new_line

    with open(ui_path, "w", encoding="utf-8") as file:
        file.writelines(ui_content)

    print("Updated Base64 strings in ui.rs successfully!")

def browse_directory():
    """Open a dialog to browse directories and handle the updates."""
    root.withdraw()  # Hide the main Tkinter window

    base_directory = select_directory("Select your RustDesk source directory.")
    if not base_directory:
        print("No directory selected. Exiting.")
        root.deiconify()
        return

    icon_file = select_file("Select the Icon PNG Image", [("Image Files", "*.png")])
    if not icon_file or not os.path.isfile(icon_file):
        print("No icon image selected. Exiting.")
        root.deiconify()
        return
    new_icon_base64 = convert_to_base64(icon_file)

    # Copy the selected icon to the RustDesk res directory as icon.ico and tray-icon
    res_dir = os.path.join(base_directory, 'res')

    try:
        # Ensure the res directory exists
        if not os.path.exists(res_dir):
            print(f"The resource directory '{res_dir}' does not exist.")
            return

        # Convert PNG to ICO and save as icon.ico
        icon_destination_path = os.path.join(res_dir, 'icon.ico')
        with Image.open(icon_file) as img:
            img.save(icon_destination_path, format='ICO')  # Save as ICO format
        print(f"Converted and saved icon to '{icon_destination_path}'")

        # Copy the icon.ico to create tray-icon
        tray_icon_destination_path = os.path.join(res_dir, 'tray-icon.ico')
        shutil.copy2(icon_destination_path, tray_icon_destination_path)
        print(f"Copied icon to '{tray_icon_destination_path}'")

    except Exception as e:
        print(f"An error occurred while processing the icon: {e}")

    new_app_name = app_name_entry.get().strip()
    executable_name = executable_name_entry.get().strip()
    command_to_run = command_entry.get().strip()

    if not new_app_name:
        messagebox.showwarning("Input Error", "Please enter a new application name.")
        root.deiconify()
        return

    if not executable_name:
        messagebox.showwarning("Input Error", "Please enter an executable name.")
        root.deiconify()
        return

    try:
        # Update the ui.rs with the new icon
        update_ui_file_with_icon(base_directory, new_icon_base64)

        # Call other update functions
        update_build_py(os.path.join(base_directory, 'build.py'), new_app_name)
        update_cargo_toml(os.path.join(base_directory, 'Cargo.toml'), new_app_name)
        update_native_model(os.path.join(base_directory, 'flutter', 'lib', 'models', 'native_model.dart'), new_app_name)
        update_platform_model(os.path.join(base_directory, 'flutter', 'lib', 'models', 'platform_model.dart'), new_app_name)
        update_web_model(os.path.join(base_directory, 'flutter', 'lib', 'models', 'web_model.dart'), new_app_name)
        update_bridge_file(os.path.join(base_directory, 'flutter', 'lib', 'web', 'bridge.dart'), new_app_name)
        update_cmakelists(os.path.join(base_directory, 'flutter', 'windows', 'CMakeLists.txt'), new_app_name)
        update_main_cpp(os.path.join(base_directory, 'flutter', 'windows', 'runner', 'main.cpp'), new_app_name)
        update_runner_rc(os.path.join(base_directory, 'flutter', 'windows', 'runner', 'Runner.rc'), new_app_name)
        update_portable_cargo_toml(os.path.join(base_directory, 'libs', 'portable', 'Cargo.toml'), new_app_name)
        update_config_rs(os.path.join(base_directory, 'libs', 'hbb_common', 'src', 'config.rs'), new_app_name)
        rust_file_path = os.path.join(base_directory, 'libs', 'portable', 'src', 'main.rs')
        update_rust_file(rust_file_path, new_app_name)
        update_rustdesk_desktop_file(os.path.join(base_directory, 'res', 'rustdesk.desktop'), new_app_name)
        update_rustdesk_service(os.path.join(base_directory, 'res', 'rustdesk.service'), new_app_name)

        if executable_name:
            generate_py_path = os.path.join(base_directory, 'libs', 'portable', 'generate.py')
            update_generate_py(generate_py_path, executable_name)

        # Execute the inline-sciter.py script after updating files
        inline_sciter_path = os.path.join(base_directory, 'res', 'inline-sciter.py')
        
        try:
            subprocess.run(["python", inline_sciter_path], cwd=base_directory, check=True)
            print("Successfully executed inline-sciter.py")
        except FileNotFoundError:
            print(f"The file '{inline_sciter_path}' was not found. Please check the file path.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing inline-sciter.py: {e}")

        if command_to_run:
            try:
                print(f"Running command: '{command_to_run}' in directory: {base_directory}")
                subprocess.run(command_to_run, shell=True, cwd=base_directory, check=True)
                print(f"Command '{command_to_run}' executed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error in executing command: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        root.deiconify()  # Show the root window again

def on_closing():
    """Handle the closing event of the application."""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()  # Exit the main loop
        root.destroy()  # Destroy the root window

# Main application setup
icon_path = r"C:\Users\VenimK\Downloads\Wrench.ico"
if os.path.isfile(icon_path):
    splash = show_splash_screen(theme_name=theme_name, icon_path=icon_path)
else:
    print(f"Icon file does not exist at: {icon_path}")

# Create and set up the main window
root = ThemedTk()
root.title("Infinite Remote")
root.geometry("600x400")
root.set_theme(theme_name)

# Make sure to set the icon for the main window here
if not set_icon(root, icon_path):
    print("Failed to set icon on main window.")

# Create a frame for organization
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(main_frame, text="Select the RustDesk directory:")
label.pack(pady=10)

browse_button = ttk.Button(main_frame, text="Browse...", command=browse_directory)
browse_button.pack(pady=5)

app_name_label = ttk.Label(main_frame, text="Enter new application name:")
app_name_label.pack(pady=5)

app_name_entry = ttk.Entry(main_frame)
app_name_entry.pack(pady=5)

executable_name_label = ttk.Label(main_frame, text="Enter new executable name (without .exe):")
executable_name_label.pack(pady=5)

executable_name_entry = ttk.Entry(main_frame)
executable_name_entry.pack(pady=5)

command_label = ttk.Label(main_frame, text="Enter command to run after updates (or leave blank):")
command_label.pack(pady=5)

command_entry = ttk.Entry(main_frame)
command_entry.pack(pady=5)

# Quit Button
quit_button = ttk.Button(main_frame, text="Quit", command=root.quit)
quit_button.pack(pady=10)

# Configure the closing event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI loop
root.mainloop()

# Only necessary for debugging
print(root.get_themes())  # This will list all available themes
