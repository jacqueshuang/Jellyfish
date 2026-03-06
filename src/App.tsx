import React from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'
import ProjectLobby from './pages/aiStudio/project/ProjectLobby'
import ProjectWorkbench from './pages/aiStudio/project/ProjectWorkbench'
import ChapterManagement from './pages/aiStudio/chapter/ChapterManagement'
import ChapterStudio from './pages/aiStudio/chapter/ChapterStudio'
import AssetManager from './pages/aiStudio/assets/AssetManager'
import PromptTemplateManager from './pages/aiStudio/prompts/PromptTemplateManager'
import FileManager from './pages/aiStudio/files/FileManager'
import VideoEditor from './pages/aiStudio/editor/VideoEditor'
import './App.css'

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/projects" replace />} />
          <Route path="projects" element={<ProjectLobby />} />
          <Route path="projects/:projectId" element={<ProjectWorkbench />} />
          <Route path="projects/:projectId/chapters" element={<ChapterManagement />} />
          <Route path="projects/:projectId/chapters/:chapterId/studio" element={<ChapterStudio />} />
          <Route path="projects/:projectId/editor" element={<VideoEditor />} />
          <Route path="assets" element={<AssetManager />} />
          <Route path="prompts" element={<PromptTemplateManager />} />
          <Route path="files" element={<FileManager />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

