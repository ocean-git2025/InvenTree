<#
.SYNOPSIS
启动 InvenTree 后端服务

.DESCRIPTION
安装依赖、执行数据库迁移并启动开发服务器
支持版本检查和环境验证
#>

param(
    [switch]$SkipInstall,
    [switch]$SkipMigrate,
    [string]$Port = "8000",
    [string]$MinPythonVersion = "3.8.0",
    [string]$MinDjangoVersion = "4.2.0"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "InvenTree 后端启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 PowerShell 版本
Write-Host "[环境检查] PowerShell 版本..." -ForegroundColor Yellow
$psVersion = $PSVersionTable.PSVersion.ToString()
Write-Host "PowerShell 版本: $psVersion" -ForegroundColor Green

# 检查 Python 版本
Write-Host "[环境检查] Python 版本..." -ForegroundColor Yellow
try {
    $pythonVersionOutput = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python 未安装或不在 PATH 中"
    }
    
    $pythonVersion = ($pythonVersionOutput -split ' ')[1]
    Write-Host "Python 版本: $pythonVersion" -ForegroundColor Green
    
    # 比较版本
    $currentVersion = [version]$pythonVersion
    $requiredVersion = [version]$MinPythonVersion
    
    if ($currentVersion -lt $requiredVersion) {
        Write-Host "警告: Python 版本过低 (需要 $MinPythonVersion 或更高)" -ForegroundColor Red
        Write-Host "建议升级 Python 以避免兼容性问题" -ForegroundColor Yellow
    }
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
    exit 1
}

# 检查 pip
Write-Host "[环境检查] pip 可用性..." -ForegroundColor Yellow
try {
    $pipVersionOutput = pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "pip 未安装或不在 PATH 中"
    }
    $pipVersion = ($pipVersionOutput -split ' ')[1]
    Write-Host "pip 版本: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "警告: $_" -ForegroundColor Yellow
    Write-Host "尝试使用 python -m pip..." -ForegroundColor Yellow
    $pipVersionOutput = python -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: pip 不可用" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# 导航到后端目录
$backendPath = Join-Path -Path $PSScriptRoot -ChildPath "src\backend\InvenTree"

if (-not (Test-Path -Path $backendPath)) {
    Write-Host "错误: 后端目录不存在: $backendPath" -ForegroundColor Red
    exit 1
}

Set-Location -Path $backendPath
Write-Host "工作目录: $PWD" -ForegroundColor Green
Write-Host ""

# 检查 manage.py 是否存在
if (-not (Test-Path -Path "manage.py")) {
    Write-Host "错误: manage.py 不存在于当前目录" -ForegroundColor Red
    exit 1
}

Write-Host "项目目录结构验证通过" -ForegroundColor Green
Write-Host ""

# 安装依赖
if (-not $SkipInstall) {
    Write-Host "[1/4] 安装 Python 依赖..." -ForegroundColor Yellow
    pip install -r ../requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败!" -ForegroundColor Red
        exit 1
    }
    Write-Host "依赖安装完成" -ForegroundColor Green
    
    # 检查 Django 版本
    Write-Host "[环境检查] Django 版本..." -ForegroundColor Yellow
    try {
        $djangoVersionOutput = python -c "import django; print(django.get_version())" 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Django 未正确安装"
        }
        
        $djangoVersion = $djangoVersionOutput.Trim()
        Write-Host "Django 版本: $djangoVersion" -ForegroundColor Green
        
        # 比较版本
        $currentDjangoVersion = [version]$djangoVersion
        $requiredDjangoVersion = [version]$MinDjangoVersion
        
        if ($currentDjangoVersion -lt $requiredDjangoVersion) {
            Write-Host "警告: Django 版本过低 (需要 $MinDjangoVersion 或更高)" -ForegroundColor Red
            Write-Host "建议升级 Django 以避免兼容性问题" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "警告: 无法检查 Django 版本: $_" -ForegroundColor Yellow
    }
    
    } else {
    Write-Host "[1/4] 跳过依赖安装" -ForegroundColor Gray
}

Write-Host ""

Write-Host ""

# 执行数据库迁移
if (-not $SkipMigrate) {
    Write-Host "[2/4] 执行数据库迁移..." -ForegroundColor Yellow
    python manage.py makemigrations
    python manage.py migrate
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "数据库迁移失败!" -ForegroundColor Red
        exit 1
    }
    Write-Host "数据库迁移完成" -ForegroundColor Green
}
else {
    Write-Host "[2/4] 跳过数据库迁移" -ForegroundColor Gray
}

Write-Host ""

# 创建超级用户（可选）
$createSuperuser = Read-Host "是否创建超级用户? (y/n)"
if ($createSuperuser -eq "y" -or $createSuperuser -eq "Y") {
    Write-Host "创建超级用户..." -ForegroundColor Yellow
    python manage.py createsuperuser
}

Write-Host ""

# 启动开发服务器
Write-Host "[3/4] 启动开发服务器..." -ForegroundColor Yellow
Write-Host "服务器将运行在: http://localhost:$Port" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Gray
Write-Host ""

# 最后显示摘要
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务器启动完成!" -ForegroundColor Green
Write-Host "访问地址: http://localhost:$Port" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 0.0.0.0:$Port
