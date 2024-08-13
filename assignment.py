from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time
import json

def valid_pan(pan):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return pan if re.match(pattern, pan) else None

def valid_gsti(gsti):
    pattern = r"[a-zA-Z0-9]{15}$"
    return gsti if re.match(pattern, gsti) else None

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://hprera.nic.in/PublicDashboard")

results = []

try:
    WebDriverWait(driver, 200).until(
        EC.presence_of_element_located((By.XPATH, '//a[@title="View Application"]'))
    )
    
    data_qs_list = []
    application_links = driver.find_elements(By.XPATH, '//a[@title="View Application"]')
    
    for link in application_links[:6]:
        data_qs = link.get_attribute("data-qs")
        if data_qs:
            data_qs_list.append(data_qs)
    
    for i, data_qs in enumerate(data_qs_list):
        driver.execute_script(f"tab_project_main_ApplicationPreview($('<a/>').attr('data-qs', '{data_qs}'));")
        
        time.sleep(10) 
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        person_data = {}
        
        name = soup.find('td', class_="fw-600")
        if name:
            person_data["Name"] = name.text.strip()
        
        address = soup.find_all("span", class_="fw-600")
        if address:
            address_list = [item.text.strip() for item in address]
            person_data["Address"] = address_list[-1]
        
        pan = soup.find_all("span", class_="mr-1 fw-600")
        for p in pan:
            pan_no = valid_pan(p.text.strip())
            gsti = valid_gsti(p.text.strip())
            if pan_no:
                person_data["PAN NO"] = pan_no
                
            if gsti:
                person_data["GSTIN"] = gsti
            else:
                person_data["GSTIN"] = 'NaN'
        
        if person_data:
            results.append(person_data)
        
        time.sleep(3)

except TimeoutException:
    print("Element not found within the specified timeout.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

json_output = json.dumps(results, indent=4)
print(json_output)

with open('output.json', 'w') as f:
    f.write(json_output)
