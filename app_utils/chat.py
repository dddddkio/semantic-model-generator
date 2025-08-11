import json
import re
from typing import Any, Dict

import requests
import streamlit as st
from snowflake.connector import SnowflakeConnection

from semantic_model_generator.qwen_utils.qwen_client import qwen_chat

API_ENDPOINT = "https://{HOST}/api/v2/cortex/analyst/message"


@st.cache_data(ttl=60, show_spinner=False)
def send_message(
    _conn: SnowflakeConnection, semantic_model: str, messages: list[dict[str, str]]
) -> Dict[str, Any]:
    """
    使用通义千问替代Cortex Analyst进行对话
    Args:
        _conn: SnowflakeConnection (已不使用，保留以兼容原有接口)
        messages: 对话消息列表
        semantic_model: 语义模型的YAML字符串

    Returns: 通义千问的响应结果，格式保持与原Cortex API一致
    """
    try:
        # 构建适合通义千问的对话消息
        qwen_messages = []
        
        # 添加系统消息，包含语义模型信息
        system_message = f"""你是一个数据分析助手，专门帮助用户分析和查询数据。

以下是当前的数据语义模型：
```yaml
{semantic_model}
```

请基于这个语义模型回答用户的问题。如果用户询问数据相关的问题，请：
1. 理解用户的业务需求
2. 基于语义模型中的表、字段和关系给出建议
3. 如果需要，可以提供相应的SQL查询示例
4. 保持回答的专业性和准确性

请用中文回答。"""
        
        qwen_messages.append({"role": "system", "content": system_message})
        
        # 转换用户消息格式
        for msg in messages:
            if msg["role"] == "user":
                # 提取文本内容
                if isinstance(msg["content"], list):
                    text_content = ""
                    for content_item in msg["content"]:
                        if content_item.get("type") == "text":
                            text_content += content_item.get("text", "")
                else:
                    text_content = str(msg["content"])
                qwen_messages.append({"role": "user", "content": text_content})
            elif msg["role"] == "analyst" or msg["role"] == "assistant":
                # 处理助手消息
                if isinstance(msg["content"], list):
                    text_content = ""
                    for content_item in msg["content"]:
                        if content_item.get("type") == "text":
                            text_content += content_item.get("text", "")
                else:
                    text_content = str(msg["content"])
                qwen_messages.append({"role": "assistant", "content": text_content})
        
        # 调用通义千问API
        response = qwen_chat(qwen_messages, model="qwen-plus")
        return response
        
    except Exception as e:
        # 如果通义千问调用失败，返回错误信息
        raise ValueError(f"通义千问API调用失败: {str(e)}")


# 保留原有的Cortex API调用作为备用（已注释掉，可根据需要启用）
def send_message_cortex(
    _conn: SnowflakeConnection, semantic_model: str, messages: list[dict[str, str]]
) -> Dict[str, Any]:
    """
    原有的Cortex Analyst API调用（备用）
    """
    request_body = {
        "messages": messages,
        "semantic_model": semantic_model,
    }

    if st.session_state["sis"]:
        import _snowflake

        resp = _snowflake.send_snow_api_request(  # type: ignore
            "POST",
            "/api/v2/cortex/analyst/message",
            {},
            {},
            request_body,
            {},
            30000,
        )
        if resp["status"] < 400:
            json_resp: Dict[str, Any] = json.loads(resp["content"])
            return json_resp
        else:
            err_body = json.loads(resp["content"])
            if "message" in err_body:
                error_msg = re.sub(
                    r"\s*Please use https://github\.com/Snowflake-Labs/semantic-model-generator.*",
                    "",
                    err_body["message"],
                )
                raise ValueError(error_msg)
            raise ValueError(err_body)

    else:
        host = st.session_state.host_name
        resp = requests.post(
            API_ENDPOINT.format(
                HOST=host,
            ),
            json=request_body,
            headers={
                "Authorization": f'Snowflake Token="{_conn.rest.token}"',  # type: ignore[union-attr]
                "Content-Type": "application/json",
            },
        )
        if resp.status_code < 400:
            json_resp: Dict[str, Any] = resp.json()
            return json_resp
        else:
            err_body = json.loads(resp.text)
            if "message" in err_body:
                error_msg = re.sub(
                    r"\s*Please use https://github\.com/Snowflake-Labs/semantic-model-generator.*",
                    "",
                    err_body["message"],
                )
                raise ValueError(error_msg)
            raise ValueError(err_body)
