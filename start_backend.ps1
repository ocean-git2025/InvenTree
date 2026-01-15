<#
.SYNOPSIS
启动 InvenTree 后端服务

.DESCRIPTION
安装依赖、执行数据库迁移并启动开发服务器
#>

param(
    [switch]$SkipInstall,
    [switch]$SkipMigrate,
    [string]$Port = "8000"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "InvenTree 后端启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 导航到后端目录
$backendPath = Join-Path -Path $PSScriptRoot -ChildPath "src\backend\InvenTree"
Set-Location -Path $backendPath

Write-Host "当前目录: $PWD" -ForegroundColor Green
Write-Host ""

# 安装依赖
if (-not $SkipInstall) {
    Write-Host "[1/3] 安装 Python 依赖..." -ForegroundColor Yellow
    pip install -r ../requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败!" -ForegroundColor Red
        exit 1
    }
    Write-Host "依赖安装完成" -ForegroundColor Green
}
else {
    Write-Host "[1/3] 跳过依赖安装" -ForegroundColor Gray
}

Write-Host ""

# 执行数据库迁移
if (-not $SkipMigrate) {
    Write-Host "[2/3] 执行数据库迁移..." -ForegroundColor Yellow
    python manage.py makemigrations
    python manage.py migrate
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "数据库迁移失败!" -ForegroundColor Red
        exit 1
    }
    Write-Host "数据库迁移完成" -ForegroundColor Green
}
else {
    Write-Host "[2/3] 跳过数据库迁移" -ForegroundColor Gray
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
Write-Host "[3/3] 启动开发服务器..." -ForegroundColor Yellow
Write-Host "服务器将运行在: http://localhost:$Port" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Gray
Write-Host ""

python manage.py runserver 0.0.0.0:$Port
