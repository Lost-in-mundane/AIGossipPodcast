import uvicorn
import os
import sys

# 打印Python版本和环境信息
print(f"Python 版本: {sys.version}")
print(f"运行路径: {os.getcwd()}")

# 移除环境变量清理逻辑

if __name__ == "__main__":
    print("准备启动FastAPI服务器...")
    
    # 配置服务器
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=5001,  # 使用统一的端口
        #reload=True,  # 开发模式下启用热重载
        #reload_dirs=["templates", "."],  # 监视这些目录的变化
        log_level="info"  # 设置日志级别
    ) 