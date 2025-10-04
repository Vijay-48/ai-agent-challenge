#!/bin/bash

echo "=========================================="
echo "Project Verification Script"
echo "=========================================="
echo ""

# Check required files
echo "1. Checking required files..."
files=("agent.py" "requirements.txt" "README.md" "tests/test_parser.py" "custom_parsers/icici_parser.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file MISSING"
        exit 1
    fi
done
echo ""

# Check dependencies
echo "2. Checking dependencies..."
if pip list | grep -q "langgraph"; then
    echo "   ✅ langgraph installed"
else
    echo "   ❌ langgraph not installed"
    exit 1
fi
echo ""

# Run tests
echo "3. Running tests..."
if pytest tests/test_parser.py -v --tb=short > /dev/null 2>&1; then
    echo "   ✅ All tests passed"
else
    echo "   ❌ Tests failed"
    exit 1
fi
echo ""

# Verify parser works
echo "4. Verifying parser..."
if python quick_test.py > /dev/null 2>&1; then
    echo "   ✅ Parser works correctly"
else
    echo "   ❌ Parser verification failed"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ ALL CHECKS PASSED!"
echo "=========================================="
echo ""
echo "Project is ready for submission."
echo ""
echo "To run the agent:"
echo "  python agent.py --target icici"
echo ""
echo "To run tests:"
echo "  pytest tests/test_parser.py -v"
echo ""

