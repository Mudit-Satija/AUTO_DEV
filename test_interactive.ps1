# Test script for interactive validation endpoint

# Test 1: Initial question
Write-Host "==== TEST 1: Initial Question ====" -ForegroundColor Cyan
$body1 = @{
    prompt = "I want to build a real-time chat application"
    conversation = @()
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/validate-interactive" `
  -Method POST -Body $body1 -ContentType "application/json" -ErrorAction Continue

Write-Host "Status: $($response1.status)" -ForegroundColor Green
Write-Host "Question: $($response1.current_question)" -ForegroundColor Yellow
Write-Host "Context: $($response1.context)" -ForegroundColor Yellow
Write-Host ""

# Test 2: Backend answer
Write-Host "==== TEST 2: After Backend Selection ====" -ForegroundColor Cyan
$body2 = @{
    prompt = "I want to build a real-time chat application"
    conversation = @(
        @{ role = "assistant"; content = "I'd like to help you flesh out your idea." },
        @{ role = "user"; content = "FastAPI sounds good" }
    )
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/validate-interactive" `
  -Method POST -Body $body2 -ContentType "application/json" -ErrorAction Continue

Write-Host "Status: $($response2.status)" -ForegroundColor Green
Write-Host "Question: $($response2.current_question)" -ForegroundColor Yellow
Write-Host ""

# Test 3: Backend + Database
Write-Host "==== TEST 3: After Database Selection ====" -ForegroundColor Cyan
$body3 = @{
    prompt = "I want to build a real-time chat application"
    conversation = @(
        @{ role = "assistant"; content = "Backend question" },
        @{ role = "user"; content = "FastAPI" },
        @{ role = "assistant"; content = "Database question" },
        @{ role = "user"; content = "PostgreSQL" }
    )
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/validate-interactive" `
  -Method POST -Body $body3 -ContentType "application/json" -ErrorAction Continue

Write-Host "Status: $($response3.status)" -ForegroundColor Green
Write-Host "Question: $($response3.current_question)" -ForegroundColor Yellow
Write-Host ""

# Test 4: Complete stack (should finalize)
Write-Host "==== TEST 4: Full Stack - Final Validation ====" -ForegroundColor Cyan
$body4 = @{
    prompt = "I want to build a real-time chat application"
    conversation = @(
        @{ role = "assistant"; content = "Backend?" },
        @{ role = "user"; content = "FastAPI" },
        @{ role = "assistant"; content = "Database?" },
        @{ role = "user"; content = "PostgreSQL" },
        @{ role = "assistant"; content = "Deployment?" },
        @{ role = "user"; content = "AWS" }
    )
} | ConvertTo-Json

$response4 = Invoke-RestMethod -Uri "http://localhost:8000/validate-interactive" `
  -Method POST -Body $body4 -ContentType "application/json" -ErrorAction Continue

Write-Host "Status: $($response4.status)" -ForegroundColor Green
Write-Host "Project Type: $($response4.project_type)" -ForegroundColor Green
Write-Host "Complexity: $($response4.complexity)" -ForegroundColor Green
Write-Host "Alignment Score: $($response4.alignment_score)" -ForegroundColor Green
Write-Host "Feedback: $($response4.feedback)" -ForegroundColor Yellow
Write-Host ""

Write-Host "✅ All tests completed!" -ForegroundColor Green
