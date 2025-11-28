import os
from uuid import UUID

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from quivr_api.logger import get_logger
from quivr_api.middlewares.auth import AuthBearer, get_current_user
from quivr_api.modules.sync.dto.inputs import (
    SyncsUserInput,
    SyncsUserStatus,
)
from quivr_api.modules.sync.service.sync_service import SyncService, SyncUserService
from quivr_api.modules.user.entity.user_identity import UserIdentity

# Initialize logger
logger = get_logger(__name__)

# Initialize sync service
sync_service = SyncService()
sync_user_service = SyncUserService()

# Initialize API router
moodle_sync_router = APIRouter()

# Moodle Configuration
DEFAULT_MOODLE_SERVICE = "moodle_mobile_app"


@moodle_sync_router.post(
    "/sync/moodle/authorize",
    dependencies=[Depends(AuthBearer())],
    tags=["Sync"],
)
def authorize_moodle_post(
    request: Request,
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Initialize Moodle authorization (POST from frontend).
    Returns the URL to the connection form.

    Args:
        request (Request): The request object.
        current_user (UserIdentity): The current authenticated user.

    Returns:
        dict: Authorization URL pointing to the Moodle connection form.
    """
    # Get the backend URL
    backend_url = os.getenv("BACKEND_URL", "http://localhost:5050")

    # Return URL to the form page
    return {
        "authorization_url": f"{backend_url}/sync/moodle/form"
    }


@moodle_sync_router.get(
    "/sync/moodle/form",
    tags=["Sync"],
)
def authorize_moodle_get():
    """
    Serve the Moodle connection form (GET request from popup).
    The Moodle URL is configured via MOODLE_URL environment variable.

    Returns:
        HTMLResponse: A simple HTML form to collect Moodle credentials (username + password only).
    """
    from fastapi.responses import HTMLResponse

    # Get the backend URL for form submission
    backend_url = os.getenv("BACKEND_URL", "http://localhost:5050")

    # Get Moodle URL from environment - this is the only Moodle instance allowed
    moodle_url = os.getenv("MOODLE_URL")
    if not moodle_url:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html lang="de">
            <head>
                <meta charset="UTF-8">
                <title>Fehler - Moodle nicht konfiguriert</title>
                <style>
                    body { font-family: sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
                    .error { background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 8px; }
                    h2 { color: #c62828; margin-top: 0; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>Moodle nicht konfiguriert</h2>
                    <p>Die Moodle-URL wurde nicht in der Serverkonfiguration hinterlegt.</p>
                    <p>Bitte kontaktieren Sie den Administrator.</p>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

    # Get frontend URL for postMessage origin check
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Return a simple HTML form with only username and password
    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Moodle Verbindung</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 500px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .form-container {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h2 {{
                margin-top: 0;
                color: #333;
            }}
            .info-box {{
                background: #e3f2fd;
                border: 1px solid #2196f3;
                padding: 12px;
                border-radius: 4px;
                margin-bottom: 20px;
                font-size: 14px;
                color: #1565c0;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                color: #555;
                font-weight: 500;
            }}
            input {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                box-sizing: border-box;
            }}
            input:focus {{
                outline: none;
                border-color: #4CAF50;
            }}
            button {{
                width: 100%;
                padding: 12px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
            }}
            button:hover {{
                background: #45a049;
            }}
            button:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
            .error {{
                color: #f44336;
                margin-top: 10px;
                display: none;
            }}
            .success {{
                color: #4CAF50;
                margin-top: 10px;
                display: none;
            }}
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>Moodle Verbindung einrichten</h2>
            <div class="info-box">
                Verbindung zu: <strong>{moodle_url}</strong>
            </div>
            <form id="moodleForm">
                <div class="form-group">
                    <label for="username">Benutzername:</label>
                    <input type="text" id="username" name="username" required autocomplete="username">
                </div>
                <div class="form-group">
                    <label for="password">Passwort:</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password">
                </div>
                <button type="submit">Verbinden</button>
                <div class="error" id="error"></div>
                <div class="success" id="success">Erfolgreich verbunden! Dieses Fenster schließt sich automatisch...</div>
            </form>
        </div>

        <script>
            document.getElementById('moodleForm').addEventListener('submit', async (e) => {{
                e.preventDefault();

                const form = e.target;
                const button = form.querySelector('button');
                const errorDiv = document.getElementById('error');
                const successDiv = document.getElementById('success');

                errorDiv.style.display = 'none';
                successDiv.style.display = 'none';
                button.disabled = true;
                button.textContent = 'Verbinde...';

                const formData = {{
                    username: form.username.value,
                    password: form.password.value
                }};

                const token = await getAuthToken();
                if (!token) {{
                    errorDiv.textContent = 'Authentifizierung fehlgeschlagen. Bitte neu einloggen.';
                    errorDiv.style.display = 'block';
                    button.disabled = false;
                    button.textContent = 'Verbinden';
                    return;
                }}

                try {{
                    const response = await fetch('{backend_url}/sync/moodle/connect', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + token
                        }},
                        body: JSON.stringify(formData)
                    }});

                    if (!response.ok) {{
                        const error = await response.json();
                        throw new Error(error.detail || 'Verbindung fehlgeschlagen');
                    }}

                    successDiv.style.display = 'block';
                    setTimeout(() => {{
                        window.close();
                    }}, 2000);
                }} catch (error) {{
                    errorDiv.textContent = error.message;
                    errorDiv.style.display = 'block';
                    button.disabled = false;
                    button.textContent = 'Verbinden';
                }}
            }});

            // Request auth token from parent window using postMessage (cross-origin safe)
            function getAuthToken() {{
                console.log('[Popup] Requesting auth token from parent...');
                return new Promise((resolve) => {{
                    if (!window.opener) {{
                        console.error('[Popup] No parent window found');
                        resolve('');
                        return;
                    }}

                    console.log('[Popup] Parent window exists, setting up message listener');

                    // Set up message listener for response
                    const messageHandler = (event) => {{
                        console.log('[Popup] Received message:', event.origin, event.data);

                        // Accept messages from configured frontend URL
                        const allowedOrigin = '{frontend_url}';
                        if (!event.origin.startsWith(allowedOrigin.split('://')[0] + '://' + allowedOrigin.split('://')[1].split(':')[0])) {{
                            console.log('[Popup] Rejected message from unauthorized origin');
                            return;
                        }}

                        if (event.data.type === 'AUTH_TOKEN_RESPONSE') {{
                            console.log('[Popup] Received auth token response, token length:', event.data.token?.length || 0);
                            window.removeEventListener('message', messageHandler);
                            resolve(event.data.token || '');
                        }}
                    }};

                    window.addEventListener('message', messageHandler);

                    console.log('[Popup] Sending AUTH_TOKEN_REQUEST to parent');
                    // Request token from parent
                    window.opener.postMessage({{ type: 'AUTH_TOKEN_REQUEST' }}, '{frontend_url}');

                    // Timeout after 5 seconds
                    setTimeout(() => {{
                        console.log('[Popup] Token request timed out after 5 seconds');
                        window.removeEventListener('message', messageHandler);
                        resolve('');
                    }}, 5000);
                }});
            }}
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


class MoodleConnectInput(BaseModel):
    """Input model for Moodle connection (simplified - only credentials)."""
    username: str
    password: str


@moodle_sync_router.post(
    "/sync/moodle/connect",
    dependencies=[Depends(AuthBearer())],
    tags=["Sync"],
)
def connect_moodle(
    request: Request,
    connection_input: MoodleConnectInput,
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Connect to Moodle using username and password.
    The Moodle URL is configured via MOODLE_URL environment variable.

    Args:
        request (Request): The request object.
        connection_input (MoodleConnectInput): Connection details (username, password only).
        current_user (UserIdentity): The current authenticated user.

    Returns:
        dict: Success message with connection details.
    """
    # Get Moodle URL from environment - this is the only Moodle instance allowed
    moodle_url = os.getenv("MOODLE_URL")
    if not moodle_url:
        raise HTTPException(
            status_code=500,
            detail="Moodle URL not configured. Please set MOODLE_URL environment variable."
        )

    logger.debug(
        f"Connecting to Moodle for user: {current_user.id}, url: {moodle_url}"
    )

    # Build token endpoint URL
    token_endpoint = f"{moodle_url.rstrip('/')}/login/token.php"

    # Prepare token request
    token_data = {
        "username": connection_input.username,
        "password": connection_input.password,
        "service": DEFAULT_MOODLE_SERVICE,
    }

    try:
        # Request token from Moodle
        logger.info(f"Requesting token from: {token_endpoint}")
        token_response = requests.post(token_endpoint, data=token_data, timeout=10)
        token_response.raise_for_status()
        token_json = token_response.json()

        # Check for errors in response
        if "error" in token_json:
            error_msg = token_json.get("error", "Unknown error")
            logger.error(f"Moodle token error: {error_msg}")
            raise HTTPException(
                status_code=401,
                detail=f"Moodle authentication failed: {error_msg}"
            )

        # Extract token
        wstoken = token_json.get("token")
        if not wstoken:
            logger.error(f"No token in response: {token_json}")
            raise HTTPException(
                status_code=500,
                detail="Failed to obtain token from Moodle"
            )

        logger.info(f"Successfully obtained token for user: {current_user.id}")

        # Get user info from Moodle Web Services
        webservice_endpoint = f"{moodle_url.rstrip('/')}/webservice/rest/server.php"
        webservice_params = {
            "wstoken": wstoken,
            "wsfunction": "core_webservice_get_site_info",
            "moodlewsrestformat": "json"
        }

        user_info_response = requests.get(webservice_endpoint, params=webservice_params, timeout=10)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        # Check for API errors
        if isinstance(user_info, dict) and "exception" in user_info:
            logger.error(f"Moodle API error: {user_info}")
            raise HTTPException(
                status_code=500,
                detail=f"Moodle API error: {user_info.get('message', 'Unknown error')}"
            )

        user_email = user_info.get("useremail", connection_input.username)
        user_fullname = user_info.get("fullname", connection_input.username)
        moodle_user_id = user_info.get("userid")
        site_name = user_info.get("sitename", "Moodle")

        logger.info(f"Retrieved Moodle user info for: {user_email} (userid: {moodle_user_id})")

        # Auto-generate connection name: "Moodle - Site Name (username)"
        connection_name = f"Moodle - {site_name} ({connection_input.username})"
        logger.info(f"Auto-generated connection name: {connection_name}")

        # Create sync user entry
        sync_user_input = SyncsUserInput(
            name=connection_name,
            user_id=str(current_user.id),
            provider="Moodle",
            credentials={"wstoken": wstoken},
            state={},
            additional_data={
                "moodle_url": moodle_url,
                "username": connection_input.username,
                "fullname": user_fullname,
                "user_id": moodle_user_id,  # Store Moodle user ID
            },
            email=user_email,
            status=str(SyncsUserStatus.SYNCED),
        )

        created_sync = sync_user_service.create_sync_user(sync_user_input)

        logger.info(f"Moodle sync created successfully for user: {current_user.id}")

        return {
            "message": "Successfully connected to Moodle",
            "sync_id": created_sync.get("id") if isinstance(created_sync, dict) else created_sync.id,
            "moodle_url": moodle_url,
            "email": user_email,
            "fullname": user_fullname,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Moodle: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Moodle: {str(e)}"
        )


@moodle_sync_router.get(
    "/sync/moodle/courses",
    dependencies=[Depends(AuthBearer())],
    tags=["Sync"],
)
def get_moodle_courses(
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Get list of Moodle courses for the current user.

    Args:
        current_user (UserIdentity): The current authenticated user.

    Returns:
        dict: A dictionary containing the list of courses.
    """
    logger.debug(f"Getting Moodle courses for user: {current_user.id}")

    # Get sync user credentials - get the most recent Moodle sync (highest ID)
    sync_users = sync_user_service.get_syncs_user(str(current_user.id))
    moodle_syncs = [sync for sync in sync_users if sync.get("provider") == "Moodle"]
    moodle_sync = max(moodle_syncs, key=lambda x: x.get("id", 0)) if moodle_syncs else None

    if not moodle_sync:
        raise HTTPException(
            status_code=404, detail="No Moodle connection found. Please connect first."
        )

    # Get web services token from credentials
    credentials = moodle_sync.get("credentials", {})
    logger.debug(f"Retrieved credentials: {credentials}, type: {type(credentials)}")

    # Handle both dict and string cases
    if isinstance(credentials, str):
        import json
        credentials = json.loads(credentials)

    wstoken = credentials.get("wstoken") if isinstance(credentials, dict) else None
    logger.debug(f"Extracted wstoken: {wstoken}")

    if not wstoken:
        raise HTTPException(
            status_code=401, detail=f"Invalid credentials. Please reconnect to Moodle. Debug: credentials={credentials}"
        )

    # Get moodle_url and user_id from additional_data
    additional_data = moodle_sync.get("additional_data", {})
    moodle_url = additional_data.get("moodle_url")
    user_id = additional_data.get("user_id")

    if not moodle_url:
        raise HTTPException(
            status_code=500, detail="Moodle URL not found. Please reconnect."
        )

    if not user_id:
        raise HTTPException(
            status_code=500, detail="User ID not found. Please reconnect."
        )

    try:
        # Call Moodle Web Services API to get user's enrolled courses
        webservice_endpoint = f"{moodle_url.rstrip('/')}/webservice/rest/server.php"
        webservice_params = {
            "wstoken": wstoken,
            "wsfunction": "core_enrol_get_users_courses",
            "moodlewsrestformat": "json",
            "userid": str(user_id)  # Must be a valid user ID
        }

        logger.debug(f"Calling Moodle API with params: {webservice_params}")
        logger.debug(f"Endpoint: {webservice_endpoint}")

        courses_response = requests.get(webservice_endpoint, params=webservice_params, timeout=10)
        logger.info(f"Courses response status: {courses_response.status_code}")
        logger.debug(f"Courses response: {courses_response.text[:500]}")
        courses_response.raise_for_status()
        courses = courses_response.json()

        # Check for error in response
        if isinstance(courses, dict) and "exception" in courses:
            logger.error(f"Moodle API error: {courses}")
            raise HTTPException(
                status_code=500,
                detail=f"Moodle API error: {courses.get('message', 'Unknown error')}"
            )

        logger.info(f"Retrieved {len(courses)} courses for user: {current_user.id}")

        return {
            "courses": courses,
            "moodle_url": moodle_url,
            "sync_id": moodle_sync.get("id"),
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching courses from Moodle: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch courses from Moodle: {str(e)}"
        )


@moodle_sync_router.get(
    "/sync/moodle/{sync_id}/files",
    dependencies=[Depends(AuthBearer())],
    tags=["Sync"],
)
def get_moodle_course_files(
    sync_id: int,
    course_id: int,
    current_user: UserIdentity = Depends(get_current_user),
):
    """
    Get files/materials from a specific Moodle course.

    Args:
        sync_id (int): The sync user ID.
        course_id (int): The Moodle course ID.
        current_user (UserIdentity): The current authenticated user.

    Returns:
        dict: A dictionary containing the course files and materials.
    """
    logger.debug(f"Getting files for Moodle course {course_id} for user: {current_user.id}")

    # Get sync user credentials - find the specific sync by ID
    sync_users = sync_user_service.get_syncs_user(str(current_user.id))
    moodle_sync = next(
        (sync for sync in sync_users if sync.get("provider") == "Moodle" and sync.get("id") == sync_id), None
    )

    if not moodle_sync:
        raise HTTPException(
            status_code=404, detail="No Moodle connection found."
        )

    # Get web services token from credentials
    credentials = moodle_sync.get("credentials", {})
    wstoken = credentials.get("wstoken")

    if not wstoken:
        raise HTTPException(
            status_code=401, detail="Invalid credentials. Please reconnect to Moodle."
        )

    # Get moodle_url from additional_data
    additional_data = moodle_sync.get("additional_data", {})
    moodle_url = additional_data.get("moodle_url")

    if not moodle_url:
        raise HTTPException(
            status_code=500, detail="Moodle URL not found. Please reconnect."
        )

    try:
        # Call Moodle Web Services API to get course contents
        webservice_endpoint = f"{moodle_url.rstrip('/')}/webservice/rest/server.php"
        webservice_params = {
            "wstoken": wstoken,
            "wsfunction": "core_course_get_contents",
            "moodlewsrestformat": "json",
            "courseid": course_id
        }

        contents_response = requests.get(webservice_endpoint, params=webservice_params, timeout=10)
        logger.info(f"Course contents response status: {contents_response.status_code}")
        logger.debug(f"Course contents response: {contents_response.text[:500]}")
        contents_response.raise_for_status()
        contents = contents_response.json()

        # Check for error in response
        if isinstance(contents, dict) and "exception" in contents:
            logger.error(f"Moodle API error: {contents}")
            raise HTTPException(
                status_code=500,
                detail=f"Moodle API error: {contents.get('message', 'Unknown error')}"
            )

        # Transform Moodle content structure to include ALL content types
        sections_data = []
        total_files = 0

        for section in contents:
            section_id = section.get("id", 0)
            section_name = section.get("name", "Unnamed Section")
            section_summary = section.get("summary", "")

            modules_data = []

            # Process modules (activities/resources) in the section
            for module in section.get("modules", []):
                module_id = module.get("id", 0)
                module_name = module.get("name", "Unnamed Item")
                module_type = module.get("modname", "")  # resource, page, label, forum, etc.
                module_url = module.get("url", "")
                module_description = module.get("description", "")

                # Extract files if present
                module_files = []
                if "contents" in module:
                    for content in module.get("contents", []):
                        if content.get("type") == "file":
                            module_files.append({
                                "filename": content.get("filename", ""),
                                "fileurl": content.get("fileurl", ""),
                                "filesize": content.get("filesize", 0),
                                "mimetype": content.get("mimetype", ""),
                                "timecreated": content.get("timecreated", 0),
                                "timemodified": content.get("timemodified", 0),
                            })
                            total_files += 1

                modules_data.append({
                    "id": module_id,
                    "name": module_name,
                    "type": module_type,
                    "url": module_url,
                    "description": module_description,
                    "files": module_files,
                    "visible": module.get("visible", 1),
                    "modplural": module.get("modplural", ""),
                })

            sections_data.append({
                "id": section_id,
                "name": section_name,
                "summary": section_summary,
                "section_number": section.get("section", 0),
                "visible": section.get("visible", 1),
                "modules": modules_data,
            })

        logger.info(f"Retrieved {len(sections_data)} sections with {total_files} files from course {course_id}")

        return {
            "course_id": course_id,
            "sections": sections_data,
            "total_sections": len(sections_data),
            "total_files": total_files,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching course contents from Moodle: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch course contents: {str(e)}"
        )
