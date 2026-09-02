import urllib.request
import re
from bs4 import BeautifulSoup

URL = "https://www.vuwtc.org.nz/trips/intentions"
OUTPUT_FILE = "index.html"

def scrape():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            # Explicit status check (triggers only if status isn't 200 OK)
            if response.status != 200:
                raise Exception(f"Failed to fetch page. Server returned status code: {response.status}")
            html = response.read().decode('utf-8')

            # 1. Convert relative links to absolute URL path
            html = re.sub(r'href="/', 'href="https://www.vuwtc.org.nz/', html)
            html = re.sub(r'src="/', 'src="https://www.vuwtc.org.nz/', html)

            soup = BeautifulSoup(html, 'html.parser')

            # 2. Hide the email subscription section if present
            subscribe_elem = soup.find(id="email-list-subscribe-section")
            if subscribe_elem:
                subscribe_elem.decompose()

            # 3. Inject CSS to hide email subscribe fallback and handle cross-origin fonts
            custom_style = soup.new_tag('style')
            custom_style.string = """
                #email-list-subscribe-section { display: none !important; }
                
                /* Override font-family fallback icons if cross-origin font load is blocked */
                @font-face {
                    font-family: 'trip-planner-icons';
                    src: url('https://www.vuwtc.org.nz/fonts/trip-planner-icons.woff?1.04') format('woff');
                }
            """
            if soup.head:
                soup.head.append(custom_style)

            # 4. Inject script to override window.alert or modal popups from failed AJAX calls
            suppress_script = soup.new_tag('script')
            suppress_script.string = """
                // Neutralize alert popups from failed cross-origin background updates (like timezone API)
                window.alert = function() { console.log('Suppressed alert:', arguments); };
                
                // Catch unhandled AJAX/Promise rejections preventing error modals
                window.addEventListener('unhandledrejection', function(event) {
                    event.preventDefault();
                });
            """
            if soup.head:
                soup.head.insert(0, suppress_script)

            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(str(soup))
                
            print("Successfully transformed and updated index.html")
            
    except Exception as e:
        print(f"Error processing page: {e}")
        raise e

if __name__ == "__main__":
    scrape()
