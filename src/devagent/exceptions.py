# 项目所有异常的基类，后面所有自定义错误都继承它
class DevAgentBaseError(Exception):
    """DevAgent 项目基础异常类"""
    pass

# 大模型调用相关的错误
class LLMRequestError(DevAgentBaseError):
    """大模型请求失败异常"""
    pass

class ToolCallError(DevAgentBaseError):
    """工具请求异常"""
    pass