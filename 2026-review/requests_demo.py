"""
requests 常用功能学习脚本。

说明：
- 本文件演示 requests 的常见用法：GET、POST、参数、JSON、Header、Session、超时、异常处理、文件下载。
- 示例接口主要使用 https://httpbin.org，适合学习和调试 HTTP 请求。
"""

from pathlib import Path
import requests

OUTPUT_DIR = Path(__file__).resolve().parent / "assets" / "output"


def ensure_output_dir() -> Path:
    """
    确保输出目录存在。

    Returns:
        Path: 输出目录路径。

    逻辑说明：
        - 下载文件示例需要写入本地目录。
        - 统一在函数入口处创建目录，避免重复判断。
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def basic_get_example() -> None:
    """
    基础 GET 请求示例。

    Returns:
        None

    逻辑说明：
        - 请求 `https://httpbin.org/get`。
        - 通过 `status_code` 与 `response.json()` 查看响应。
    """
    url = "https://httpbin.org/get"
    response = requests.get(url, timeout=10)

    print("\n=== basic_get_example ===")
    print("status:", response.status_code)
    print("url:", response.url)
    print("origin ip:", response.json().get("origin"))


def get_with_params_and_headers() -> None:
    """
    GET 携带 query 参数和请求头示例。

    Returns:
        None

    逻辑说明：
        - `params` 会自动拼接到 URL query string。
        - `headers` 可模拟客户端信息（如 User-Agent）。
    """
    url = "https://httpbin.org/get"
    params = {"keyword": "python", "page": 1}
    headers = {"User-Agent": "PythonReview-RequestsDemo/1.0"}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    data = response.json()

    print("\n=== get_with_params_and_headers ===")
    print("final url:", response.url)
    print("args:", data.get("args"))
    print("user-agent:", data.get("headers", {}).get("User-Agent"))


def post_json_example() -> None:
    """
    POST JSON 请求示例。

    Returns:
        None

    逻辑说明：
        - 使用 `json=` 传参时，requests 会自动设置 `Content-Type: application/json`。
        - 适用于调用 REST API 的常见场景。
    """
    url = "https://httpbin.org/post"
    payload = {"name": "alice", "score": 95}

    response = requests.post(url, json=payload, timeout=10)
    data = response.json()

    print("\n=== post_json_example ===")
    print("status:", response.status_code)
    print("json sent:", data.get("json"))


def post_form_example() -> None:
    """
    POST 表单请求示例（application/x-www-form-urlencoded）。

    Returns:
        None

    逻辑说明：
        - 使用 `data=` 发送表单字段。
        - 常见于传统登录接口、表单提交接口。
    """
    url = "https://httpbin.org/post"
    form = {"username": "demo_user", "password": "not-a-real-password"}

    response = requests.post(url, data=form, timeout=10)
    data = response.json()

    print("\n=== post_form_example ===")
    print("status:", response.status_code)
    print("form sent:", data.get("form"))


def timeout_and_exception_example() -> None:
    """
    超时与异常处理示例。

    Returns:
        None

    逻辑说明：
        - `timeout` 建议在生产代码中始终设置，避免请求无限等待。
        - 使用 `RequestException` 统一捕获 requests 常见异常。
        - `raise_for_status()` 可将 4xx/5xx 转成 HTTPError。
    """
    print("\n=== timeout_and_exception_example ===")
    try:
        # 该接口会延迟响应：delay/3 代表延迟约 3 秒
        response = requests.get("https://httpbin.org/delay/3", timeout=1)
        response.raise_for_status()
        print("request succeeded unexpectedly:", response.status_code)
    except requests.Timeout:
        print("timeout captured: request took too long")
    except requests.RequestException as exc:
        print("request failed:", exc)


def session_cookie_example() -> None:
    """
    Session 与 Cookie 持久化示例。

    Returns:
        None

    逻辑说明：
        - `Session` 会在多个请求之间复用连接并保存 Cookie。
        - 先调用 /cookies/set 设置 cookie，再调用 /cookies 读取。
    """
    print("\n=== session_cookie_example ===")
    with requests.Session() as session:
        session.get("https://httpbin.org/cookies/set?token=abc123", timeout=10)
        response = session.get("https://httpbin.org/cookies", timeout=10)
        print("cookies from server:", response.json().get("cookies"))


def download_file_example() -> Path:
    """
    文件下载示例（流式下载）。

    Returns:
        Path: 下载后的本地文件路径。

    逻辑说明：
        - `stream=True` 可边读边写，适合大文件，避免一次性占用大量内存。
        - 使用 `iter_content` 分块写入文件。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "httpbin_image.png"

    url = "https://httpbin.org/image/png"
    with requests.get(url, stream=True, timeout=15) as response:
        response.raise_for_status()
        with output_path.open("wb") as f:
            # 以 8KB 为单位写入磁盘
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print("\n=== download_file_example ===")
    print("saved:", output_path)
    return output_path


def run_all_requests_demos() -> None:
    """
    串行执行所有 requests 示例。

    Returns:
        None

    逻辑说明：
        - 作为统一学习入口，一次运行可看到常见请求场景。
        - 若网络不可用，部分请求会报错，可先检查代理/网络连接。
    """
    basic_get_example()
    get_with_params_and_headers()
    post_json_example()
    post_form_example()
    timeout_and_exception_example()
    session_cookie_example()
    download_file_example()

    print("\nAll requests demos finished.")


if __name__ == "__main__":
    run_all_requests_demos()
