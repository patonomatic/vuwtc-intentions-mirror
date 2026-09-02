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
            if response.status != 200:
                raise Exception(f"Non-200 response received: {response.status}")

            html = response.read().decode('utf-8')

            # Convert relative links to absolute URL path
            html = re.sub(r'href="/', 'href="https://www.vuwtc.org.nz/', html)
            html = re.sub(r'src="/', 'src="https://www.vuwtc.org.nz/', html)

            soup = BeautifulSoup(html, 'html.parser')

            # Strip specific elements from DOM
            for element_id in ["email-list-subscribe-section", "error-modal"]:
                elem = soup.find(id=element_id)
                if elem:
                    elem.decompose()

            # Remove font preloads pointing to primary server
            for preload in soup.find_all('link', rel=lambda r: r and 'preload' in r):
                if 'trip-planner-icons' in preload.get('href', ''):
                    preload.decompose()

            # Inject CSS for local font & display rules
            custom_style = soup.new_tag('style')
            custom_style.string = """
                body.modal-open {
                    overflow: auto !important;
                    padding-right: 0 !important;
                }
                @font-face {
                    font-family: 'trip-planner-icons' !important;
                    src: url('./trip-planner-icons.woff') format('woff') !important;
                    font-weight: normal;
                    font-style: normal;
                }
                #error-modal, .modal-backdrop {
                    display: none !important;
                    opacity: 0 !important;
                    visibility: hidden !important;
                }
            """
            if soup.head:
                soup.head.append(custom_style)

            # Override window alert & promise rejections
            suppress_script = soup.new_tag('script')
            suppress_script.string = """
                window.alert = function() { console.log('Suppressed alert:', arguments); };
                window.addEventListener('unhandledrejection', function(event) {
                    event.preventDefault();
                });
            """
            if soup.head:
                soup.head.insert(0, suppress_script)

            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(str(soup))
                
            print("Successfully transformed and saved index.html")
            
    except Exception as e:
        print(f"Error processing page: {e}")
        raise e

if __name__ == "__main__":
    scrape()
