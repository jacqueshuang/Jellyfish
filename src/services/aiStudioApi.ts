import { get, post, put, del } from './http'
import type {
  Project,
  Chapter,
  Shot,
  ShotDetail,
  Asset,
  PromptTemplate,
  FileItem,
  TimelineClip,
} from '../mocks/data'

const api = {
  projects: {
    list: () => get<Project[]>('/projects'),
    get: (id: string) => get<Project>(`/projects/${id}`),
    create: (data: Partial<Project> & { name: string }) => post<Project>('/projects', data),
    update: (id: string, data: Partial<Project>) => put<Project>(`/projects/${id}`, data),
    delete: (id: string) => del<void>(`/projects/${id}`),
  },
  chapters: {
    list: (projectId: string) => get<Chapter[]>(`/projects/${projectId}/chapters`),
  },
  shots: {
    list: (chapterId: string) => get<Shot[]>(`/chapters/${chapterId}/shots`),
    get: (shotId: string) => get<ShotDetail>(`/shots/${shotId}`),
  },
  assets: {
    list: (type?: string) =>
      get<Asset[]>(type ? `/assets?type=${type}` : '/assets'),
  },
  prompts: {
    templates: () => get<PromptTemplate[]>('/prompts/templates'),
  },
  files: {
    list: () => get<FileItem[]>('/files'),
  },
  timeline: {
    get: (projectId: string) =>
      get<TimelineClip[]>(`/projects/${projectId}/timeline`),
  },
}

export default api
