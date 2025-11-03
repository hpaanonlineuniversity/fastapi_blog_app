#!/bin/bash

# Simple login script
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user02@example.com",
    "password": "password"
  }'