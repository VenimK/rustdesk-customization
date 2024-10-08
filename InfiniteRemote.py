import subprocess
import sys
import os
import base64
import shutil
import requests
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
import tkinter.ttk as ttk

# List of required packages
required_packages = [
    'requests',
    'Pillow',  # For PIL (Pillow must be installed for Image module)
    'ttkthemes'  # Ensure ttkthemes is installed
]

def install(package):
    """Function to install package using pip."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Check for required packages
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"{package} is not installed. Installing...")
        install(package)
    else:
        print(f"{package} is already installed.")

# Global variables for the entry fields
app_name_entry = None
executable_name_entry = None
command_entry = None
description_entry = None  # Variable for the description entry
pub_key_entry = None  # Variable for the public key entry
rendezvous_server_entry = None  # Variable for the custom ID server entry

# Set the theme name
theme_name = "aquativo"

def download_icon(icon_url, icon_path):
    """Download an icon from a URL and save it to a local path."""
    try:
        response = requests.get(icon_url)
        response.raise_for_status()  # Raise an error for bad responses
        with open(icon_path, 'wb') as f:
            f.write(response.content)
        print(f"Icon downloaded successfully: {icon_path}")
        return True
    except Exception as e:
        print(f"Error downloading icon: {e}")
        return False

def download_file(url, destination):
    """Download a file from a URL and save it to a local path."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(destination, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded successfully: {destination}")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def download_sciter_dll(destination):
    """Download sciter.dll from the given URL."""
    url = "https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.win/x64/sciter.dll"
    return download_file(url, destination)

def set_icon(window, icon_path):
    """Set the icon for a given Tkinter window."""
    if icon_path and os.path.isfile(icon_path):
        try:
            window.iconbitmap(icon_path)
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

def convert_to_base64(image_path):
    """Convert an image file to a Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def update_cargo_toml_description(file_path, new_description):
    """Update the Cargo.toml file to set the package description and FileDescription."""
    try:
        content = read_file(file_path)
        if content is None:
            return

        updated_content = []
        in_package_section = False
        in_metadata_section = False
        
        for line in content:
            stripped_line = line.strip()
            if stripped_line == '[package]':
                in_package_section = True
                in_metadata_section = False  # Reset this for the next section
            elif stripped_line == '[package.metadata.winres]':
                in_metadata_section = True
            
            # Update description in the package section
            if in_package_section and stripped_line.startswith('description ='):
                line = f'description = "{new_description}"\n'
                
            # Update FileDescription in the metadata section
            if in_metadata_section and stripped_line.startswith('FileDescription ='):
                line = f'FileDescription = "{new_description}"\n'

            updated_content.append(line)

        write_file(file_path, updated_content)
        print("Updated Cargo.toml with new description and FileDescription:")
        print(''.join(updated_content))
    except FileNotFoundError:
        print("Cargo.toml file not found in the selected directory.")
    except Exception as e:
        print(f"An error occurred while updating Cargo.toml: {e}")

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
            # Update FileVersion, ProductVersion, ProductName, InternalName, and OriginalFilename
            if "FileVersion" in line:
                lines[i] = f"            VALUE \"FileVersion\", \"1.0.0.0\" \"\\0\"\n"
            elif "ProductVersion" in line:
                lines[i] = f"            VALUE \"ProductVersion\", \"1.0.0.0\" \"\\0\"\n"
            elif "ProductName" in line:
                lines[i] = f"            VALUE \"ProductName\", \"{new_app_name}\" \"\\0\"\n"
            elif "InternalName" in line:
                lines[i] = f"            VALUE \"InternalName\", \"{new_app_name.lower()}\" \"\\0\"\n"
            elif "OriginalFilename" in line:
                lines[i] = f"            VALUE \"OriginalFilename\", \"{new_app_name.lower()}.exe\" \"\\0\"\n"

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

def update_client_file(base_directory):
    """Comment out the TCP connection security section in src/client.rs."""
    file_path = os.path.join(base_directory, 'src', 'client.rs')
    print(f"Updating {file_path} to comment out TCP connection security section.")

    lines = read_file(file_path)
    if lines is not None:
        modified_lines = []
        is_within_block = False
        for line in lines:
            stripped_line = line.strip()
            # Start of the block to be commented out
            if stripped_line.startswith('if !key.is_empty() && !token.is_empty() {'):
                is_within_block = True
                modified_lines.append("/*\n")
            if is_within_block:
                modified_lines.append(line)  # Add current line to modified
            else:
                modified_lines.append(line)  # Include unchanged lines
            # End of the block to be commented out
            if stripped_line == '}':
                if is_within_block:  # Only close the block if we were inside it
                    modified_lines.append("*/\n")
                    is_within_block = False

        write_file(file_path, modified_lines)
        print("Successfully updated client.rs to comment out TCP connection security section.")
    else:
        print("Failed to read client.rs")

def update_ui_file_with_icon(base_directory, icon_base64):
    """Update the ui.rs file with the new Base64 encoded icon."""
    ui_path = os.path.join(base_directory, "src", "ui.rs")
    if not os.path.isfile(ui_path):
        print("ui.rs file not found. Exiting.")
        return

    with open(ui_path, "r", encoding="utf-8") as file:
        ui_content = file.readlines()

    line_indices_to_replace = [788, 792]  # Adjust these line numbers based on your actual ui.rs

    for index in line_indices_to_replace:
        if 0 <= index < len(ui_content):
            old_line = ui_content[index].strip()
            print(f"Updating line {index + 1}: {old_line}")
            new_line = f'        "data:image/png;base64,{icon_base64}".into()\n'
            ui_content[index] = new_line

    with open(ui_path, "w", encoding="utf-8") as file:
        file.writelines(ui_content)

    print("Updated Base64 strings in ui.rs successfully!")

# Assuming this is part of the update process
def update_config_rs(file_path, new_app_name, new_pub_key, new_rendezvous_server):
    """Update the config.rs file with the new application name, public key, and rendezvous server."""
    try:
        lines = read_file(file_path)
        if lines is None:
            return

        # Initialize flags to check if the lines have been modified
        app_name_modified = False
        pub_key_modified = False
        rendezvous_server_modified = False  # New flag for rendezvous server update

        for i in range(len(lines)):
            # Update the application name
            if "pub static ref APP_NAME: RwLock<String> = RwLock::new(" in lines[i]:
                lines[i] = f'pub static ref APP_NAME: RwLock<String> = RwLock::new("{new_app_name}".to_owned());\n'
                app_name_modified = True

            # Update the public key
            if "pub const PUBLIC_RS_PUB_KEY: &str =" in lines[i]:
                lines[i] = f'pub const PUBLIC_RS_PUB_KEY: &str = "{new_pub_key}";\n'
                pub_key_modified = True

          # Update the PROD_RENDEZVOUS_SERVER
            if "pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new(match option_env!(\"RENDEZVOUS_SERVER\") {" in lines[i]:
                # Look for the next line that contains the "_ => """ statement
                if i + 2 < len(lines) and "_ => \"\"" in lines[i + 2]:
                    lines[i + 2] = f'    _ => "{new_rendezvous_server}",\n'
                    rendezvous_server_modified = True

        write_file(file_path, lines)

        if app_name_modified:
            print(f"Changed APP_NAME to '{new_app_name}'")
        if pub_key_modified:
            print(f"Changed PUBLIC_RS_PUB_KEY to '{new_pub_key}'")
        if rendezvous_server_modified:
            print(f"Changed PROD_RENDEZVOUS_SERVER to '{new_rendezvous_server}'")

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

def browse_directory():
    """Open a dialog to browse directories and handle the updates."""
    root.withdraw()  # Hide the Tkinter window

    base_directory = select_directory("Select your RustDesk source directory.")
    if not base_directory:
        print("No directory selected. Exiting.")
        root.deiconify()
        return

    new_app_name = app_name_entry.get().strip()
    new_pub_key = pub_key_entry.get().strip()
    executable_name = executable_name_entry.get().strip()
    command_to_run = command_entry.get().strip()
    new_rendezvous_server = rendezvous_server_entry.get().strip()  # Retrieve the custom rendezvous server entry

    # Validate inputs
    if not new_app_name or not new_pub_key or not new_rendezvous_server:
        messagebox.showwarning("Input Error", "App name, public key, and rendezvous server cannot be empty.")
        root.deiconify()
        return

    try:
        # Update the config.rs with the new parameters
        update_config_rs(os.path.join(base_directory, 'libs', 'hbb_common', 'src', 'config.rs'), new_app_name, new_pub_key, new_rendezvous_server)

        icon_file = select_file("Select the Icon PNG Image", [("Image Files", "*.png")])
        if not icon_file or not os.path.isfile(icon_file):
            print("No icon image selected. Exiting.")
            root.deiconify()
            return
        new_icon_base64 = convert_to_base64(icon_file)

        # Download sciter.dll
        sciter_dll_destination = os.path.join(base_directory, 'sciter.dll')
        if download_sciter_dll(sciter_dll_destination):
            print(f"Downloaded sciter.dll to {sciter_dll_destination}.")
        
        # Copy the selected icon to the RustDesk res directory as icon.ico and tray-icon
        res_dir = os.path.join(base_directory, 'res')

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

        # Update the ui.rs with the new icon
        update_ui_file_with_icon(base_directory, new_icon_base64)

        # Call other update functions
        update_build_py(os.path.join(base_directory, 'build.py'), new_app_name)
        update_cargo_toml(os.path.join(base_directory, 'Cargo.toml'), new_app_name)
        update_cargo_toml_description(os.path.join(base_directory, 'Cargo.toml'), description_entry.get().strip())
        update_native_model(os.path.join(base_directory, 'flutter', 'lib', 'models', 'native_model.dart'), new_app_name)
        update_platform_model(os.path.join(base_directory, 'flutter', 'lib', 'models', 'platform_model.dart'), new_app_name)
        update_web_model(os.path.join(base_directory, 'flutter', 'lib', 'models', 'web_model.dart'), new_app_name)
        update_bridge_file(os.path.join(base_directory, 'flutter', 'lib', 'web', 'bridge.dart'), new_app_name)
        update_cmakelists(os.path.join(base_directory, 'flutter', 'windows', 'CMakeLists.txt'), new_app_name)
        update_main_cpp(os.path.join(base_directory, 'flutter', 'windows', 'runner', 'main.cpp'), new_app_name)
        update_runner_rc(os.path.join(base_directory, 'flutter', 'windows', 'runner', 'Runner.rc'), new_app_name)
        update_portable_cargo_toml(os.path.join(base_directory, 'libs', 'portable', 'Cargo.toml'), new_app_name)
        rust_file_path = os.path.join(base_directory, 'libs', 'portable', 'src', 'main.rs')
        update_rustdesk_desktop_file(os.path.join(base_directory, 'res', 'rustdesk.desktop'), new_app_name)
        update_rustdesk_service(os.path.join(base_directory, 'res', 'rustdesk.service'), new_app_name)
        update_client_file(base_directory)

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
icon_url = "https://www.iconarchive.com/download/i144838/gartoon-team/gartoon-apps/gnome-remote-shell.ico"  # Icon URL
icon_path = "downloaded_icon.ico"  # Path where the icon will be saved

# Download the icon
if download_icon(icon_url, icon_path):
    # Now show the splash screen with the downloaded icon
    splash = show_splash_screen(theme_name=theme_name, icon_path=icon_path)
else:
    print(f"Icon could not be downloaded from: {icon_url}")

# Load main window after the splash
root = ThemedTk()
root.title("Infinite Remote")
root.geometry("700x600")
root.set_theme(theme_name)

# Set the icon for the main window
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

# New Description Entry
description_label = ttk.Label(main_frame, text="Enter new description AKA RustDesk Remote Desktop:")
description_label.pack(pady=5)

description_entry = ttk.Entry(main_frame)  # Entry for the description
description_entry.pack(pady=5)

# New Public Key Entry
pub_key_label = ttk.Label(main_frame, text="Enter new public key:")
pub_key_label.pack(pady=5)

pub_key_entry = ttk.Entry(main_frame)  # Entry for the public key
pub_key_entry.pack(pady=5)

# New Rendezvous Server Entry
rendezvous_server_label = ttk.Label(main_frame, text="Enter new rendezvous server:")
rendezvous_server_label.pack(pady=5)

rendezvous_server_entry = ttk.Entry(main_frame)  # Entry for the custom rendezvous server
rendezvous_server_entry.pack(pady=5)

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

# Clean up: Remove the icon file after use
if os.path.exists(icon_path):
    os.remove(icon_path)

# Only necessary for debugging
print(root.get_themes())  # This will list all available themes
