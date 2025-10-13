import requests

ENDPOINTS = [
    ("Home", "http://127.0.0.1:8000/", [200]),
    ("Login", "http://127.0.0.1:8000/comptes/login/", [200, 302]),
    ("Allauth login", "http://127.0.0.1:8000/auth/login/", [200, 302]),
    ("Projects (public API)", "http://127.0.0.1:8000/projects/", [200, 301, 302, 404]),
    ("Notifications API", "http://127.0.0.1:8000/devis/api/notifications/", [200, 401, 403]),
]

def main():
    print("Running smoke test...")
    for name, url, ok_codes in ENDPOINTS:
        try:
            resp = requests.get(url, allow_redirects=True, timeout=5)
            status = resp.status_code
            result = "OK" if status in ok_codes else "FAIL"
            print(f"- {name}: {status} {result} -> {url}")
        except Exception as e:
            print(f"- {name}: ERROR {e} -> {url}")

if __name__ == "__main__":
    main()

