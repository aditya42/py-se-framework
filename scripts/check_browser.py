from shutil import which

browsers = {"chrome": which("google-chrome") or which("chrome"), "firefox": which("firefox")}
available = [name for name, path in browsers.items() if path]
print("Detected browsers:", ", ".join(available) if available else "none on PATH")
print("Selenium Manager downloads/resolves a compatible driver when the browser is installed.")
