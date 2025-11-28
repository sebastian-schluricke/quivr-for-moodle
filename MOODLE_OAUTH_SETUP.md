# Moodle OAuth Integration - Setup and Testing Guide

## Status: Backend Implementation Complete ✅

The Moodle OAuth backend integration is now complete and the routes are successfully loaded in the API.

## Implemented Endpoints

### 1. Authorization Endpoint
- **URL**: `POST /sync/moodle/authorize`
- **Purpose**: Initiates the OAuth flow
- **Authentication**: Requires Quivr JWT token
- **Parameters**:
  - `name`: Friendly name for this Moodle connection (e.g., "Eckener Schule Moodle")
  - `moodle_url`: Optional - Moodle instance URL (defaults to env variable)
- **Returns**: `{"authorization_url": "https://..."}`

### 2. OAuth Callback Endpoint
- **URL**: `GET /sync/moodle/oauth2callback`
- **Purpose**: Handles OAuth callback from Moodle
- **Parameters**: Automatically handled (code, state)
- **Returns**: Success page

### 3. Courses Endpoint (Placeholder)
- **URL**: `GET /sync/moodle/courses`
- **Purpose**: Lists Moodle courses (Web Services implementation pending)
- **Authentication**: Requires Quivr JWT token
- **Status**: Placeholder implementation

## Next Steps

### Step 1: Update Moodle Redirect URI ⚠️ REQUIRED

You need to update the Redirect URI in your Moodle OAuth provider configuration:

1. Go to Moodle → Site administration → Server → OAuth provider
2. Find your "quivr-client" configuration
3. **Change Redirect URL from**:
   ```
   http://localhost:3000/auth/callback/moodle
   ```
   **To**:
   ```
   http://localhost:5050/sync/moodle/oauth2callback
   ```
4. Save the configuration

**Why?** The redirect now goes directly to the backend instead of the frontend.

### Step 2: Test Backend OAuth Flow

Once the Redirect URI is updated, you can test the backend:

#### Option A: Test with Swagger UI

1. Open: http://localhost:5050/docs
2. Find the `/sync/moodle/authorize` endpoint under "Sync" tag
3. Click "Try it out"
4. You'll need a valid JWT token (get it by logging into Quivr frontend first)
5. Click "Execute" and copy the `authorization_url`
6. Open that URL in browser to test OAuth flow

#### Option B: Test with curl (requires JWT token)

```bash
# Get JWT token first by logging into Quivr frontend
# Then use it in the Authorization header

curl -X POST "http://localhost:5050/sync/moodle/authorize" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Moodle Connection",
    "moodle_url": "https://moodle.draftdev.com"
  }'
```

Expected response:
```json
{
  "authorization_url": "https://moodle.draftdev.com/local/oauth/login.php?client_id=quivr-client&response_type=code&redirect_uri=http://localhost:5050/sync/moodle/oauth2callback&scope=user_info&state=..."
}
```

#### Option C: Manual Test Flow

1. Get JWT token from Quivr frontend (login and check browser DevTools → Application → Local Storage)
2. Call authorize endpoint to get authorization URL
3. Open authorization URL in browser
4. Login to Moodle
5. You'll be redirected to `http://localhost:5050/sync/moodle/oauth2callback`
6. Backend will exchange code for token and store credentials
7. You should see a success page

### Step 3: Verify Token Storage

After successful OAuth flow, check the database:

```sql
-- In Supabase SQL Editor
SELECT
  id,
  user_id,
  provider,
  email,
  status,
  created_at
FROM syncs_user
WHERE provider = 'Moodle';
```

You should see an entry with:
- `provider`: "Moodle"
- `email`: Your Moodle email
- `status`: "SYNCED"
- `credentials`: JSON with access_token (encrypted)

## Environment Variables

The following environment variables are configured in `.env`:

```bash
MOODLE_URL=https://moodle.draftdev.com
MOODLE_CLIENT_ID=quivr-client
MOODLE_CLIENT_SECRET=740819f32be69f129d6e27aada9137c393679804e189de7d
BACKEND_URL=http://localhost:5050
```

## OAuth Endpoints Used

- **Authorization**: `https://moodle.draftdev.com/local/oauth/login.php`
- **Token**: `https://moodle.draftdev.com/local/oauth/token.php`
- **User Info**: `https://moodle.draftdev.com/local/oauth/user_info.php`

## Future Work

### Phase 2: Moodle Web Services Integration
- Implement course listing endpoint
- Add endpoint to fetch course content
- Create brain from course functionality

### Phase 3: Frontend Integration
- Add Moodle connection button to Quivr UI
- Display Moodle courses in course selection dialog
- Show sync status and connection management

### Phase 4: Multi-Tenancy Support
- Allow users to connect multiple Moodle instances
- School-specific Moodle URL configuration
- Support for different Moodle versions

## Troubleshooting

### Authorization Code Expired
**Symptom**: Error during token exchange: "authorization code has expired"
**Solution**: Normal behavior - authorization codes are only valid 60-120 seconds. Just try the flow again.

### Redirect URI Mismatch
**Symptom**: Error from Moodle: "redirect_uri mismatch"
**Solution**: Make sure the Redirect URI in Moodle exactly matches: `http://localhost:5050/sync/moodle/oauth2callback`

### Not Authenticated
**Symptom**: Error: "Not authenticated" when calling /sync/moodle/authorize
**Solution**: You need a valid Quivr JWT token. Login to Quivr frontend first, then use that token in the Authorization header.

## API Documentation

Full API documentation is available at: http://localhost:5050/docs

Look for the "Sync" tag to find all Moodle-related endpoints.
