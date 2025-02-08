import asyncio
import os
from time import time
from typing import Dict, Any

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_fixed

# 加载环境变量
load_dotenv()


class LlamaClient:
    def __init__(self):
        """初始化 Llama API 客户端"""
        self.BASE_URL = os.getenv("LLAMA_PARSE_BASE_URL")
        self.API_KEY = os.getenv("LLAMA_PARSE_API_KEY")

        if not self.BASE_URL or not self.API_KEY:
            raise ValueError("请确保在 .env 文件中设置 LLAMA_PARSE_BASE_URL 和 LLAMA_PARSE_API_KEY")

    def _get_public_headers(self) -> Dict[str, str]:
        """生成公共头部信息"""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.API_KEY}",
        }

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
    async def upload_file_to_parse(self, fileName, binary, content_type) -> Dict[str, Any]:
        """
        上传文件到 Llama API 并提交解析任务。

        Parameters:
        - file: FastAPI 的 `UploadFile` 类型，包含要上传的文件。

        Returns:
        - Llama API 响应数据（含任务 ID 等信息）。
        """
        try:
            # 准备表单和文件数据
            form_data = {
                "job_timeout_in_seconds": 1200,
                "job_timeout_extra_time_per_page_in_seconds": 1200
            }
            files = {
                "file": (fileName, binary, content_type)  # 此处是文件字段
            }
            limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
            timeout = httpx.Timeout(None, connect=5.0)  # 设置时间限制
            async with httpx.AsyncClient(limits=limits, timeout=timeout, verify=False) as client:
                headers = self._get_public_headers()  # 假设这是获取请求头的方法
                response = await client.post(
                    url=f"{self.BASE_URL}api/v1/parsing/upload",
                    headers=headers,
                    data=form_data,  # 普通表单字段
                    files=files,  # 文件字段
                    timeout=30
                )
                # 检查响应状态
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=response.text)

                return response.json()
        except Exception as e:
            raise RuntimeError(f"文件上传失败: {str(e)}")

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
    async def poll_task_status(self, job_id: str, interval: int = 5) -> Dict[str, Any]:
        """
        轮询任务状态，直到任务完成或失败。

        Parameters:
        - job_id: 任务的 ID。
        - interval: 每次轮询之间的间隔，单位为秒（默认 5 秒）。

        Returns:
        - 最终的任务状态数据。
        """
        try:
            limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
            timeout = httpx.Timeout(None, connect=5.0)  # 设置时间限制
            async with httpx.AsyncClient(limits=limits, timeout=timeout, verify=False, ) as client:
                headers = self._get_public_headers()
                start_time = time()
                timeout_seconds = 600  # 超时10分钟
                while (time() - start_time) < timeout_seconds:
                    try:
                        response = await client.get(
                            f"{self.BASE_URL}api/v1/parsing/job/{job_id}",
                            headers=headers, timeout=30
                        )
                    except httpx.ConnectError as ce:
                        error_details = f"连接错误: {repr(ce)}"
                        print(error_details)
                        raise RuntimeError(f"轮询任务状态失败: {job_id} {error_details}") from ce
                    except httpx.HTTPError as e:
                        error_details = f"HTTP错误: {repr(e)}"
                        print(error_details)
                        raise RuntimeError(f"轮询任务状态失败: {job_id} {error_details}") from e

                    # 显示响应状态和内容以便调试
                    print(f"响应状态码: {response.status_code}, 响应内容: {response.text}")

                    if response.status_code not in (200,):
                        error_msg = f"非预期状态码: {response.status_code}, 响应内容: {response.text}"
                        print(error_msg)
                        raise RuntimeError(error_msg)

                    try:
                        result = response.json()
                    except Exception as json_err:
                        error_msg = f"解析响应JSON失败: {repr(json_err)}，响应内容: {response.text}"
                        print(error_msg)
                        raise RuntimeError(error_msg) from json_err

                    status = result.get("status")
                    print(f"轮询状态: {status} (任务 ID: {job_id})")

                    if status in ["SUCCESS", "ERROR", "CANCELLED"]:
                        return result
                    else:
                        # 状态为 None 或其他情况，等待 interval 秒后再次尝试
                        print(f"任务状态未就绪，等待 {interval} 秒后重试...")
                        await asyncio.sleep(interval)
            # 如果超时未完成，返回超时信息
            timeout_msg = f"轮询超时（{timeout_seconds}秒）未获取最终状态"
            print(timeout_msg)
            return {"status": "failed", "error": timeout_msg}

        except Exception as e:
            error_info = f"轮询任务状态失败: {job_id}, 异常详情: {repr(e)}"
            print(error_info)
            raise RuntimeError(error_info) from e

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
    async def get_markdown_result(self, job_id: str) -> str:
        """
        获取任务的 Markdown 解析结果。

        Parameters:
        - job_id: 任务的 ID。

        Returns:
        - Markdown 格式的任务结果。
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = self._get_public_headers()

                response = await client.get(f"{self.BASE_URL}api/v1/parsing/job/{job_id}/result/raw/markdown",
                                            headers=headers)

                if response.status_code != 200:
                    print("No 200")
                    raise HTTPException(status_code=response.status_code, detail=response.text)
                return response.text  # 返回 Markdown 内容
        except Exception as e:

            raise RuntimeError(f"获取 Markdown 结果失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(LlamaClient().poll_task_status('f24442ac-1142-4163-aa20-d8b02a737f72'))
