#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 multitasking 库的 Python 3.8 兼容性问题
"""
import os
import sys
import subprocess
import importlib.util

print("=" * 60)
print("🔧 修复 multitasking 兼容性问题")
print("=" * 60)

# 方案一：降级安装兼容版本
print("\n📦 方案一：安装兼容版本 multitasking==0.0.9")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "multitasking==0.0.9"])
    print("✅ 成功安装兼容版本")
except Exception as e:
    print(f"❌ 安装失败: {e}")
    print("\n💡 尝试方案二...")

# 检查问题是否已解决
try:
    import multitasking
    print("✅ 问题已解决！")
    
    # 再测试 yfinance
    try:
        import yfinance
        print("✅ yfinance 也正常工作了！")
    except Exception as e:
        print(f"⚠️ 但 yfinance 仍有问题: {e}")
        
    print("\n🎉 现在可以运行:")
    print("   streamlit run app.py")
    
except Exception as e:
    print(f"\n❌ 问题仍在: {e}")
    
    # 方案二：直接修改文件
    print("\n🔧 尝试方案二：直接修复 multitasking 源代码...")
    
    try:
        # 找到 multitasking 位置
        spec = importlib.util.find_spec('multitasking')
        if spec and spec.origin:
            file_path = spec.origin
            print(f"📁 找到文件: {file_path}")
            
            # 读取并修复
            with open(file_path, 'r') as f:
                content = f.read()
            
            # 修复类型提示问题
            original = 'engine: Union[type[Thread], type[Process]]  # Execution engine'
            fixed = 'engine: None  # Execution engine (patched for Python 3.8)'
            
            if original in content:
                content = content.replace(original, fixed)
                
                # 备份并写入
                backup_path = file_path + '.backup'
                import shutil
                shutil.copy2(file_path, backup_path)
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ 文件已修复！备份在: {backup_path}")
                
                # 再次测试
                try:
                    import importlib
                    import multitasking
                    importlib.reload(multitasking)
                    print("✅ 修复成功！")
                except Exception as e:
                    print(f"❌ 仍然有问题: {e}")
            else:
                print("❌ 找不到需要修复的内容")
    
    except Exception as e:
        print(f"❌ 修复失败: {e}")
    
    print("\n💡 最后建议：使用 Python 3.9+ 或者只用 AkShare")

print("\n" + "=" * 60)
