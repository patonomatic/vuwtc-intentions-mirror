import urllib.request
import re

URL = "https://www.vuwtc.org.nz/trips/intentions"
OUTPUT_FILE = "index.html"

def scrape():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # Convert relative VUWTC links to absolute so styles, images, and fonts load correctly
            html = re.sub(r'href="/', 'href="https://www.vuwtc.org.nz/', html)
            html = re.sub(r'src="/', 'src="https://www.vuwtc.org.nz/', html)
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(html)
            print("Successfully updated index.html")
    except Exception as e:
        print(f"Error fetching intentions page: {e}")
        raise e

if __name__ == "__main__":
    scrape()
