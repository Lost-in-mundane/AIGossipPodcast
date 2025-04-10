import uvicorn
import os
import sys

# 打印Python版本和环境信息
print(f"Python 版本: {sys.version}")
print(f"运行路径: {os.getcwd()}")

# 移除环境变量清理逻辑

if __name__ == "__main__":
    print("准备启动FastAPI服务器...")
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=5001,
        reload=True,  # 保持重载以便开发
        reload_dirs=["templates", "."],
        log_level="info"
    ) 