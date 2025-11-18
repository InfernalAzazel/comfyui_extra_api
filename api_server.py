"""ComfyUI 额外 API 服务器

提供输出/输入图片的查询与删除接口。
"""

import os
from aiohttp.web import Request
from server import PromptServer
import folder_paths
from .utils import get_temp_flag, validate_filename, get_annotated_file, collect_images, success_resp, error_resp

routes = PromptServer.instance.routes

@routes.get("/extra-api/v1/output-images")
async def list_output_images(request: Request):
    """获取输出图片列表。

    接口:
        GET /extra-api/v1/output-images

    查询参数:
        temp (str): "true"/"false"。为 true 时列出临时输出目录（由 PreviewImage 节点生成），否则列出正式输出目录。

    返回:
        JSON 响应，字段:
            images (List[Dict]): 图片列表，包含 name 与 full_path。

    异常:
        500: 服务内部错误。
    """
    try:
        is_temp = get_temp_flag(request)
        folder = (
            folder_paths.get_temp_directory()
            if is_temp
            else folder_paths.get_output_directory()
        )
        return success_resp(images=collect_images(folder))
    except Exception as e:
        return error_resp(500, str(e))


@routes.delete("/extra-api/v1/output-images/{filename}")
async def delete_output_image(request: Request):
    """删除输出图片。

    接口:
        DELETE /extra-api/v1/output-images/{filename}

    路径参数:
        filename (str): 文件名。

    查询参数:
        temp (str): "true"/"false"。为 true 时删除临时输出目录文件，否则删除正式输出目录文件。

    安全:
        禁止绝对路径与路径穿越（包含前导 "/" 或 ".."）。

    返回:
        200: 删除成功。
        400: 参数非法或缺失。
        404: 文件不存在。
        500: 服务内部错误。
    """
    try:
        filename = request.match_info.get("filename")
        if filename is None:
            return error_resp(400, "filename is required")

        if not validate_filename(filename):
            return error_resp(400, "invalid filename")

        is_temp = get_temp_flag(request)
        annotated_file = get_annotated_file(filename, "output", is_temp)
        if not folder_paths.exists_annotated_filepath(annotated_file):
            return error_resp(404, f"file {filename} not found")

        filepath = folder_paths.get_annotated_filepath(annotated_file)
        os.remove(filepath)
        return success_resp()
    except Exception as e:
        return error_resp(500, str(e))


@routes.delete("/extra-api/v1/input-images/{filename}")
async def delete_input_image(request: Request):
    """删除输入图片。

    接口:
        DELETE /extra-api/v1/input-images/{filename}

    路径参数:
        filename (str): 文件名。

    查询参数:
        temp (str): "true"/"false"。为 true 时删除临时输入目录文件，否则删除正式输入目录文件。

    安全:
        禁止绝对路径与路径穿越（包含前导 "/" 或 ".."）。

    返回:
        200: 删除成功。
        400: 参数非法或缺失。
        404: 文件不存在。
        500: 服务内部错误。
    """
    try:
        filename = request.match_info.get("filename")
        if filename is None:
            return error_resp(400, "filename is required")

        if not validate_filename(filename):
            return error_resp(400, "invalid filename")

        is_temp = get_temp_flag(request)
        annotated_file = get_annotated_file(filename, "input", is_temp)
        if not folder_paths.exists_annotated_filepath(annotated_file):
            return error_resp(404, f"file {filename} not found")

        filepath = folder_paths.get_annotated_filepath(annotated_file)
        os.remove(filepath)
        return success_resp()
    except Exception as e:
        return error_resp(500, str(e))


def run_comfyui_extra_api():
    """额外 API 启动提示。

    由主程序调用以启动额外 API 时输出启动日志。
    """
    print("extra API server started")
