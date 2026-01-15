<#
.SYNOPSIS
快速启动 InvenTree 后端（单命令版本）

.DESCRIPTION
使用分号分隔的单命令快速启动后端服务
#>

param(
    [string]$Port = "8000"
)

Write-Host "快速启动 InvenTree 后端..." -ForegroundColor Cyan

# 导航到后端目录
Set-Location -Path "src\backend\InvenTree"

# 使用分号分隔的命令执行所有操作
# 安装依赖；执行迁移；启动服务器
pip install -r ../requirements.txt; python manage.py makemigrations; python manage.py migrate; python manage.py runserver 0.0.0.0:$Port