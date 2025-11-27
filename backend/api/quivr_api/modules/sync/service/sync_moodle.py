"""
Moodle sync service for processing course content.
"""
import html2text
import requests
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Union
from uuid import UUID

from quivr_api.logger import get_logger
from quivr_api.modules.dependencies import BaseService
from quivr_api.modules.sync.entity.sync_models import SyncFile

logger = get_logger(__name__)


class SyncMoodleService:
    """Service for handling Moodle-specific sync operations."""

    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.body_width = 0  # Don't wrap text

    def convert_html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML content to Markdown.

        Args:
            html_content: HTML string to convert

        Returns:
            Markdown string
        """
        try:
            if not html_content or html_content.strip() == "":
                return ""
            markdown = self.html_converter.handle(html_content)
            return markdown.strip()
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {e}")
            return html_content  # Return original if conversion fails

    def get_course_contents(
        self, moodle_url: str, wstoken: str, course_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get course contents from Moodle API.

        Args:
            moodle_url: Moodle instance URL
            wstoken: Web services token
            course_id: Course ID

        Returns:
            List of sections with modules
        """
        endpoint = f"{moodle_url.rstrip('/')}/webservice/rest/server.php"
        params = {
            "wstoken": wstoken,
            "wsfunction": "core_course_get_contents",
            "moodlewsrestformat": "json",
            "courseid": course_id,
        }

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            contents = response.json()

            # Check for API errors
            if isinstance(contents, dict) and "exception" in contents:
                error_msg = contents.get("message", "Unknown error")
                logger.error(f"Moodle API error: {error_msg}")
                raise Exception(f"Moodle API error: {error_msg}")

            return contents
        except Exception as e:
            logger.error(f"Error fetching course contents: {e}")
            raise

    def process_section_content(
        self, section: Dict[str, Any], course_name: str
    ) -> Dict[str, Any]:
        """
        Process a course section and convert to structured data.

        Args:
            section: Section data from Moodle API
            course_name: Name of the course

        Returns:
            Processed section data with markdown content
        """
        section_name = section.get("name", "Unnamed Section")
        section_summary = section.get("summary", "")

        # Convert HTML summary to Markdown
        summary_markdown = self.convert_html_to_markdown(section_summary)

        # Build section document
        content_parts = [f"# {section_name}"]

        if summary_markdown:
            content_parts.append("\n## Section Summary\n")
            content_parts.append(summary_markdown)

        # Process modules in the section
        modules = section.get("modules", [])
        if modules:
            content_parts.append("\n## Section Activities\n")

        for module in modules:
            module_name = module.get("name", "Unnamed Module")
            module_type = module.get("modname", "")
            module_description = module.get("description", "")
            module_url = module.get("url", "")

            content_parts.append(f"\n### {module_name}")
            content_parts.append(f"\n**Type:** {module_type}")

            if module_url:
                content_parts.append(f"\n**URL:** [{module_url}]({module_url})")

            if module_description:
                description_markdown = self.convert_html_to_markdown(
                    module_description
                )
                if description_markdown:
                    content_parts.append(f"\n{description_markdown}")

            # List files if present
            if "contents" in module:
                files = [
                    c for c in module.get("contents", []) if c.get("type") == "file"
                ]
                if files:
                    content_parts.append("\n**Files:**")
                    for file in files:
                        filename = file.get("filename", "")
                        fileurl = file.get("fileurl", "")
                        filesize = file.get("filesize", 0)
                        filesize_mb = filesize / (1024 * 1024)
                        content_parts.append(
                            f"- [{filename}]({fileurl}) ({filesize_mb:.2f} MB)"
                        )

        # Combine all parts
        full_content = "\n".join(content_parts)

        return {
            "section_id": section.get("id"),
            "section_name": section_name,
            "section_number": section.get("section", 0),
            "content": full_content,
            "modules": modules,
            "file_count": sum(
                1
                for m in modules
                if "contents" in m
                for c in m.get("contents", [])
                if c.get("type") == "file"
            ),
        }

    def extract_files_from_section(
        self, section: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract all downloadable files from a section.

        Args:
            section: Section data from Moodle API

        Returns:
            List of file information dictionaries
        """
        files = []
        section_name = section.get("name", "Unnamed Section")

        for module in section.get("modules", []):
            module_name = module.get("name", "Unnamed Module")
            module_id = module.get("id")

            if "contents" in module:
                for content in module.get("contents", []):
                    if content.get("type") == "file":
                        files.append(
                            {
                                "filename": content.get("filename", ""),
                                "fileurl": content.get("fileurl", ""),
                                "filesize": content.get("filesize", 0),
                                "mimetype": content.get("mimetype", ""),
                                "timecreated": content.get("timecreated", 0),
                                "timemodified": content.get("timemodified", 0),
                                "section_name": section_name,
                                "module_name": module_name,
                                "module_id": module_id,
                            }
                        )

        return files


class MoodleSync:
    """Sync class for Moodle integration - compatible with BaseSync interface."""

    name = "Moodle"
    lower_name = "moodle"

    def get_files(
        self, credentials: Dict, folder_id: str | None = None, recursive: bool = False
    ) -> List[SyncFile]:
        """
        Get list of Moodle courses or course sections.

        Args:
            credentials: Dict with 'wstoken' key
            folder_id: If None, returns courses. If provided, returns sections of that course.
            recursive: Not applicable for Moodle

        Returns:
            List of SyncFile objects representing courses or sections
        """
        wstoken = credentials.get("wstoken")
        if not wstoken:
            logger.error("No wstoken found in credentials")
            return []

        moodle_url = credentials.get("moodle_url")
        if not moodle_url:
            logger.error("No moodle_url found in credentials")
            return []

        # If no folder_id, return top-level courses
        if not folder_id:
            logger.info("Getting Moodle courses")
            return self._get_courses(credentials, moodle_url, wstoken)

        # If folder_id is provided, return sections of that course
        else:
            logger.info(f"Getting sections for course {folder_id}")
            return self._get_course_sections(credentials, moodle_url, wstoken, folder_id)

    def _get_courses(self, credentials: Dict, moodle_url: str, wstoken: str) -> List[SyncFile]:
        """Get list of enrolled courses."""
        endpoint = f"{moodle_url.rstrip('/')}/webservice/rest/server.php"
        params = {
            "wstoken": wstoken,
            "wsfunction": "core_enrol_get_users_courses",
            "moodlewsrestformat": "json",
            "userid": credentials.get("user_id", ""),
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            courses = response.json()

            if isinstance(courses, dict) and "exception" in courses:
                logger.error(f"Moodle API error: {courses}")
                return []

            logger.info(f"Found {len(courses)} Moodle courses")

            sync_files = []
            for course in courses:
                course_id = str(course.get("id", ""))
                course_name = course.get("fullname", course.get("shortname", "Unnamed Course"))

                timestamp = course.get("timemodified", course.get("timecreated", 0))
                if timestamp:
                    last_modified_str = datetime.fromtimestamp(timestamp).isoformat()
                else:
                    last_modified_str = datetime.now().isoformat()

                sync_file = SyncFile(
                    name=course_name,
                    id=course_id,
                    is_folder=True,  # Courses are folders containing sections
                    last_modified=last_modified_str,
                    mime_type="application/x-moodle-course",
                    web_view_link=f"{moodle_url}/course/view.php?id={course_id}",
                )
                sync_files.append(sync_file)

            return sync_files

        except Exception as e:
            logger.error(f"Error fetching Moodle courses: {e}")
            return []

    def _get_course_sections(self, credentials: Dict, moodle_url: str, wstoken: str, course_id: str) -> List[SyncFile]:
        """Get sections of a specific course as individual files."""
        try:
            course_id_int = int(course_id)
            service = SyncMoodleService()
            sections = service.get_course_contents(moodle_url, wstoken, course_id_int)

            logger.info(f"Found {len(sections)} sections in course {course_id}")

            sync_files = []
            for section in sections:
                section_id = section.get("id")
                section_name = section.get("name", "Unnamed Section")
                section_number = section.get("section", 0)

                # Create unique ID: course_id:section_id
                file_id = f"{course_id}:{section_id}"

                # Use section's summary or modules to determine last modified
                # For now, use current time as fallback
                last_modified_str = datetime.now().isoformat()

                # Create SyncFile for this section as a file (not folder)
                sync_file = SyncFile(
                    name=f"Section {section_number}: {section_name}.md",
                    id=file_id,
                    is_folder=False,  # Sections are files, not folders
                    last_modified=last_modified_str,
                    mime_type="application/x-moodle-section",
                    web_view_link=f"{moodle_url}/course/view.php?id={course_id}#section-{section_number}",
                )
                sync_files.append(sync_file)

            return sync_files

        except Exception as e:
            logger.error(f"Error fetching course sections: {e}")
            return []

    async def aget_files(
        self,
        credentials: Dict,
        folder_id: str | None = None,
        recursive: bool = False,
        sync_user_id: int | None = None,
    ) -> List[SyncFile]:
        """Async version of get_files."""
        return self.get_files(credentials, folder_id, recursive)

    def get_files_by_id(self, credentials: Dict, file_ids: List[str]) -> List[SyncFile]:
        """Get specific courses by ID (not implemented yet)."""
        logger.warning("get_files_by_id not yet implemented for Moodle")
        return []

    async def aget_files_by_id(
        self, credentials: Dict, file_ids: List[str]
    ) -> List[SyncFile]:
        """Async version of get_files_by_id."""
        return self.get_files_by_id(credentials, file_ids)

    def check_and_refresh_access_token(self, credentials: dict) -> Dict:
        """Moodle tokens don't expire, so just return credentials."""
        return credentials

    def download_file(
        self, credentials: Dict, file: SyncFile
    ) -> Dict[str, Union[str, BytesIO]]:
        """
        Download Moodle section content and convert to markdown.

        For sections, this fetches the section content and converts it to markdown.
        """
        wstoken = credentials.get("wstoken")
        moodle_url = credentials.get("moodle_url")

        if not wstoken or not moodle_url:
            logger.error("Missing wstoken or moodle_url in credentials")
            return {"file_name": file.name, "content": BytesIO(b"")}

        # If it's a section, download it as markdown
        if file.mime_type == "application/x-moodle-section":
            try:
                # Parse course_id and section_id from file.id (format: "course_id:section_id")
                parts = file.id.split(":")
                if len(parts) != 2:
                    logger.error(f"Invalid section ID format: {file.id}")
                    return {"file_name": file.name, "content": BytesIO(b"")}

                course_id = int(parts[0])
                section_id = int(parts[1])

                logger.info(f"Downloading section {section_id} from course {course_id}")

                # Create service instance for processing
                service = SyncMoodleService()

                # Get all course contents
                sections = service.get_course_contents(moodle_url, wstoken, course_id)

                # Find the specific section
                target_section = None
                for section in sections:
                    if section.get("id") == section_id:
                        target_section = section
                        break

                if not target_section:
                    logger.error(f"Section {section_id} not found in course {course_id}")
                    return {"file_name": file.name, "content": BytesIO(b"")}

                # Process the section to markdown
                section_data = service.process_section_content(target_section, f"Course {course_id}")

                # Create markdown content
                markdown_content = []
                markdown_content.append(f"**Course Section**: {file.web_view_link}\n\n")
                markdown_content.append(section_data["content"])

                # Add metadata at the end
                markdown_content.append(f"\n\n---\n\n")
                markdown_content.append(f"**Files in this section**: {section_data['file_count']}\n")
                markdown_content.append(f"**Modules**: {len(section_data['modules'])}\n")

                # Combine content
                full_markdown = "\n".join(markdown_content)

                # Convert to BytesIO
                content_bytes = full_markdown.encode("utf-8")
                content_io = BytesIO(content_bytes)

                # The filename is already included in file.name (e.g., "Section 1: Introduction.md")
                logger.info(f"Generated markdown for section: {file.name} ({len(content_bytes)} bytes)")

                return {"file_name": file.name, "content": content_io}

            except Exception as e:
                logger.error(f"Error downloading Moodle section content: {e}")
                return {"file_name": file.name, "content": BytesIO(b"")}
        else:
            # For other types (actual files), not yet implemented
            logger.warning(f"Download of file type {file.mime_type} not yet implemented: {file.name}")
            return {"file_name": file.name, "content": BytesIO(b"")}

    async def adownload_file(
        self, credentials: Dict, file: SyncFile
    ) -> Dict[str, Union[str, BytesIO]]:
        """Async version of download_file."""
        return self.download_file(credentials, file)
