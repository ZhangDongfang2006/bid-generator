#!/bin/bash

# 投标文件生成系统 - 启动脚本

cd /Users/zhangdongfang/workspace/bid-generator

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 启动 Streamlit
streamlit run app.py --server.port 8501
