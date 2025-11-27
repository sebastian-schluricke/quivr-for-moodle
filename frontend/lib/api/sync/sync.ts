import { AxiosInstance } from "axios";
import { UUID } from "crypto";

import {
  ActiveSync,
  OpenedConnection,
  Provider,
  Sync,
  SyncElement,
  SyncElements,
} from "./types";

// Moodle course response types
interface MoodleCourse {
  id: number;
  fullname: string;
  shortname: string;
  displayname?: string;
}

interface MoodleCoursesResponse {
  courses: MoodleCourse[];
  moodle_url: string;
  sync_id: number;
}

// Moodle section/files response types
interface MoodleFile {
  filename: string;
  fileurl: string;
  filesize: number;
  mimetype: string;
}

interface MoodleModule {
  id: number;
  name: string;
  type: string;
  url: string;
  description: string;
  files: MoodleFile[];
  visible: number;
}

interface MoodleSection {
  id: number;
  name: string;
  summary: string;
  section_number: number;
  visible: number;
  modules: MoodleModule[];
}

interface MoodleCourseFilesResponse {
  course_id: number;
  sections: MoodleSection[];
  total_sections: number;
  total_files: number;
}

const createFilesSettings = (files: SyncElement[]) =>
  files.filter((file) => !file.is_folder).map((file) => file.id);

const createFoldersSettings = (files: SyncElement[]) =>
  files.filter((file) => file.is_folder).map((file) => file.id);

export const syncGoogleDrive = async (
  name: string,
  axiosInstance: AxiosInstance
): Promise<{ authorization_url: string }> => {
  return (
    await axiosInstance.post<{ authorization_url: string }>(
      `/sync/google/authorize?name=${name}`
    )
  ).data;
};

export const syncSharepoint = async (
  name: string,
  axiosInstance: AxiosInstance
): Promise<{ authorization_url: string }> => {
  return (
    await axiosInstance.post<{ authorization_url: string }>(
      `/sync/azure/authorize?name=${name}`
    )
  ).data;
};

export const syncDropbox = async (
  name: string,
  axiosInstance: AxiosInstance
): Promise<{ authorization_url: string }> => {
  return (
    await axiosInstance.post<{ authorization_url: string }>(
      `/sync/dropbox/authorize?name=${name}`
    )
  ).data;
};

export const syncNotion = async (
  name: string,
  axiosInstance: AxiosInstance
): Promise<{ authorization_url: string }> => {
  return (
    await axiosInstance.post<{ authorization_url: string }>(
      `/sync/notion/authorize?name=${name}`
    )
  ).data;
};

export const syncMoodle = async (
  name: string,
  axiosInstance: AxiosInstance
): Promise<{ authorization_url: string }> => {
  return (
    await axiosInstance.post<{ authorization_url: string }>(
      `/sync/moodle/authorize?name=${name}`
    )
  ).data;
};

export const getUserSyncs = async (
  axiosInstance: AxiosInstance
): Promise<Sync[]> => {
  return (await axiosInstance.get<Sync[]>("/sync")).data;
};

export const getSyncFiles = async (
  axiosInstance: AxiosInstance,
  userSyncId: number,
  folderId?: string,
  provider?: Provider
): Promise<SyncElements> => {
  // For Moodle, use special endpoints and transform the response
  if (provider === "Moodle") {
    if (!folderId) {
      // Initial call - get courses as folders
      const response = await axiosInstance.get<MoodleCoursesResponse>(
        `/sync/moodle/courses`
      );

      // Transform Moodle courses to SyncElements format
      const courses = response.data.courses || [];
      const files: SyncElement[] = courses.map((course) => ({
        id: String(course.id),
        name: course.displayname || course.fullname || course.shortname,
        is_folder: true,
        // Don't set icon - let the component use the default folder icon
      }));

      return { files };
    } else {
      // Subsequent call - get course contents (folderId is the course_id)
      const response = await axiosInstance.get<MoodleCourseFilesResponse>(
        `/sync/moodle/${userSyncId}/files?course_id=${folderId}`
      );

      // Transform Moodle sections/modules to SyncElements format
      const sections = response.data.sections || [];
      const files: SyncElement[] = [];

      for (const section of sections) {
        // Add section as a folder
        files.push({
          id: `section_${section.id}`,
          name: section.name || `Section ${section.section_number}`,
          is_folder: true,
          // Don't set icon - let the component use the default folder icon
        });

        // Add modules/files within the section
        for (const module of section.modules || []) {
          // Add module files
          for (const file of module.files || []) {
            files.push({
              id: `file_${section.id}_${module.id}_${file.filename}`,
              name: `${module.name} - ${file.filename}`,
              is_folder: false,
              // Don't set icon - let the component use the default file icon
            });
          }

          // If module has URL but no files, add as a link item
          if ((module.files?.length === 0 || !module.files) && module.url) {
            files.push({
              id: `module_${section.id}_${module.id}`,
              name: `${module.name} (${module.type})`,
              is_folder: false,
              // Don't set icon - let the component use the default file icon
            });
          }
        }
      }

      return { files };
    }
  }

  // Default behavior for other providers
  const url = folderId
    ? `/sync/${userSyncId}/files?user_sync_id=${userSyncId}&folder_id=${folderId}`
    : `/sync/${userSyncId}/files?user_sync_id=${userSyncId}`;

  return (await axiosInstance.get<SyncElements>(url)).data;
};

export const syncFiles = async (
  axiosInstance: AxiosInstance,
  openedConnection: OpenedConnection,
  brainId: UUID
): Promise<void> => {
  return (
    await axiosInstance.post<void>(`/sync/active`, {
      name: openedConnection.name,
      syncs_user_id: openedConnection.user_sync_id,
      settings: {
        files: createFilesSettings(openedConnection.selectedFiles.files),
        folders: createFoldersSettings(openedConnection.selectedFiles.files),
      },
      brain_id: brainId,
    })
  ).data;
};

export const updateActiveSync = async (
  axiosInstance: AxiosInstance,
  openedConnection: OpenedConnection
): Promise<void> => {
  return (
    await axiosInstance.put<void>(`/sync/active/${openedConnection.id}`, {
      name: openedConnection.name,
      settings: {
        files: createFilesSettings(openedConnection.selectedFiles.files),
        folders: createFoldersSettings(openedConnection.selectedFiles.files),
      },
      last_synced: openedConnection.last_synced,
    })
  ).data;
};

export const deleteActiveSync = async (
  axiosInstance: AxiosInstance,
  syncId: number
): Promise<void> => {
  await axiosInstance.delete<void>(`/sync/active/${syncId}`);
};

export const getActiveSyncs = async (
  axiosInstance: AxiosInstance
): Promise<ActiveSync[]> => {
  return (await axiosInstance.get<ActiveSync[]>(`/sync/active`)).data;
};

export const deleteUserSync = async (
  axiosInstance: AxiosInstance,
  syncId: number
): Promise<void> => {
  return (await axiosInstance.delete<void>(`/sync/${syncId}`)).data;
};
