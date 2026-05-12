import json
import requests
from config import BASE_URL, TIMEOUT


class ApiError(Exception):
    pass


class PostApiService:
    @staticmethod
    def _headers() -> dict:
        return {"Content-Type": "application/json", "Accept": "application/json"}

    @staticmethod
    def _handle_response(resp: requests.Response) -> dict:
        if resp.status_code == 422:
            try:
                detail = resp.json()
                errors = detail.get("errors", {})
                if isinstance(errors, dict):
                    lines = []
                    for field, msgs in errors.items():
                        line = ", ".join(msgs) if isinstance(msgs, list) else str(msgs)
                        lines.append(f"  • {field}: {line}")
                    msg = "\n".join(lines) if lines else json.dumps(detail, indent=2)
                else:
                    msg = json.dumps(detail, indent=2)
            except Exception:
                msg = resp.text
            raise ApiError(f"Validasi gagal (422):\n{msg}")

        if not resp.ok:
            raise ApiError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        if resp.status_code == 204 or not resp.content:
            return {"success": True}

        return resp.json()

    def get_all_posts(self) -> dict:
        try:
            print(f"[DEBUG] Memanggil: {BASE_URL}/posts")
            resp = requests.get(
                f"{BASE_URL}/posts",
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            print(f"[DEBUG] Status: {resp.status_code}")
            result = self._handle_response(resp)
            print(f"[DEBUG] Jumlah data: {len(result.get('data', []))}")
            return result
        except requests.exceptions.ConnectionError:
            raise ApiError("Koneksi gagal. Periksa jaringan Anda.")
        except requests.exceptions.Timeout:
            raise ApiError(f"Request timeout setelah {TIMEOUT} detik.")

    def get_post(self, post_id: int) -> dict:
        try:
            resp = requests.get(
                f"{BASE_URL}/posts/{post_id}",
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            return self._handle_response(resp)
        except requests.exceptions.ConnectionError:
            raise ApiError("Koneksi gagal. Periksa jaringan Anda.")
        except requests.exceptions.Timeout:
            raise ApiError(f"Request timeout setelah {TIMEOUT} detik.")

    def create_post(self, payload: dict) -> dict:
        try:
            resp = requests.post(
                f"{BASE_URL}/posts",
                json=payload,
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            return self._handle_response(resp)
        except requests.exceptions.ConnectionError:
            raise ApiError("Koneksi gagal. Periksa jaringan Anda.")
        except requests.exceptions.Timeout:
            raise ApiError(f"Request timeout setelah {TIMEOUT} detik.")

    def update_post(self, post_id: int, payload: dict) -> dict:
        try:
            resp = requests.put(
                f"{BASE_URL}/posts/{post_id}",
                json=payload,
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            return self._handle_response(resp)
        except requests.exceptions.ConnectionError:
            raise ApiError("Koneksi gagal. Periksa jaringan Anda.")
        except requests.exceptions.Timeout:
            raise ApiError(f"Request timeout setelah {TIMEOUT} detik.")

    def delete_post(self, post_id: int) -> dict:
        try:
            resp = requests.delete(
                f"{BASE_URL}/posts/{post_id}",
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            return self._handle_response(resp)
        except requests.exceptions.ConnectionError:
            raise ApiError("Koneksi gagal. Periksa jaringan Anda.")
        except requests.exceptions.Timeout:
            raise ApiError(f"Request timeout setelah {TIMEOUT} detik.")