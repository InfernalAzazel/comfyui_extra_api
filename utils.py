"""通用工具函数

提供图片扩展名常量、请求解析、文件名校验、注释路径生成、目录图片收集
以及统一响应封装。
"""

import os
from aiohttp.web import Request, json_response

ALLOWED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def get_temp_flag(request: Request) -> bool:
    """解析请求中的 temp 标志。"""
    return request.rel_url.query.get("temp", "false") == "true"


def validate_filename(filename: str) -> bool:
    """校验文件名，防止绝对路径与路径穿越。"""
    if not filename:
        return False
    if filename.startswith("/") or ".." in filename:
        return False
    return filename == os.path.basename(filename)


def get_annotated_file(filename: str, kind: str, is_temp: bool) -> str:
    """生成 ComfyUI 注释路径字符串。"""
    return f"{filename} [{'temp' if is_temp else kind}]"


def collect_images(folder: str):
    """遍历目录收集图片文件。"""
    images = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(ALLOWED_IMAGE_EXTENSIONS):
                images.append({"name": file, "full_path": os.path.join(root, file)})
    return images


def success_resp(**kwargs):
    """成功响应封装。

    参数:
        **kwargs: 需要包含在返回体中的数据。

    返回:
        JSON 响应，格式为: {"code": 200, "message": "success", ...}。
    """
    return json_response({"code": 200, "message": "success", **kwargs})


def error_resp(code, message, **kwargs):
    """错误响应封装。

    参数:
        code (int): 错误码。
        message (str): 错误信息。
        **kwargs: 需要包含在返回体中的额外数据。

    返回:
        JSON 响应，格式为: {"code": code, "message": message, ...}。
    """
    return json_response({"code": code, "message": message, **kwargs})