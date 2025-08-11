"""
通义千问API客户端包装器
"""
import os
import json
from typing import Dict, List, Any, Optional
import dashscope
from loguru import logger

# 从环境变量获取API密钥
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")


class QwenClient:
    """通义千问API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化通义千问客户端
        
        Args:
            api_key: DashScope API密钥，如果不提供则从环境变量DASHSCOPE_API_KEY获取
        """
        self.api_key = api_key or DASHSCOPE_API_KEY
        if not self.api_key:
            raise ValueError(
                "DashScope API key is required. "
                "Please set DASHSCOPE_API_KEY environment variable or pass api_key parameter."
            )
        dashscope.api_key = self.api_key
    
    def complete(self, prompt: str, model: str = "qwen-turbo") -> str:
        """
        调用通义千问完成API
        
        Args:
            prompt: 输入提示词
            model: 模型名称，默认为qwen-turbo
            
        Returns:
            生成的文本内容
            
        Raises:
            ValueError: 当API调用失败时
        """
        try:
            response = dashscope.Generation.call(
                model=model,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1,
                top_p=0.9,
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
            else:
                logger.error(f"QWen API call failed: {response}")
                raise ValueError(f"QWen API call failed with status {response.status_code}: {response.message}")
                
        except Exception as e:
            logger.error(f"Error calling QWen API: {e}")
            raise ValueError(f"Error calling QWen API: {e}")
    
    def chat(self, messages: List[Dict[str, str]], model: str = "qwen-turbo") -> Dict[str, Any]:
        """
        调用通义千问对话API
        
        Args:
            messages: 对话消息列表，格式为[{"role": "user", "content": "..."}, ...]
            model: 模型名称，默认为qwen-turbo
            
        Returns:
            包含响应内容的字典
            
        Raises:
            ValueError: 当API调用失败时
        """
        try:
            response = dashscope.Generation.call(
                model=model,
                messages=messages,
                max_tokens=4000,
                temperature=0.1,
                top_p=0.9,
                result_format='message'
            )
            
            if response.status_code == 200:
                # 返回与原有Cortex API相似的格式
                return {
                    "message": {
                        "content": [
                            {
                                "type": "text",
                                "text": response.output.choices[0].message.content
                            }
                        ]
                    },
                    "request_id": response.request_id
                }
            else:
                logger.error(f"QWen chat API call failed: {response}")
                raise ValueError(f"QWen chat API call failed with status {response.status_code}: {response.message}")
                
        except Exception as e:
            logger.error(f"Error calling QWen chat API: {e}")
            raise ValueError(f"Error calling QWen chat API: {e}")
    
    def validate_semantic_model(self, yaml_content: str) -> None:
        """
        使用通义千问验证语义模型YAML
        
        Args:
            yaml_content: YAML格式的语义模型内容
            
        Raises:
            ValueError: 当验证失败时
        """
        try:
            # 构造验证提示词
            validation_prompt = f"""
请检查以下YAML格式的语义模型是否正确：

```yaml
{yaml_content}
```

请检查以下方面：
1. YAML语法是否正确
2. 必需字段是否存在（name, description, tables等）
3. 数据类型是否合理
4. 表达式语法是否正确

如果发现错误，请详细说明错误内容。如果正确，请回复"验证通过"。
"""
            
            result = self.complete(validation_prompt, model="qwen-plus")
            
            # 简单的验证逻辑：如果返回内容包含"错误"、"Error"等关键词，则认为验证失败
            error_keywords = ["错误", "Error", "error", "错", "问题", "不正确", "invalid", "Invalid"]
            if any(keyword in result for keyword in error_keywords) and "验证通过" not in result:
                raise ValueError(result)
            
            logger.info("Semantic model validation passed")
            
        except Exception as e:
            logger.error(f"Semantic model validation failed: {e}")
            raise ValueError(f"Semantic model validation failed: {e}")


# 全局客户端实例
_qwen_client = None


def get_qwen_client() -> QwenClient:
    """获取全局通义千问客户端实例"""
    global _qwen_client
    if _qwen_client is None:
        _qwen_client = QwenClient()
    return _qwen_client


def qwen_complete(prompt: str, model: str = "qwen-turbo") -> str:
    """便捷函数：调用通义千问完成API"""
    client = get_qwen_client()
    return client.complete(prompt, model)


def qwen_chat(messages: List[Dict[str, str]], model: str = "qwen-turbo") -> Dict[str, Any]:
    """便捷函数：调用通义千问对话API"""
    client = get_qwen_client()
    return client.chat(messages, model)


def validate_semantic_model_with_qwen(yaml_content: str) -> None:
    """便捷函数：使用通义千问验证语义模型"""
    client = get_qwen_client()
    return client.validate_semantic_model(yaml_content)
