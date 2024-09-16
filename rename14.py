import tkinter as tk
from tkinter import filedialog
import os
import re
import subprocess
import time

def show_splash_screen(duration=3000):
    # Create a splash screen
    splash = tk.Tk()
    splash.title("Infinite Remote!")
    
    # Set the dimensions of the splash screen
    splash_width = 300
    splash_height = 150
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()

    # Calculate x and y coordinates for the splash screen to center it
    x = (screen_width // 2) - (splash_width // 2)
    y = (screen_height // 2) - (splash_height // 2)

    splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")  # Width x Height + X + Y
    splash.configure(bg="lightblue")

    # Add a label for the developer's name
    developer_name = "Developer: @VenimK @ Discord"
    label = tk.Label(splash, text=developer_name, bg="lightblue", font=("Helvetica", 14))
    label.pack(expand=True)

    # Bring splash screen to front and focus on it
    splash.lift()
    splash.focus_force()

    # Display the splash screen for a few seconds
    splash.after(duration, splash.destroy)  # Display for the specified duration (default: 3 seconds)
    splash.mainloop()

# Declare global variables for the entry fields
app_name_entry = None
executable_name_entry = None

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

def update_file(file_path, new_app_name, updates):
    """General file update function."""
    content = read_file(file_path)
    if content is None:
        return

    updated_content = []
    for line in content:
        for pattern, replacement in updates:
            if re.search(pattern, line):
                line = re.sub(pattern, replacement.format(new_app_name), line)
                print(f"Updating line: {line.strip()}")
        updated_content.append(line)

    write_file(file_path, updated_content)
    print(f"Updated {file_path} with new application name: {new_app_name}")

def update_build_py(file_path, new_app_name):
    """Update the build.py file with the new application name."""
    try:
        print(f"Updating {file_path} with new application name: {new_app_name}")
        content = read_file(file_path)
        if content is None:
            return

        updated_content = []
        for line in content:
            # Replace occurrences of 'hbb_name' assignment to include the new application name
            if 'hbb_name =' in line:
                line = re.sub(r"hbb_name\s*=\s*['\"]([^'\"]+)['\"]", f"hbb_name = '{new_app_name}'", line)

            # Update other lines that should include the application name
            if 'set_app_name' in line:  # Example: modify based on your code structure
                line = re.sub(r'set_app_name\(\s*["\']([^"\']+)["\']', f'set_app_name("{new_app_name}"', line)

            updated_content.append(line)

        write_file(file_path, updated_content)
        print(f"Updated {file_path} with the new application name: {new_app_name}.")

    except Exception as e:
        print(f"An error occurred while updating {file_path}: {e}")

def update_cargo_toml(file_path, new_app_name):
    try:
        """Update the Cargo.toml file to set name, default-run, and modify features."""
        content = read_file(file_path)
        if content is None:
            return

        updated_content = []
        in_package_section = False
        in_metadata_section = False
        in_features_section = False
        
        for line in content:
            stripped_line = line.strip()  # Trim whitespace
            
            # Identify the start of the [package] section
            if stripped_line == '[package]':
                in_package_section = True

            # Define end of the section on encountering a new section header
            elif in_package_section and stripped_line.startswith('['):
                in_package_section = False
            
            # Update 'name' and 'default-run' in the [package] section
            if in_package_section:
                # Check and update 'name' field
                if stripped_line.startswith('name ='):
                    line = f'name = "{new_app_name}"\n'
                # Check and update 'default-run' field
                elif stripped_line.startswith('default-run ='):
                    line = f'default-run = "{new_app_name}"\n'

            # Identify the start of the [package.metadata.winres] section
            if stripped_line == '[package.metadata.winres]':
                in_metadata_section = True
            
            # Update 'ProductName' and 'OriginalFilename' in the [package.metadata.winres] section
            if in_metadata_section:
                # Check and update 'ProductName' field
                if stripped_line.startswith('ProductName ='):
                    line = f'ProductName = "{new_app_name}"\n'
                # Check and update 'OriginalFilename' field
                elif stripped_line.startswith('OriginalFilename ='):
                    line = f'OriginalFilename = "{new_app_name.lower()}.exe"\n'

            # Identify the start of the [features] section
            if stripped_line == '[features]':
                in_features_section = True
            
            # Update 'use_dasp' within the [features] section
            if in_features_section:
                if stripped_line.startswith('use_dasp ='):
                    line = 'use_dasp = ["dasp", "inline"]\n'

            # If a new section starts, we need to exit the features section
            elif in_features_section and stripped_line.startswith('['):
                in_features_section = False

            updated_content.append(line)

        write_file(file_path, updated_content)
        print("Updated Cargo.toml content:")
        print(''.join(updated_content))  # Print updated content for debugging
        
    except FileNotFoundError:
        print("Cargo.toml file not found in the selected directory.")
    except Exception as e:
        print(f"An error occurred while updating Cargo.toml: {e}")

def update_native_model(file_path, new_app_name):
    updates = [
        (r'late\s+\w+Impl\s*_ffiBind;', f'late {new_app_name}Impl _ffiBind;'),
        (r'\w+Impl\s+get ffiBind\s*=>\s*_ffiBind;', f'{new_app_name}Impl get ffiBind => _ffiBind;'),
        (r'_ffiBind\s*=\s*[^;]+;', f'_ffiBind = {new_app_name}Impl(dylib);'),
        (r'_startListenEvent\(\w+Impl\s+\w+\)', f'_startListenEvent({new_app_name}Impl {new_app_name}Impl)'),
        (r'var sink = \w+Impl\.startGlobalEventStream\(', f'var sink = {new_app_name}Impl.startGlobalEventStream(')
    ]
    update_file(file_path, new_app_name, updates)

def update_platform_model(file_path, new_app_name):
    updates = [
        (r'(\w+)Impl\s+get bind\s*=>\s*platformFFI\.ffiBind;', f'{new_app_name}Impl get bind => platformFFI.ffiBind;')
    ]
    update_file(file_path, new_app_name, updates)

def update_web_model(file_path, new_impl_name):
    # Identifying the current implementation name logic can be left unchanged for simplicity
    content = read_file(file_path)
    if content is None:
        return

    previous_impl_name = None
    for line in content:
        if "final" in line and " _ffiBind =" in line:
            previous_impl_name = line.split()[1]  # Gets the type before _ffiBind
            break

    if previous_impl_name is None:
        print("No implementation name found to replace.")
        return

    updated_content = []
    for line in content:
        if f'final {previous_impl_name} _ffiBind =' in line:
            line = line.replace(previous_impl_name, f'{new_impl_name}Impl')
            line = line.replace(f'{previous_impl_name}()', f'{new_impl_name}Impl()')

        if f'{previous_impl_name} get ffiBind =>' in line:
            line = line.replace(previous_impl_name, f'{new_impl_name}Impl')

        updated_content.append(line)

    write_file(file_path, updated_content)
    print(f"Updated web_model.dart with the new implementation name: {new_impl_name}Impl.")

def update_bridge_file(file_path, new_class_name):
    content = read_file(file_path)
    if content is None:
        return

    current_class_name = None
    for line in content:
        if line.strip().startswith('class ') and 'Impl' in line:
            current_class_name = line.split()[1].strip()  # Capture current class name
            break

    if current_class_name is None:
        print("No implementation class name found to replace.")
        return

    updated_content = []
    for line in content:
        if f'class {current_class_name} ' in line:
            line = line.replace(current_class_name, f'{new_class_name}Impl')
        updated_content.append(line)

    write_file(file_path, updated_content)
    print(f"Updated bridge.dart with the new class name: {new_class_name}Impl.")

def update_cmakelists(file_path, new_app_name):
    updates = [
        (r'set\(BINARY_NAME\s+"([^"]+)"\)', f'set(BINARY_NAME "{new_app_name}")')
    ]
    update_file(file_path, new_app_name, updates)

def update_main_cpp(file_path, new_app_name):
    updates = [
        (r'std::wstring app_name = L"([^"]+)";', f'std::wstring app_name = L"{new_app_name}";')
    ]
    update_file(file_path, new_app_name, updates)

def update_runner_rc(file_path, new_app_name):
    updates = [
        (r'VALUE\s+"InternalName",\s+"[^"]*"', f'VALUE "InternalName", "{new_app_name.lower()}"'),
        (r'VALUE\s+"OriginalFilename",\s+"[^"]*"', f'VALUE "OriginalFilename", "{new_app_name.lower()}.exe"')
    ]
    update_file(file_path, new_app_name, updates)

def update_portable_cargo_toml(file_path, new_app_name):
    """
    This function updates the Cargo.toml file in libs/portable
    to set the ProductName and OriginalFilename based on the new app name.
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            content = file.readlines()

        print("Original libs/portable/Cargo.toml content:")
        print(''.join(content))  # Print original content for debugging

        updated_content = []
        in_winres_section = False

        for line in content:
            stripped_line = line.strip()  # Trim whitespace from both ends
            print(f"Processing line: '{stripped_line}'")  # Debug output

            if stripped_line == '[package.metadata.winres]':
                in_winres_section = True
                print("Entering [package.metadata.winres] section.")  # Debug output
                updated_content.append(line)  # Preserve the section header
                continue
            
            elif in_winres_section and stripped_line.startswith('['):
                in_winres_section = False  # Exit from winres section
                print("Exiting [package.metadata.winres] section.")  # Debug output

            if in_winres_section:
                # Check and update 'ProductName' field
                if stripped_line.startswith('ProductName ='):
                    print(f"Updating ProductName from: {line.strip()} to ProductName = \"{new_app_name}\"")  # Debug output
                    line = f'ProductName = "{new_app_name}"\n'  # Updated line
                # Check and update 'OriginalFilename' field
                elif stripped_line.startswith('OriginalFilename ='):
                    print(f"Updating OriginalFilename from: {line.strip()} to OriginalFilename = \"{new_app_name.lower()}.exe\"")  # Debug output
                    line = f'OriginalFilename = "{new_app_name.lower()}.exe"\n'  # Updated line

            updated_content.append(line)

        # Write the changes back to the libs/portable/Cargo.toml file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(updated_content)

        print("Updated libs/portable/Cargo.toml content:")
        print(''.join(updated_content))  # Print updated content for debugging

    except FileNotFoundError:
        print("libs/portable/Cargo.toml file not found in the selected directory.")
    except Exception as e:
        print(f"An error occurred while updating libs/portable/Cargo.toml: {e}")

def update_config_rs(file_path, new_app_name):
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

def update_generate_py(file_path, executable_name):
    try:
        print(f"Updating {file_path} with new executable name: {executable_name}")
        content = read_file(file_path)
        if content is None:
            return

        updated_content = []
        for line in content:
            if 'options.executable =' in line:
                line = re.sub(r'options\.executable\s*=\s*"([^"]*)"', f'options.executable = "{executable_name}.exe"', line)
            updated_content.append(line)

        write_file(file_path, updated_content)
        print(f"Updated {file_path} with the new executable name: {executable_name}.")
        
    except Exception as e:
        print(f"An error occurred while updating {file_path}: {e}")

def update_rust_file(file_path, new_app_prefix):
    try:
        print(f"Updating {file_path} with new APP_PREFIX: {new_app_prefix}")
        content = read_file(file_path)
        if content is None:
            return
        
        updated_content = []
        for line in content:
            if line.startswith("const APP_PREFIX: &str ="):
                line = re.sub(r'const APP_PREFIX: &str\s*=\s*"([^"]*)"', f'const APP_PREFIX: &str = "{new_app_prefix}"', line)
            updated_content.append(line)

        write_file(file_path, updated_content)
        print(f"Updated {file_path} with new APP_PREFIX: {new_app_prefix}.")
        
    except Exception as e:
        print(f"An error occurred while updating {file_path}: {e}")

def update_rustdesk_desktop_file(file_path, new_app_name):
    """Update the rustdesk.desktop file with the new application name."""
    if not os.path.exists(file_path):
        print(f"Desktop file not found at: {file_path}")
        return

    content = read_file(file_path)
    if content is None:
        return

    updated_content = []
    in_desktop_entry = False

    for line in content:
        stripped_line = line.strip()
        
        if stripped_line == '[Desktop Entry]':
            in_desktop_entry = True
        
        if in_desktop_entry and stripped_line.startswith('Name='):
            print(f"Updating '{stripped_line}' to 'Name={new_app_name}'")
            line = f'Name={new_app_name}\n'
        
        if stripped_line == '' and in_desktop_entry:
            in_desktop_entry = False

        updated_content.append(line)

    write_file(file_path, updated_content)
    print(f"Updated {file_path} with new application name: {new_app_name}")

def update_rustdesk_service(file_path, new_app_name):
    """Update the rustdesk.service file with the new application description."""
    if not os.path.exists(file_path):
        print(f"Service file not found at: {file_path}")
        return

    content = read_file(file_path)
    if content is None:
        return

    updated_content = []
    
    for line in content:
        stripped_line = line.strip()
        
        if stripped_line.startswith('Description='):
            print(f"Updating '{stripped_line}' to 'Description={new_app_name}'")
            line = f'Description={new_app_name}\n'

        updated_content.append(line)

    write_file(file_path, updated_content)
    print(f"Updated {file_path} with new application description: {new_app_name}")

def browse_directory():
    # Hide the main Tkinter window (only for the directory dialog)
    root.withdraw()  # Hide the root window

    folder_selected = filedialog.askdirectory(title="Select RustDesk Directory")
    if folder_selected:
        print("Selected directory:", folder_selected)
        new_app_name = app_name_entry.get()
        executable_name = executable_name_entry.get()

        if not new_app_name:
            print("Please enter a new application name.")
            return  # Exit early if the new_app_name is not provided

        # File updates
        update_build_py(os.path.join(folder_selected, 'build.py'), new_app_name)
        update_cargo_toml(os.path.join(folder_selected, 'Cargo.toml'), new_app_name)
        update_native_model(os.path.join(folder_selected, 'flutter', 'lib', 'models', 'native_model.dart'), new_app_name)
        update_platform_model(os.path.join(folder_selected, 'flutter', 'lib', 'models', 'platform_model.dart'), new_app_name)
        update_web_model(os.path.join(folder_selected, 'flutter', 'lib', 'models', 'web_model.dart'), new_app_name)
        update_bridge_file(os.path.join(folder_selected, 'flutter', 'lib', 'web', 'bridge.dart'), new_app_name) 
        update_cmakelists(os.path.join(folder_selected, 'flutter', 'windows', 'CMakeLists.txt'), new_app_name)
        update_main_cpp(os.path.join(folder_selected, 'flutter', 'windows', 'runner', 'main.cpp'), new_app_name)
        update_runner_rc(os.path.join(folder_selected, 'flutter', 'windows', 'runner', 'Runner.rc'), new_app_name)  
        update_portable_cargo_toml(os.path.join(folder_selected, 'libs', 'portable', 'Cargo.toml'), new_app_name)
        update_config_rs(os.path.join(folder_selected, 'libs', 'hbb_common', 'src', 'config.rs'), new_app_name)
        rust_file_path = os.path.join(folder_selected, 'libs', 'portable', 'src', 'main.rs')
        update_rust_file(rust_file_path, new_app_name)
        update_rustdesk_desktop_file(os.path.join(folder_selected, 'res', 'rustdesk.desktop'), new_app_name)
        update_rustdesk_service(os.path.join(folder_selected, 'res', 'rustdesk.service'), new_app_name)        

        # Update generate.py with the new executable name, if provided
        if executable_name:
            generate_py_path = os.path.join(folder_selected, 'libs', 'portable', 'generate.py')
            update_generate_py(generate_py_path, executable_name)
        else:
            print("Please enter an executable name.")

        # Execute the inline-sciter.py command after all files have been updated
       # Build the path to the `common.css` file
        common_css_path = os.path.join(folder_selected, 'src', 'ui', 'common.css')
        
        try:
            # Attempt to open the common.css file
            common_css = open(common_css_path).read()
            print("Successfully read common.css")
            
            # Path to the inline-sciter.py script
            inline_sciter_path = os.path.join(folder_selected, 'res', 'inline-sciter.py')
            
            # Execute inline-sciter.py in the selected directory
            subprocess.run(["python", inline_sciter_path], cwd=folder_selected, check=True)
            print("Successfully executed inline-sciter.py")
        
        except FileNotFoundError:
            print(f"The file '{common_css_path}' was not found. Please check the file path.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing inline-sciter.py: {e}")
        

# Create a simple GUI
root = tk.Tk()
root.title("RustDesk Renamer")
root.geometry("400x300")

label = tk.Label(root, text="Select the RustDesk directory:")
label.pack(pady=10)

browse_button = tk.Button(root, text="Browse...", command=browse_directory)
browse_button.pack(pady=5)

app_name_label = tk.Label(root, text="Enter new application name:")
app_name_label.pack(pady=5)

app_name_entry = tk.Entry(root)
app_name_entry.pack(pady=5)

executable_name_label = tk.Label(root, text="Enter new executable name (without .exe):")
executable_name_label.pack(pady=5)

executable_name_entry = tk.Entry(root)
executable_name_entry.pack(pady=5)

# Show the splash screen when the script is run
show_splash_screen()

# Start the GUI loop
root.mainloop()