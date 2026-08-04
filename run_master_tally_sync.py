import os
import time
import subprocess
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
USERNAME = "admin"
PASSWORD = "bhandar2020"

# 🔴 FIX: Start on 9000, but allow it to change dynamically
STARTING_PORT = "9000"

SYNC_WAIT_TIME_PER_COMPANY = 300  

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
    pyautogui.click(width / 2, height / 3)
    time.sleep(0.5)

def force_kill_tally():
    print("[CLEANUP] Cleaning up any stuck Tally background processes...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "tally.exe"], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
        time.sleep(2)
    except Exception:
        pass

# 🔴 FIX: Modified to accept "target_port" so PyAutoGUI types the correct port
def prepare_tally_environment(target_port):
    ensure_capslock_off()
    force_kill_tally()
    
    print(f"[START] Launching Tally Prime (Configuring for Port {target_port})...")
    subprocess.Popen(TALLY_EXE_PATH)
    print("[WAIT] Waiting 15 seconds for Tally Prime startup screen...")
    time.sleep(15)

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
    time.sleep(4)

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
    pyautogui.write("Both", interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1)
    
    pyautogui.write("Yes", interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1)
    
    pyautogui.press('backspace', presses=5)
    
    # 🔴 FIX: Writes the dynamic port into Tally's settings
    pyautogui.write(target_port, interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter') 
    time.sleep(1.5)

    pyautogui.press('enter') 
    time.sleep(1.5)

    pyautogui.hotkey('ctrl', 'a')
    time.sleep(2)
    
    print("[RESTART] Accepting Tally restart prompt...")
    pyautogui.press('y') 
    print("[WAIT] Waiting 20 seconds for Tally reboot...") 
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
    time.sleep(4)
    
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
    print("[WAIT] Loading company, please wait 8 seconds...")
    time.sleep(8)

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
    
    profile_path = os.path.join(PROJECT_BASE_DIR, "tally_chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    current_tally_port = initial_port
    
    try:
        print(f"[WEB] Opening GUI Interface: {GUI_URL}")
        driver.get(GUI_URL)
        time.sleep(3)
        
        print("[CONFIG] Setting Technology -> Google BigQuery")
        tech_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "database_technology"))))
        tech_dropdown.select_by_value("bigquery")
        time.sleep(1)
        
        total_targets = len(SYNC_TARGETS)
        
        for idx, target in enumerate(SYNC_TARGETS, 1):
            schema_name = target["schema"]
            target_company = target["company"]
            
            print(f"\n--------------------------------------------------")
            print(f"[SYNC] [{idx}/{total_targets}] Schema: '{schema_name}' | Company: '{target_company}'")
            print(f"--------------------------------------------------")
            
            port_input = driver.find_element(By.ID, "tally_port")
            reload_btn = driver.find_element(By.XPATH, "//input[@value='Reload Company List']")
            
            alternate_port = "9001" if current_tally_port == "9000" else "9000"
            ports_to_try = [current_tally_port, alternate_port]
            sync_successful = False
            
            for test_port in ports_to_try:
                try:
                    if test_port != current_tally_port:
                        print(f"  [RECOVERY ERROR] Sync failed on {current_tally_port}. Reconfiguring Tally Prime inside PyAutoGUI to Port {test_port}...")
                        
                        driver.minimize_window()
                        prepare_tally_environment(test_port)
                        current_tally_port = test_port
                        driver.maximize_window()
                        time.sleep(2)
                    
                    print(f"  [ATTEMPT] Testing GUI connection to Tally on Port {test_port}...")
                    port_input.clear()
                    port_input.send_keys(test_port)
                    time.sleep(0.5)
                    
                    driver.execute_script("arguments[0].click();", reload_btn)
                    time.sleep(4) 
                    
                    # 🔴 FIX: Check for the exact GUI error text after reloading the company list!
                    if "Unable to connect with Tally" in driver.page_source:
                        raise ValueError(f"GUI Explicit Error: 'Unable to connect with Tally' caught on port {test_port}.")
                    
                    datalist_options = driver.find_elements(By.XPATH, "//datalist[@id='dl_tally_company']/option")
                    available_companies = [opt.get_attribute("value").strip() for opt in datalist_options if opt.get_attribute("value")]
                    
                    if not any(target_company in comp for comp in available_companies):
                        raise ValueError(f"Company '{target_company}' missing from GUI menu.")
                        
                    print(f"  [SUCCESS] Tally connected and company found! Proceeding with sync...")
                    
                    schema_input = driver.find_element(By.ID, "database_schema")
                    schema_input.clear()
                    schema_input.send_keys(schema_name)
                    time.sleep(1)
                    
                    company_input = driver.find_element(By.ID, "tally_company")
                    company_input.clear()
                    company_input.send_keys(target_company)
                    time.sleep(1)
                    
                    print("  [ACTION] Clicking Sync button...")
                    sync_btn = driver.find_element(By.ID, "btnSync")
                    driver.execute_script("arguments[0].click();", sync_btn)
                    
                    # 🔴 FIX: Aggressively monitor the output console for 10 seconds before waiting
                    print("  [MONITOR] Checking GUI output console for connection errors...")
                    error_detected = False
                    for _ in range(5):  # Check 5 times (every 2 seconds)
                        time.sleep(2)
                        if "Unable to connect with Tally" in driver.page_source:
                            error_detected = True
                            break
                            
                    if error_detected:
                        raise ConnectionError(f"Sync crashed right after clicking: 'Unable to connect with Tally' on port {test_port}")
                    
                    print(f"  [WAIT] No immediate port errors. Waiting {SYNC_WAIT_TIME_PER_COMPANY}s for BigQuery upload to finish...")
                    time.sleep(SYNC_WAIT_TIME_PER_COMPANY)
                    
                    print(f"  [SUCCESS] Completed sync sequence for {target_company}")
                    sync_successful = True
                    break 
                    
                except Exception as e:
                    print(f"  [WARNING] Sync failed -> {e}")
                    continue 

            if not sync_successful:
                print(f"[CRITICAL ERROR] Could not sync '{target_company}' on ANY port. Skipping to next company...")
            
        print("\n==================================================")
        print("[FINISHED] ALL AVAILABLE TARGET COMPANIES PROCESSED")
        print("==================================================")

    except Exception as err:
        print(f"[ERROR] Pipeline Execution Fault: {err}")
        
    finally:
        driver.quit()

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