import React, { useEffect, useState } from 'react'
import { Card, Tree, Input, Row, Col, Tag, message } from 'antd'
import type { DataNode } from 'antd/es/tree'
import api from '../../../services/aiStudioApi'
import type { PromptTemplate } from '../../../mocks/data'

const categoryLabels: Record<string, string> = {
  frame_head: '首帧',
  frame_tail: '尾帧',
  frame_key: '关键帧',
  video: '视频生成',
  storyboard: '分镜',
  bgm: '配乐',
  sfx: '音效',
  role: '角色',
  combined: '综合提示词',
}

const PromptTemplateManager: React.FC = () => {
  const [templates, setTemplates] = useState<PromptTemplate[]>([])
  const [selected, setSelected] = useState<PromptTemplate | null>(null)
  const [search, setSearch] = useState('')

  const load = async () => {
    try {
      const list = await api.prompts.templates()
      setTemplates(Array.isArray(list) ? list : [])
    } catch {
      message.error('加载模板失败')
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const list = Array.isArray(templates) ? templates : []
  const filtered = search
    ? list.filter(
        (t) =>
          t.name.toLowerCase().includes(search.toLowerCase()) ||
          t.preview.toLowerCase().includes(search.toLowerCase())
        )
    : list

  const treeData: DataNode[] = [
    {
      title: '首/尾/关键帧',
      key: 'frame',
      children: filtered
        .filter((t) =>
          ['frame_head', 'frame_tail', 'frame_key'].includes(t.category)
        )
        .map((t) => ({
          title: t.name,
          key: t.id,
          isLeaf: true,
        })),
    },
    {
      title: '视频生成 / 分镜',
      key: 'video',
      children: filtered
        .filter((t) => ['video', 'storyboard'].includes(t.category))
        .map((t) => ({
          title: t.name,
          key: t.id,
          isLeaf: true,
        })),
    },
    {
      title: '配乐 / 音效 / 角色',
      key: 'other',
      children: filtered
        .filter((t) => ['bgm', 'sfx', 'role'].includes(t.category))
        .map((t) => ({
          title: t.name,
          key: t.id,
          isLeaf: true,
        })),
    },
    {
      title: '综合提示词',
      key: 'combined',
      children: filtered
        .filter((t) => t.category === 'combined')
        .map((t) => ({
          title: t.name,
          key: t.id,
          isLeaf: true,
        })),
    },
  ]

  const onSelect = (_: React.Key[], info: { node: { key: React.Key } }) => {
    const id = String(info.node.key)
    const t = templates.find((x) => x.id === id)
    setSelected(t || null)
  }

  return (
    <div className="space-y-4">
      <Card title="提示词模板管理">
        <Input.Search
          placeholder="搜索模板名称或预览"
          allowClear
          className="mb-4 max-w-md"
          onSearch={setSearch}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Row gutter={16}>
          <Col xs={24} md={10}>
            <Tree
              showLine
              defaultExpandAll
              treeData={treeData}
              onSelect={onSelect}
              fieldNames={{ title: 'title', key: 'key', children: 'children' }}
            />
          </Col>
          <Col xs={24} md={14}>
            {selected ? (
              <Card title={selected.name} size="small">
                <Tag>{categoryLabels[selected.category] || selected.category}</Tag>
                <p className="text-gray-600 text-sm mt-2">{selected.preview}</p>
                <pre className="mt-3 p-3 bg-gray-50 rounded text-xs overflow-auto max-h-48">
                  {selected.content}
                </pre>
                {selected.variables.length > 0 && (
                  <div className="mt-2 text-xs text-gray-500">
                    变量：{selected.variables.join(', ')}
                  </div>
                )}
              </Card>
            ) : (
              <Card>
                <div className="text-gray-500 text-center py-8">
                  左侧选择模板查看详情
                </div>
              </Card>
            )}
          </Col>
        </Row>
      </Card>
    </div>
  )
}

export default PromptTemplateManager
