<#
.SYNOPSIS
Setup script for Stock Threshold Plugin

.DESCRIPTION
This script installs dependencies and runs database migrations for the Stock Threshold Plugin
#>

param(
    [string]$BackendPath = "d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend"
)

$ErrorActionPreference = "Stop"

try {
    Write-Host "=== Stock Threshold Plugin Setup ===`n" -ForegroundColor Cyan

    # Change to backend directory
    Write-Host "Changing to backend directory: $BackendPath" -ForegroundColor Yellow
    Set-Location -Path $BackendPath -ErrorAction Stop

    # Check if requirements.txt exists
    if (-not (Test-Path "requirements.txt")) {
        throw "requirements.txt not found in $BackendPath"
    }

    # Install main dependencies
    Write-Host "`n[1/3] Installing main dependencies..." -ForegroundColor Yellow
    $installResult = pip install -r requirements.txt 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install main dependencies: $($installResult -join '\n')"
    }
    Write-Host "Main dependencies installed successfully!" -ForegroundColor Green

    # Install dev dependencies if available
    if (Test-Path "requirements-dev.txt") {
        Write-Host "`n[2/3] Installing development dependencies..." -ForegroundColor Yellow
        $devInstallResult = pip install -r requirements-dev.txt 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to install development dependencies: $($devInstallResult -join '\n')"
            Write-Warning "Continuing with setup..."
        } else {
            Write-Host "Development dependencies installed successfully!" -ForegroundColor Green
        }
    } else {
        Write-Host "`n[2/3] requirements-dev.txt not found, skipping dev dependencies..." -ForegroundColor Yellow
    }

    # Run migrations
    Write-Host "`n[3/3] Running database migrations..." -ForegroundColor Yellow
    $migrateResult = python manage.py migrate 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Database migration failed: $($migrateResult -join '\n')"
    }
    Write-Host "Database migrations completed successfully!" -ForegroundColor Green

    Write-Host "`n=== Setup Complete! ===`n" -ForegroundColor Cyan
    Write-Host "You can now start the development server:"
    Write-Host "  python manage.py runserver`n" -ForegroundColor Green

    exit 0
} catch {
    Write-Host "`n=== Setup Failed ===`n" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
