import base64

from fastapi import FastAPI, Body
from pydantic import BaseModel
from pydantic import Field

from backend.api.LLamaParseAPI import LlamaClient
from backend.llm.Client import LLM
from backend.llm.llmUtils import generateMessage
from backend.llm.prompts.prompts import bpPrompt
from backend.model.Result import Result, ResultStatus

app = FastAPI()


# 定义数据模型，用于验证接收到的数据结构
class FileObject(BaseModel):
    content_type: str = Field(..., alias='$content-type')  # 将 `$content-type` 映射到 content_type
    content: str = Field(..., alias='$content')  # 将 `$content` 映射到 content


class Upload(BaseModel):
    fileName: str
    File: FileObject


@app.post("/upload")
async def upload_file(up: Upload = Body(...)):
    decoded_content = base64.b64decode(up.File.content)
    # 提交任务
    client = LlamaClient()
    result = await client.upload_file_to_parse(up.fileName, decoded_content, up.File.content_type)
    jobid = result.get('id')
    print(f'''{up.fileName} 获得llama jobId :{jobid}''')
    jobResult = await client.poll_task_status(jobid)
    if jobResult.get('status').upper() != "SUCCESS":
        return Result(code=ResultStatus.FAILURE_CODE, message="文档解析失败", data=None)
    else:
        markdown = await client.get_markdown_result(jobid)
        openaiClient = LLM(model='gpt-4o-2024-11-20')
        summary = openaiClient.getCompletionAnswerWithNoSysPrompt(generateMessage('user', bpPrompt(markdown)))
        return Result(code=ResultStatus.SUCCESS_CODE, message=summary, data=None)
