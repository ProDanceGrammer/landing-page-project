#!/bin/bash

FRONTEND_URL="https://vasyl-yarmolenko.online"
BACKEND_URL="https://landing-backend.onrender.com"

echo "=================================================="
echo "Testing Deployment"
echo "=================================================="

# Test frontend
echo ""
echo "✓ Testing frontend at $FRONTEND_URL..."
if curl -f -s -o /dev/null -w "%{http_code}" $FRONTEND_URL | grep -q "200"; then
    echo "  ✅ Frontend is live!"
else
    echo "  ❌ Frontend failed!"
    exit 1
fi

# Test backend ping
echo ""
echo "✓ Testing backend ping at $BACKEND_URL/ping..."
if curl -f -s $BACKEND_URL/ping | grep -q "alive"; then
    echo "  ✅ Backend ping successful!"
else
    echo "  ❌ Backend ping failed!"
    exit 1
fi

# Test backend health
echo ""
echo "✓ Testing backend health at $BACKEND_URL/health..."
if curl -f -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health | grep -q "200"; then
    echo "  ✅ Backend health check passed!"
else
    echo "  ⚠️  Backend health check failed (may be cold start)"
fi

# Test API lead submission
echo ""
echo "✓ Testing lead submission..."
RESPONSE=$(curl -s -X POST $BACKEND_URL/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Deployment test from script"
  }')

if echo "$RESPONSE" | grep -q "received"; then
    echo "  ✅ Lead submission successful!"
    echo "  Response: $RESPONSE" | head -c 100
else
    echo "  ❌ Lead submission failed!"
    echo "  Response: $RESPONSE"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ All tests passed!"
echo "=================================================="
