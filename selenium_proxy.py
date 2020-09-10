import rpyc
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import Options

chopt = Options()
chopt.add_argument('--headless')
chopt.add_argument('--no-sandbox')
chopt.add_argument('--disable-dev-shm-usage')
chopt.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=chopt)
driver.get("https://example.com/")
print("Started Chrome.")


class Runner(rpyc.Service):
    def on_connect(self, conn):
        print("New Connection.")
    
    def on_disconnect(self, conn):
        print("Client Disconnected.")
    
    def exposed_dxinfo(self, url):
        print(url)
        driver.get(url)
        print("Scrape done.")

        return driver.page_source
    
    def exposed_srvstop(self):
        t.close()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(Runner, port=3333)
    t.start()
