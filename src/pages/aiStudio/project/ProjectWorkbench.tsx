import React, { useEffect, useState } from 'react'
import {
  Card,
  Button,
  Tag,
  Statistic,
  Row,
  Col,
  Progress,
  Tabs,
  Space,
  Dropdown,
  Table,
  Modal,
  Input,
  message,
  Empty,
  Spin,
} from 'antd'
import type { MenuProps } from 'antd'
import type { TableColumnsType } from 'antd'
import {
  HomeOutlined,
  UnorderedListOutlined,
  UserOutlined,
  PictureOutlined,
  ScissorOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  SettingOutlined,
  PlusOutlined,
  EllipsisOutlined,
  ArrowLeftOutlined,
  VideoCameraFilled,
  RiseOutlined,
} from '@ant-design/icons'
import { Link, useParams, useNavigate } from 'react-router-dom'
import api from '../../../services/aiStudioApi'
import { projects as mockProjects, chapters as mockChapters, type Project, type Chapter } from '../../../mocks/data'

const { TextArea } = Input

type TabKey = 'dashboard' | 'chapters' | 'roles' | 'scenes' | 'props' | 'files' | 'edit' | 'settings'

const TAB_CONFIG: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'dashboard', label: '仪表盘', icon: <HomeOutlined /> },
  { key: 'chapters', label: '章节', icon: <UnorderedListOutlined /> },
  { key: 'roles', label: '角色', icon: <UserOutlined /> },
  { key: 'scenes', label: '场景', icon: <PictureOutlined /> },
  { key: 'props', label: '道具/服装', icon: <ScissorOutlined /> },
  { key: 'files', label: '文件', icon: <FileImageOutlined /> },
  { key: 'edit', label: '剪辑', icon: <VideoCameraOutlined /> },
  { key: 'settings', label: '设置', icon: <SettingOutlined /> },
]


const chapterStatusMap: Record<Chapter['status'], { color: string; text: string }> = {
  draft: { color: 'default', text: '草稿' },
  shooting: { color: 'processing', text: '拍摄中' },
  done: { color: 'success', text: '完成' },
}

const ProjectWorkbench: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard')
  const [createChapterOpen, setCreateChapterOpen] = useState(false)
  const [createTitle, setCreateTitle] = useState('')
  const [createContent, setCreateContent] = useState('')

  const load = async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const [proj, list] = await Promise.all([
        api.projects.get(projectId),
        api.chapters.list(projectId),
      ])
      const resolvedProject = proj && typeof proj === 'object' && 'id' in proj ? proj : null
      const resolvedChapters = Array.isArray(list) ? list : []
      setProject(resolvedProject ?? mockProjects.find((p) => p.id === projectId) ?? null)
      setChapters(resolvedChapters.length > 0 ? resolvedChapters : mockChapters.filter((c) => c.projectId === projectId))
    } catch {
      const useMock = import.meta.env.VITE_USE_MOCK === 'true'
      if (useMock) {
        setProject(mockProjects.find((p) => p.id === projectId) ?? null)
        setChapters(mockChapters.filter((c) => c.projectId === projectId))
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [projectId])

  const handleCreateChapter = () => {
    if (!createTitle.trim()) {
      message.warning('请输入章节标题')
      return
    }
    message.success('创建成功（Mock）')
    setCreateChapterOpen(false)
    setCreateTitle('')
    setCreateContent('')
    void load()
  }

  const incompleteChapters = chapters.filter((c) => c.status !== 'done')
  const latestInProgressChapter = chapters.find((c) => c.status === 'shooting') ?? incompleteChapters[0]

  const moreMenuItems: MenuProps['items'] = [
    { key: 'newRole', label: '新建角色', onClick: () => setActiveTab('roles') },
    { key: 'upload', label: '上传素材', onClick: () => navigate('/assets') },
    { key: 'newScene', label: '新建场景', onClick: () => setActiveTab('scenes') },
    { key: 'newProp', label: '新建道具', onClick: () => setActiveTab('props') },
  ]

  if (!project && !loading) {
    return (
      <Card>
        <Empty description="项目不存在" />
        <Link to="/projects">
          <Button type="link" icon={<ArrowLeftOutlined />}>返回项目列表</Button>
        </Link>
      </Card>
    )
  }

  return (
    <div className="space-y-0">
      {/* 项目专属顶部区域 Sticky */}
      <div
        className="sticky top-0 z-20 bg-white border-b border-gray-200 shadow-sm"
        style={{ margin: -5, marginBottom: 0, padding: '16px 24px' }}
      >

        {/* Tab 导航 + 右侧快速操作 */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-gray-100">
          <Tabs
            activeKey={activeTab}
            onChange={(k) => setActiveTab(k as TabKey)}
            size="middle"
            className="project-workbench-tabs flex-1 min-w-0"
            items={TAB_CONFIG.map(({ key, label, icon }) => ({
              key,
              label: (
                <span className="flex items-center gap-1.5">
                  {icon}
                  {label}
                </span>
              ),
            }))}
          />
          <Space size="small" wrap className="shrink-0">
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateChapterOpen(true)}>
              新建章节
            </Button>
            {latestInProgressChapter ? (
              <Button
                icon={<VideoCameraOutlined />}
                onClick={() =>
                  navigate(`/projects/${projectId}/chapters/${latestInProgressChapter.id}/studio`)
                }
              >
                继续拍摄{chapters.length > 0 ? `第${latestInProgressChapter.index}章` : ''}
              </Button>
            ) : (
              <Button icon={<VideoCameraOutlined />} disabled>
                继续拍摄
              </Button>
            )}
            <Button
              icon={<VideoCameraFilled />}
              onClick={() => navigate(`/projects/${projectId}/editor`)}
            >
              进入后期剪辑
            </Button>
            <Dropdown menu={{ items: moreMenuItems }} placement="bottomRight">
              <Button icon={<EllipsisOutlined />}>更多</Button>
            </Dropdown>
          </Space>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="pt-4 animate-fadeIn" style={{ animation: 'fadeIn 0.25s ease-out' }}>
        {activeTab === 'dashboard' && (
          project ? (
            <DashboardTab
              project={project}
              chapters={chapters}
              latestChapter={latestInProgressChapter}
              onNavigateChapters={() => setActiveTab('chapters')}
              onNavigateChapterStudio={(chapterId) =>
                navigate(`/projects/${projectId}/chapters/${chapterId}/studio`)
              }
              onNavigateEditor={() => navigate(`/projects/${projectId}/editor`)}
              onNavigateChaptersPage={() => navigate(`/projects/${projectId}/chapters`)}
              onNavigateAssets={() => navigate('/assets')}
            />
          ) : (
            <div className="flex justify-center items-center py-16">
              <Spin size="large" tip="加载中…" />
            </div>
          )
        )}
        {activeTab === 'chapters' && (
          <ChaptersTab
            chapters={chapters}
            loading={loading}
            onOpenCreate={() => setCreateChapterOpen(true)}
            onEnterStudio={(chapterId) =>
              navigate(`/projects/${projectId}/chapters/${chapterId}/studio`)
            }
            onManageChapters={() => navigate(`/projects/${projectId}/chapters`)}
          />
        )}
        {activeTab === 'roles' && (
          <PlaceholderTab
            title="角色管理"
            description="管理项目角色与立绘，支持筛选「缺少立绘」「缺少提示词」。"
            actionLabel="前往资产管理"
            onAction={() => navigate('/assets')}
          />
        )}
        {activeTab === 'scenes' && (
          <PlaceholderTab
            title="场景管理"
            description="管理场景资源，支持按室内/室外/特殊分类。"
            actionLabel="前往资产管理"
            onAction={() => navigate('/assets')}
          />
        )}
        {activeTab === 'props' && (
          <PlaceholderTab
            title="道具 / 服装"
            description="合并管理道具与服装，支持按类别过滤。"
            actionLabel="前往资产管理"
            onAction={() => navigate('/assets')}
          />
        )}
        {activeTab === 'files' && (
          <PlaceholderTab
            title="生成文件"
            description="生成的图片/视频素材库，支持标签过滤、批量标记、导出。"
            actionLabel="前往文件管理"
            onAction={() => navigate('/files')}
          />
        )}
        {activeTab === 'edit' && (
          <PlaceholderTab
            title="后期剪辑"
            description="时间线编辑器，或从可剪辑章节列表进入。"
            actionLabel="进入后期剪辑"
            onAction={() => navigate(`/projects/${projectId}/editor`)}
          />
        )}
        {activeTab === 'settings' && (
          <PlaceholderTab
            title="项目设置"
            description="项目基础信息、全局风格/种子、协作成员、删除项目等。"
            actionLabel="前往系统设置"
            onAction={() => navigate('/settings')}
          />
        )}
      </div>

      {/* 新建章节 Modal */}
      <Modal
        title="新建章节"
        open={createChapterOpen}
        onCancel={() => setCreateChapterOpen(false)}
        onOk={handleCreateChapter}
        okText="创建"
        width={560}
      >
        <div className="space-y-3">
          <div>
            <span className="text-gray-600 text-sm">章节标题</span>
            <Input
              placeholder="例如：第1集 出租屋里的争吵"
              value={createTitle}
              onChange={(e) => setCreateTitle(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <span className="text-gray-600 text-sm">章节内容（可粘贴剧本）</span>
            <TextArea
              rows={6}
              placeholder="粘贴文学剧本..."
              value={createContent}
              onChange={(e) => setCreateContent(e.target.value)}
              className="mt-1 font-mono text-sm"
            />
          </div>
        </div>
      </Modal>
    </div>
  )
}

function DashboardTab({
  project,
  chapters,
  latestChapter,
  onNavigateChapters,
  onNavigateChapterStudio,
  onNavigateEditor,
  onNavigateChaptersPage,
  onNavigateAssets,
}: {
  project: Project
  chapters: Chapter[]
  latestChapter: Chapter | undefined
  onNavigateChapters: () => void
  onNavigateChapterStudio: (chapterId: string) => void
  onNavigateEditor: () => void
  onNavigateChaptersPage: () => void
  onNavigateAssets: () => void
}) {
  const totalShots = chapters.reduce((s, c) => s + c.storyboardCount, 0)
  const completedShots = Math.round((totalShots * project.progress) / 100)
  const incompleteCount = chapters.filter((c) => c.status !== 'done').length

  return (
    <div className="space-y-6">
      {/* 快速动作 */}
      <Card size="small">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="min-w-0">
            <div className="font-medium">快速开始</div>
            <div className="text-xs text-gray-500">
              {latestChapter
                ? `继续拍摄：第${latestChapter.index}章（${latestChapter.title}）`
                : '暂无进行中的章节，可先创建章节或进入章节管理'}
            </div>
          </div>
          <Space wrap>
            <Button onClick={onNavigateChapters}>创建/管理章节</Button>
            <Button onClick={onNavigateEditor}>进入后期剪辑</Button>
            <Button
              type="primary"
              icon={<VideoCameraOutlined />}
              disabled={!latestChapter}
              onClick={() => latestChapter && onNavigateChapterStudio(latestChapter.id)}
            >
              继续拍摄
            </Button>
          </Space>
        </div>
      </Card>

      {/* KPI 卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" className="h-full">
            <Statistic title="未完成章节" value={incompleteCount} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" className="h-full">
            <Statistic
              title="已生成片段/总分镜"
              value={completedShots}
              suffix={`/ ${totalShots}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" className="h-full">
            <Statistic title="资产覆盖率" value={76} suffix="%" />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" className="h-full">
            <Statistic
              title="整体进度"
              value={project.progress}
              suffix="%"
              prefix={<RiseOutlined />}
            />
            <Progress
              percent={project.progress}
              showInfo={false}
              size="small"
              strokeColor={{ from: '#6366f1', to: '#a855f7' }}
              className="mt-1"
            />
          </Card>
        </Col>
      </Row>

      {/* 章节进度模块：可水平滚动的章节卡片 */}
      <Card title="章节进度" size="small" extra={<Button type="link" onClick={onNavigateChaptersPage}>查看全部</Button>}>
        <div className="flex gap-3 overflow-x-auto pb-2" style={{ minHeight: 140 }}>
          {chapters.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-gray-500 py-8">
              还没有任何章节，<Button type="link" className="p-0" onClick={onNavigateChapters}>立即创建第一章</Button>
            </div>
          ) : (
            chapters.slice(0, 8).map((ch) => (
              <Card
                key={ch.id}
                size="small"
                hoverable
                className="shrink-0 cursor-pointer"
                style={{ width: 280 }}
                onClick={() => onNavigateChapterStudio(ch.id)}
              >
                <div className="font-medium truncate">第{ch.index}集 {ch.title}</div>
                <Tag color={chapterStatusMap[ch.status].color} className="mt-1">
                  {chapterStatusMap[ch.status].text}
                </Tag>
                <div className="text-xs text-gray-500 mt-1">分镜 {ch.storyboardCount} · {ch.updatedAt}</div>
              </Card>
            ))
          )}
        </div>
      </Card>

      {/* 最近活动 + 资产健康 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={14}>
          <Card title="最近活动" size="small">
            <ul className="list-none pl-0 m-0 space-y-2 text-sm text-gray-600">
              <li>· 生成第5章第12镜参考图</li>
              <li>· 更新第3章分镜脚本</li>
              <li>· 完成第2章拍摄</li>
            </ul>
            <Button type="link" className="p-0 mt-2">查看更多</Button>
          </Card>
        </Col>
        <Col xs={24} md={10}>
          <Card title="资产健康快照" size="small">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>角色</span>
                <span className="text-gray-500">{project.stats.roles} 项</span>
              </div>
              <Progress percent={80} size="small" showInfo={false} />
              <div className="flex justify-between text-sm">
                <span>场景</span>
                <span className="text-gray-500">{project.stats.scenes} 项</span>
              </div>
              <Progress percent={60} size="small" showInfo={false} />
              <div className="flex justify-between text-sm">
                <span>道具</span>
                <span className="text-gray-500">{project.stats.props} 项</span>
              </div>
              <Progress percent={75} size="small" showInfo={false} />
            </div>
            <Button type="link" className="p-0 mt-2" onClick={onNavigateAssets}>管理资产</Button>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

function ChaptersTab({
  chapters,
  loading,
  onOpenCreate,
  onEnterStudio,
  onManageChapters,
}: {
  chapters: Chapter[]
  loading: boolean
  onOpenCreate: () => void
  onEnterStudio: (chapterId: string) => void
  onManageChapters: () => void
}) {
  const columns: TableColumnsType<Chapter> = [
    { title: '章节', dataIndex: 'index', key: 'index', width: 80, render: (v: number) => `第${v}集` },
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
    { title: '分镜数', dataIndex: 'storyboardCount', key: 'storyboardCount', width: 90 },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: Chapter['status']) => (
        <Tag color={chapterStatusMap[status].color}>{chapterStatusMap[status].text}</Tag>
      ),
    },
    { title: '更新时间', dataIndex: 'updatedAt', key: 'updatedAt', width: 160 },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button type="link" size="small" icon={<VideoCameraOutlined />} onClick={() => onEnterStudio(record.id)}>
          进入拍摄
        </Button>
      ),
    },
  ]

  if (chapters.length === 0 && !loading) {
    return (
      <Card>
        <Empty
          description="还没有任何章节，立即创建第一章吧"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Space>
            <Button type="primary" size="large" icon={<PlusOutlined />} onClick={onOpenCreate}>
              创建第一章
            </Button>
            <Button onClick={onManageChapters}>查看章节管理页</Button>
          </Space>
        </Empty>
      </Card>
    )
  }

  return (
    <Card
      title="章节列表"
      extra={
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={onOpenCreate}>
            新建章节
          </Button>
          <Button onClick={onManageChapters}>管理章节</Button>
        </Space>
      }
    >
      <Table<Chapter>
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={chapters}
        pagination={{ pageSize: 10 }}
        size="small"
      />
    </Card>
  )
}

function PlaceholderTab({
  title,
  description,
  actionLabel,
  onAction,
}: {
  title: string
  description: string
  actionLabel: string
  onAction: () => void
}) {
  return (
    <Card>
      <Empty
        description={
          <div className="text-left">
            <div className="font-medium text-gray-900 mb-1">{title}</div>
            <p className="text-gray-500 text-sm mb-3">{description}</p>
            <Button type="primary" onClick={onAction}>
              {actionLabel}
            </Button>
          </div>
        }
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      />
    </Card>
  )
}

export default ProjectWorkbench
