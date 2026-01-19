<#
.SYNOPSIS
快速启动 InvenTree 后端（单命令版本）

.DESCRIPTION
使用分号分隔的单命令快速启动后端服务，包含环境检查
#>

param(
    [string]$Port = "8000",
    [string]$MinPythonVersion = "3.8.0"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "快速启动 InvenTree 后端" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 环境检查
Write-Host "[环境检查] 正在检查系统环境..." -ForegroundColor Yellow

try {
    # 检查 Python
    $pythonVersionOutput = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python 未安装或不在 PATH 中"
    }
    $pythonVersion = ($pythonVersionOutput -split ' ')[1]
    
    # 比较版本
    $currentVersion = [version]$pythonVersion
    $requiredVersion = [version]$MinPythonVersion
    
    if ($currentVersion -lt $requiredVersion) {
        Write-Host "警告: Python 版本过低 ($pythonVersion < $MinPythonVersion)" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Python $pythonVersion" -ForegroundColor Green
    }
    
    # 检查 pip
    $null = pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "pip 不可用"
    }
    Write-Host "✓ pip 可用" -ForegroundColor Green
    
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 检查目录
$backendPath = Join-Path -Path $PSScriptRoot -ChildPath "src\backend\InvenTree"
if (-not (Test-Path -Path $backendPath)) {
    Write-Host "错误: 后端目录不存在: $backendPath" -ForegroundColor Red
    exit 1
}

Set-Location -Path $backendPath
Write-Host "工作目录: $PWD" -ForegroundColor Green
Write-Host ""

# 检查 manage.py
if (-not (Test-Path -Path "manage.py")) {
    Write-Host "错误: manage.py 不存在" -ForegroundColor Red
    exit 1
}

Write-Host "[执行中] 正在启动服务..." -ForegroundColor Yellow
Write-Host "端口: $Port" -ForegroundColor Green
Write-Host ""

# 使用分号分隔的命令执行所有操作
# 安装依赖；执行迁移；启动服务器
pip install -r ../requirements.txt; python manage.py makemigrations; python manage.py migrate; Write-Host "服务器启动完成: http://localhost:$Port" -ForegroundColor Green; python manage.py runserver 0.0.0.0:$Port