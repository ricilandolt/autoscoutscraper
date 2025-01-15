import zipfile
from seleniumwire import webdriver

class seleniumdriver:
        def __init__(self, PROXY_HOST, PROXY_PORT,PROXY_USER,PROXY_PASS):

            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
            background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                    }
                };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

            chrome_capabilities = {
                "browserName": "chrome",
                "version": "",
                "platform": "ANY",
                "javascriptEnabled": True,
                'applicationName': 'test1'
            }

            sw_options = {
                'addr': '0.0.0.0',
                'port': 8087,
                'auto_config': False,  
                'proxy': {
                    'http': 'http://{}:{}@{}:{}'.format(PROXY_USER,PROXY_PASS,PROXY_HOST,PROXY_PORT),
                    'http': 'http://{}:{}@{}:{}'.format(PROXY_USER,PROXY_PASS,PROXY_HOST,PROXY_PORT)
                }
            }

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--proxy-server=http://{}:{}'.format(PROXY_HOST,PROXY_PORT))
            chrome_options.add_argument('--ignore-certificate-errors')
            pluginfile = '/home/ec2-user/autoscoutscraper/proxy_auth_plugin.zip'

            with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
            chrome_options.add_extension(pluginfile)


            self.driver = webdriver.Remote("http://172.17.0.2:4444/wd/hub", desired_capabilities=chrome_capabilities,
                                    options=chrome_options , seleniumwire_options=sw_options)


