from snowflake.connector import SnowflakeConnection

from app_utils.chat import send_message
from semantic_model_generator.qwen_utils.qwen_client import validate_semantic_model_with_qwen


def load_yaml(yaml_path: str) -> str:
    """
    Load local yaml file into str.

    yaml_path: str The absolute path to the location of your yaml file. Something like path/to/your/file.yaml.
    """
    with open(yaml_path) as f:
        yaml_str = f.read()
    return yaml_str


def validate(yaml_str: str, conn: SnowflakeConnection) -> None:
    """
    使用通义千问验证语义模型YAML格式和内容的正确性
    
    yaml_str: YAML格式的语义模型内容
    conn: SnowflakeConnection（保留以兼容原有接口，但实际不使用）
    """
    try:
        # 使用通义千问进行语义模型验证
        validate_semantic_model_with_qwen(yaml_str)
    except Exception as e:
        # 如果通义千问验证失败，抛出异常
        raise ValueError(f"语义模型验证失败: {str(e)}")


def validate_with_cortex(yaml_str: str, conn: SnowflakeConnection) -> None:
    """
    原有的Cortex Analyst验证方法（备用）
    """
    dummy_request = [
        {"role": "user", "content": [{"type": "text", "text": "SMG app validation"}]}
    ]
    send_message(conn, yaml_str, dummy_request)


def validate_from_local_path(yaml_path: str, conn: SnowflakeConnection) -> None:
    yaml_str = load_yaml(yaml_path)
    validate(yaml_str, conn)
