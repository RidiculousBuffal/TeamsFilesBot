# Teams Channel 文件解析机器人示例
> 本示例旨在跑通利用**power automate**从Teams 的 channel 中获取文件-自动回复的全流程——商业计划书模板为例

# 内容准备
- 一个MS office 账号
-  `OPENAI_API_KEY`
- `OPENAI_BASE_URL`

# 搭建automate工作流
## 1.找到Teams对应的Team 和 Channel
![img.png](pics%2Fimg.png)
## 2.获取MessageId
![img_1.png](pics%2Fimg_1.png)
## 3.获取附件内容
新建一个变量填写附件的内容数组,整个的消息格式json示例如下:
```json
{
  "@odata.context": "",
  "id": "",
  "replyToId": "",
  "etag": "",
  "messageType": "",
  "createdDateTime": "",
  "lastModifiedDateTime": "",
  "lastEditedDateTime": null,
  "deletedDateTime": null,
  "subject": "",
  "summary": null,
  "chatId": null,
  "importance": "normal",
  "locale": "en-us",
  "webUrl": "",
  "policyViolation": null,
  "eventDetail": null,
  "from": {
    "application": null,
    "device": null,
    "user": {
      "@odata.type": "",
      "id": "",
      "displayName": "",
      "userIdentityType": "",
      "tenantId": ""
    }
  },
  "body": {
    "contentType": "html",
    "content": "<p>213</p><attachment id=\"1578081d-c531-4888-909d-04d2db4ce594\"></attachment>",
    "plainTextContent": "213"
  },
  "channelIdentity": {
    "teamId": "",
    "channelId": ""
  },
  "attachments": [
    {
      "id": "1578081d-c531-4888-909d-04d2db4ce594",
      "contentType": "reference",
      "contentUrl": "https://xxx.sharepoint.com/sites/xxx/Documents partages/xxx/xxx.doc",
      "content": null,
      "name": "xxx.doc",
      "thumbnailUrl": null,
      "teamsAppId": null
    }
  ],
  "mentions": [],
  "reactions": [],
  "messageLink": "",
  "threadType": "channel",
  "teamId": "",
  "channelId": ""
}

```
![img_3.png](pics%2Fimg_3.png)
![img_2.png](pics%2Fimg_2.png)
## 4.新建filePath变量记录文件路径
![img_4.png](pics%2Fimg_4.png)
## 5.对attachment数组进行循环
![img_5.png](pics%2Fimg_5.png)
## 6.提取出每个attachment的filePath
由于sharepoint在拿文件的时候sitepath和filepath是分开的,举例:
```txt
"contentUrl": "https://xxx.sharepoint.com/sites/xxx/Documents partages/xxx/xxx.doc" # 这个是原始的url
"sitepath":"https://xxx.sharepoint.com/sites/xxx
"filepath":/Documents partages/xxx/xxx.doc
```
filepath把前半部分清空即可
![img_6.png](pics%2Fimg_6.png)
## 7.通过sharepoint拿到文件
![img_8.png](pics%2Fimg_8.png)
![img_7.png](pics%2Fimg_7.png)
## 8.向服务端发送请求
这里需要注意sharepoint发来的文件都是base64编码后的结果,所以在服务端先进行了解码(本来想传multiPartFormData的,没折腾出来😭)
![img_10.png](pics%2Fimg_10.png)
![img_9.png](pics%2Fimg_9.png)
## 9.解析Json
![img_11.png](pics%2Fimg_11.png)
## 10.发送给前台
![img_12.png](pics%2Fimg_12.png)
## 整体概览
![img_13.png](pics%2Fimg_13.png)
# 整体效果
![img_14.png](pics%2Fimg_14.png)
# 修改提示词
- [prompts.py](backend%2Fllm%2Fprompts%2Fprompts.py)
# 启动服务端
```bash
cp .env.example .env
python.exe -m uvicorn main:app --reload 
```