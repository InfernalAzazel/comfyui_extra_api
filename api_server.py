import logging
import os
import traceback
from aiohttp.web import Request, json_response
from server import PromptServer
import folder_paths
routes = PromptServer.instance.routes


def success_resp(**kwargs):
    return json_response({"code": 200, "message": "success", **kwargs})


def error_resp(code, message, **kwargs):
    return json_response({"code": code, "message": message, **kwargs})

@routes.get("/comfyapi/v1/output-images")
async def get_output_images(request: Request):
    try:
        is_temp = request.rel_url.query.get("temp", "false") == "true"
        folder = (
            folder_paths.get_temp_directory()
            if is_temp
            else folder_paths.get_output_directory()
        )
        # iterate through the folder and get the list of images
        images = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                    image = {"name": file, "full_path": os.path.join(root, file)}
                    images.append(image)
        return success_resp(images=images)
    except Exception as e:
        return error_resp(500, str(e))


@routes.delete("/comfyapi/v1/output-images/{filename}")
async def delete_output_images(request: Request):
    try:
        filename = request.match_info.get("filename")
        if filename is None:
            return error_resp(400, "filename is required")

        if filename[0] == "/" or ".." in filename:
            return error_resp(400, "invalid filename")

        is_temp = request.rel_url.query.get("temp", "false") == "true"
        annotated_file = f"{filename} [{'temp' if is_temp else 'output'}]"
        if not folder_paths.exists_annotated_filepath(annotated_file):
            return error_resp(404, f"file {filename} not found")

        filepath = folder_paths.get_annotated_filepath(annotated_file)
        os.remove(filepath)
        return success_resp()
    except Exception as e:
        return error_resp(500, str(e))


@routes.delete("/comfyapi/v1/input-images/{filename}")
async def delete_input_images(request: Request):
    try:
        filename = request.match_info.get("filename")
        if filename is None:
            return error_resp(400, "filename is required")

        if filename[0] == "/" or ".." in filename:
            return error_resp(400, "invalid filename")

        is_temp = request.rel_url.query.get("temp", "false") == "true"
        annotated_file = f"{filename} [{'temp' if is_temp else 'input'}]"
        if not folder_paths.exists_annotated_filepath(annotated_file):
            return error_resp(404, f"file {filename} not found")

        filepath = folder_paths.get_annotated_filepath(annotated_file)
        os.remove(filepath)
        return success_resp()
    except Exception as e:
        return error_resp(500, str(e))


def run_comfyui_extra_api():
    print("extra API server started")
