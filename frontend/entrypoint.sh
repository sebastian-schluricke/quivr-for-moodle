#!/bin/sh
# Runtime environment variable injection for Next.js
# This script replaces placeholder values in the built JavaScript files
# with actual environment variables at container startup time.

set -e

echo "==> Injecting runtime environment variables..."

# Define placeholder values (these are used during build)
# Format: PLACEHOLDER=ACTUAL_ENV_VAR_NAME
REPLACEMENTS="
__RUNTIME_NEXT_PUBLIC_BACKEND_URL__:NEXT_PUBLIC_BACKEND_URL
__RUNTIME_NEXT_PUBLIC_SUPABASE_URL__:NEXT_PUBLIC_SUPABASE_URL
__RUNTIME_NEXT_PUBLIC_SUPABASE_ANON_KEY__:NEXT_PUBLIC_SUPABASE_ANON_KEY
__RUNTIME_NEXT_PUBLIC_FRONTEND_URL__:NEXT_PUBLIC_FRONTEND_URL
__RUNTIME_NEXT_PUBLIC_AUTH_MODES__:NEXT_PUBLIC_AUTH_MODES
"

# Find all JS files in .next directory
find /app/.next -name "*.js" -type f | while read file; do
    for replacement in $REPLACEMENTS; do
        placeholder=$(echo "$replacement" | cut -d: -f1)
        env_var=$(echo "$replacement" | cut -d: -f2)
        env_value=$(eval echo "\$$env_var")

        if [ -n "$env_value" ]; then
            # Replace placeholder with actual value
            sed -i "s|$placeholder|$env_value|g" "$file" 2>/dev/null || true
        fi
    done
done

echo "==> Environment variables injected:"
echo "    NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL:-not set}"
echo "    NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL:-not set}"
echo "    NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY:+***set***}"
echo "    NEXT_PUBLIC_FRONTEND_URL=${NEXT_PUBLIC_FRONTEND_URL:-not set}"
echo "    NEXT_PUBLIC_AUTH_MODES=${NEXT_PUBLIC_AUTH_MODES:-not set}"

echo "==> Starting Next.js server..."
exec node server.js
