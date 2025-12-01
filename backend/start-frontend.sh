#!/bin/bash
# Start Frontend

cd "$(dirname "$0")/../frontend"

echo "Starting Frontend..."
echo "Starting Next.js on http://0.0.0.0:3000 (accessible from Windows)"

# Start frontend on 0.0.0.0 WITHOUT turbo (turbo causes compilation issues)
npx next dev -H 0.0.0.0

