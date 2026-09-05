import os
import sys
import time
import subprocess
import getpass
import psutil
import pyautogui
import ctypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# PyAutoGUI Safety & Delay Settings
pyautogui.PAUSE = 0.8
pyautogui.FAILSAFE = True

# ==============================================================================
# CONFIGURATION & SPLIT PATHS
# ==============================================================================
TALLY_EXE_PATH = r"C:\Program Files\TallyPrime\tally.exe"

PROJECT_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_GUI_DIR = r"C:\Users\Administrator\Desktop\tally database"
BAT_FILE_NAME = "run-gui.bat"
GUI_URL = f"file:///{BACKEND_GUI_DIR}/gui.html".replace("\\", "/")

# Tally Credentials & Company Identifiers
MAIN_COMPANY = "Bijoy Bhandar 25-26"
MEMBER_COMPANY_AP = "Bijoy Bhandar (A.P.)"
USERNAME = ""
PASSWORD = ""

# 🔴 FIX: Start on 9000, but allow it to change dynamically
STARTING_PORT = "9000"

SYNC_TARGETS = [
    {
        "schema": "tallydb",
        "company": "Bijoy Bhandar (H/w) - (from 1-Apr-25)"
    },
    {
        "schema": "tallydb3",
        "company": "Bijoy Bhandar (F/s) - (from 1-Apr-25)"
    },
    {
        "schema": "tallydb4",
        "company": "Bijoy Bhandar (S/r) - (from 1-Apr-25)"
    },
    {
        "schema": "tallydb5",        
        "company": "Bijoy Bhandar(Gro) - (from 1-Apr-25)"   
    },
    {
        "schema": "tallydb6",          
        "company": "Bijoy Bhandar (A.P.)"   
    },
    {
        "schema": "P_R",          
        "company": "P & R Construction"    
    }
]
# ==============================================================================


# ------------------------------------------------------------------------------
# SECTION 1: TALLY DESKTOP AUTOMATION (PYAUTOGUI)
# ------------------------------------------------------------------------------
def ensure_capslock_off():
    VK_CAPITAL = 0x14
    if ctypes.windll.user32.GetKeyState(VK_CAPITAL) & 1:
        print("[WARNING] Caps Lock is ON. Automatically disabling it...")
        pyautogui.press('capslock')
        time.sleep(0.5)

def focus_tally_window():
    width, height = pyautogui.size()
    pyautogui.click(width / 2, 20)
    time.sleep(0.5)

def force_kill_tally():
    current_user = getpass.getuser().lower()
    print(f"[CLEANUP] Checking for stuck Tally processes owned by '{current_user}'...")
    
    killed_any = False
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == 'tally.exe':
                proc_user = (proc.info['username'] or '').lower()
                
                # Check if the process belongs to the current user/admin session
                if current_user in proc_user:
                    print(f"  -> Terminating local Tally process (PID: {proc.info['pid']})...")
                    proc.kill()
                    killed_any = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    if killed_any:
        time.sleep(2)
        print("[CLEANUP] Local user Tally instance closed.")
    else:
        print("[CLEANUP] No active Tally instance found for this user.")

def prepare_tally_environment(target_port):
    ensure_capslock_off()
    
    # 🔴 FIX: Only force-kill Tally if we are NOT testing during working hours
    if "--no-kill" not in sys.argv:
        force_kill_tally()
    else:
        print("[INFO] Working hours mode active. Skipping Tally force-kill...")
    
    print(f"[START] Launching Tally Prime (Configuring for Port {target_port})...")
    subprocess.Popen(TALLY_EXE_PATH)
    print("[WAIT] Waiting 20 seconds for Tally Prime startup screen...")
    time.sleep(20)

    focus_tally_window()

    print(f"[SEARCH] Selecting Primary Company: '{MAIN_COMPANY}'...")
    pyautogui.write(MAIN_COMPANY, interval=0.05)
    pyautogui.press('enter')
    time.sleep(2)

    print(f"[LOGIN] Logging in as '{USERNAME}'...")
    pyautogui.write(USERNAME, interval=0.05)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.write(PASSWORD, interval=0.05)
    pyautogui.press('enter')
    time.sleep(40)

    print("[SETTINGS] Navigating to F1: Help -> Settings -> Connectivity...")
    pyautogui.press('f1') 
    time.sleep(1.5)
    pyautogui.press('s')  
    time.sleep(1.5)
    pyautogui.press('n')  
    time.sleep(1.5)
    pyautogui.press('enter')  
    time.sleep(1.5)

    print(f"[CONFIG] Setting Client/Server: Both | ODBC: Yes | Port: {target_port}...")
    
    pyautogui.write("Both", interval=0.3)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    
    pyautogui.write("Yes", interval=0.3)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    
    pyautogui.write(str(target_port), interval=0.3)
    time.sleep(1)
    
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(2)
    
    print("[RESTART] Accepting Tally restart prompt...")
    pyautogui.press('y')
    
    print("[WAIT] Waiting 20 seconds for Tally to reboot...")
    time.sleep(20)

    print(f"[LOGIN] Re-logging into '{MAIN_COMPANY}' post-restart...")
    focus_tally_window()
    pyautogui.write(MAIN_COMPANY, interval=0.05)
    pyautogui.press('enter')
    time.sleep(2)
    
    pyautogui.write(USERNAME, interval=0.05)
    pyautogui.press('enter')
    time.sleep(1)
    
    pyautogui.write(PASSWORD, interval=0.05)
    pyautogui.press('enter')
    time.sleep(40)
    
    print(f"[FOLDER] Pressing F3 -> Selecting 'Select Company' -> Loading '{MEMBER_COMPANY_AP}'...")
    pyautogui.press('f3') 
    time.sleep(1.5)
    pyautogui.press('up', presses=10, interval=0.05)
    time.sleep(0.5)
    pyautogui.press('down', presses=2, interval=0.2)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)
    
    pyautogui.write(MEMBER_COMPANY_AP, interval=0.05)
    pyautogui.press('enter')
    print("[WAIT] Loading company, please wait 20 seconds...")
    time.sleep(20)

    print("[FOLDER] Navigating Directory Tree for P & R Construction...")
    pyautogui.press('f3')
    time.sleep(1.5)
    pyautogui.press('up', presses=10, interval=0.05)
    time.sleep(0.5)
    pyautogui.press('down', presses=2, interval=0.2)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)

    pyautogui.press('up', presses=15, interval=0.05)  
    time.sleep(0.5)
    pyautogui.press('down', presses=5, interval=0.2)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1.5)

    pyautogui.press('up', presses=15, interval=0.05)  
    time.sleep(0.5)
    pyautogui.press('down', presses=5, interval=0.2)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1.5)

    pyautogui.write("P&R", interval=0.05)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1.5)

    pyautogui.write("10005", interval=0.05)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1.5)

    pyautogui.write("P & R Construction", interval=0.05)
    time.sleep(0.5)
    pyautogui.press('enter')
    
    print("[WAIT] Loading final company...")
    time.sleep(8) 
    print("[SUCCESS] Tally Prime setup complete! All required companies are loaded.")


# ------------------------------------------------------------------------------
# SECTION 2: WEB GUI & BIGQUERY SYNC AUTOMATION (SELENIUM)
# ------------------------------------------------------------------------------
def start_backend():
    print("[START] Starting local Node.js backend server...")
    bat_path = os.path.join(BACKEND_GUI_DIR, BAT_FILE_NAME)
    return subprocess.Popen(
        bat_path, 
        cwd=BACKEND_GUI_DIR, 
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def run_sync_pipeline(initial_port):
    options = webdriver.ChromeOptions()
    options.add_argument("--allow-file-access-from-files")
    options.add_argument("--disable-web-security")
    options.add_argument("--remote-allow-origins=*")
    
    print("  [WEB] Running Chrome   ")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # 🔴 FIX 1: Bring back the persistent profile so it stops acting like a Guest!
    profile_path = os.path.join(PROJECT_BASE_DIR, "tally_chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--profile-directory=Default")
    
    current_tally_port = initial_port
    total_targets = len(SYNC_TARGETS)
    
    for idx, target in enumerate(SYNC_TARGETS, 1):
        schema_name = target["schema"]
        target_company = target["company"]
        
        print(f"\n--------------------------------------------------")
        print(f"[SYNC] [{idx}/{total_targets}] Schema: '{schema_name}' | Company: '{target_company}'")
        print(f"--------------------------------------------------")
        
        # 🔴 FIX 1: Launch a FRESH browser for every single company to prevent memory crashes
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 20)
            
            print(f"  [WEB] Loading a clean GUI Interface...")
            driver.get(GUI_URL)
            time.sleep(3)
            
            print("  [CONFIG] Setting Technology -> Google BigQuery")
            tech_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "database_technology"))))
            tech_dropdown.select_by_value("bigquery")
            time.sleep(1)
            
            port_input = wait.until(EC.element_to_be_clickable((By.ID, "tally_port")))
            reload_btn = driver.find_element(By.XPATH, "//input[@value='Reload Company List']")
            
            alternate_port = "9001" if current_tally_port == "9000" else "9000"
            ports_to_try = [current_tally_port, alternate_port]
            sync_successful = False
            
            for test_port in ports_to_try:
                try:
                    if test_port != current_tally_port:
                        print(f"  [RECOVERY ERROR] Sync failed on {current_tally_port}. Reconfiguring Tally Prime to Port {test_port}...")
                        
                        # 🔴 FIX 2: Safely attempt to minimize/maximize without breaking if the browser died
                        try:
                            driver.minimize_window()
                        except:
                            pass
                            
                        prepare_tally_environment(test_port)
                        current_tally_port = test_port
                        
                        try:
                            driver.maximize_window()
                        except:
                            pass
                        time.sleep(2)
                    
                    print(f"  [ATTEMPT] Testing GUI connection to Tally on Port {test_port}...")
                    port_input.clear()
                    port_input.send_keys(test_port)
                    time.sleep(0.5)
                    
                    driver.execute_script("arguments[0].click();", reload_btn)
                    time.sleep(4) 
                    
                    visible_body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                    if "unable to connect with tally" in visible_body_text:
                        raise ValueError(f"GUI Explicit Error: 'Unable to connect with Tally' caught on port {test_port}.")
                    
                    datalist_options = driver.find_elements(By.XPATH, "//datalist[@id='dl_tally_company']/option")
                    available_companies = [opt.get_attribute("value").strip() for opt in datalist_options if opt.get_attribute("value")]
                    
                    print(f"  [DEBUG] Companies actually found in GUI dropdown: {available_companies}")
                    
                    if not any(target_company.lower() in comp.lower() for comp in available_companies):
                        raise ValueError(f"Company '{target_company}' missing from GUI menu.")
                        
                    print(f"  [SUCCESS] Tally connected and company found! Proceeding with sync...")
                    
                    schema_input = wait.until(EC.element_to_be_clickable((By.ID, "database_schema")))
                    schema_input.clear()
                    schema_input.send_keys(schema_name)
                    time.sleep(1)
                    
                    company_input = wait.until(EC.element_to_be_clickable((By.ID, "tally_company")))
                    company_input.clear()
                    company_input.send_keys(target_company)
                    time.sleep(1)
                    
                    print("  [ACTION] Clicking Sync button...")
                    sync_btn = driver.find_element(By.ID, "btnSync")
                    driver.execute_script("arguments[0].click();", sync_btn)
                    
                    SUCCESS_KEYWORD = "import completed successfully" 
                    MAX_TIMEOUT = 1800  
                    
                    print(f"  [MONITOR] Watching live GUI logs. Waiting for '{SUCCESS_KEYWORD}'...")
                    
                    elapsed_time = 0
                    sync_finished = False
                    
                    while elapsed_time < MAX_TIMEOUT:
                        time.sleep(5)
                        elapsed_time += 5
                        
                        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                        
                        if "unable to connect with tally" in page_text:
                            raise ConnectionError(f"Sync crashed: 'Unable to connect with Tally' on port {test_port}")
                            
                        if SUCCESS_KEYWORD in page_text:
                            print(f"  [SUCCESS] Sync for {target_company} finished dynamically in {elapsed_time} seconds!")
                            sync_finished = True
                            break
                            
                    if not sync_finished:
                        raise TimeoutError(f"Sync timed out after {MAX_TIMEOUT} seconds! Backend might be frozen.")
                        
                    sync_successful = True
                    break 
                    
                except Exception as e:
                    print(f"  [WARNING] Sync failed -> {e}")
                    continue 

            if not sync_successful:
                print(f"[CRITICAL ERROR] Could not sync '{target_company}' on ANY port. Skipping to next company...")
                
        except Exception as err:
            print(f"[ERROR] Critical pipeline failure for {target_company}: {err}")
        finally:
            # 🔴 FIX 2: Safely destroy the browser and UNLOCK the profile folder
            if driver:
                try:
                    driver.quit()
                    print("  [CLEANUP] Browser closed. Releasing profile folder lock...")
                    time.sleep(3)  # Wait 3 seconds to guarantee Windows unlocks the folder!
                except:
                    pass
    print("\n==================================================")
    print("[FINISHED] ALL AVAILABLE TARGET COMPANIES PROCESSED")
    print("==================================================")

    
# ------------------------------------------------------------------------------
# SECTION 3: MASTER EXECUTION FLOW
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    backend_proc = None
    try:
        # Start the sequence on Port 9000
        prepare_tally_environment(STARTING_PORT)
        
        backend_proc = start_backend()
        print("[WAIT] Waiting for backend server initialization...")
        time.sleep(5)
        
        run_sync_pipeline(STARTING_PORT)
        
    finally:
        if backend_proc:
            backend_proc.terminate()
            print("[CLOSED] Backend process safely shut down.")