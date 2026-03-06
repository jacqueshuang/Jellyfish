import React, { useEffect, useState } from 'react'
import { Card, Tabs, Input, Row, Col, Tag, Button, message } from 'antd'
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons'
import api from '../../../services/aiStudioApi'
import type { Asset } from '../../../mocks/data'

const typeLabels: Record<string, string> = {
  actor: '演员',
  scene: '场景',
  prop: '道具',
  costume: '服装',
}

const AssetManager: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<string>('actor')
  const [search, setSearch] = useState('')

  const load = async () => {
    try {
      const list = await api.assets.list()
      setAssets(Array.isArray(list) ? list : [])
    } catch {
      message.error('加载资产失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const list = Array.isArray(assets) ? assets : []
  const filtered = search
    ? list.filter(
        (a) =>
          a.name.toLowerCase().includes(search.toLowerCase()) ||
          a.description.toLowerCase().includes(search.toLowerCase()) ||
          a.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()))
        )
    : list

  const byType = (type: string) => filtered.filter((a) => a.type === type)

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Input.Search
          placeholder="搜索名称、描述或标签"
          allowClear
          className="max-w-sm"
          onSearch={setSearch}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Button type="primary" icon={<PlusOutlined />}>
          新建资产
        </Button>
      </div>

      <Card loading={loading}>
        <Tabs
          activeKey={activeTab}
          onChange={(k) => setActiveTab(k)}
          items={['actor', 'scene', 'prop', 'costume'].map((type) => ({
            key: type,
            label: typeLabels[type] || type,
            children: (
              <Row gutter={[16, 16]}>
                {byType(type).length === 0 ? (
                  <Col span={24}>
                    <div className="text-center text-gray-500 py-8">
                      {search ? '无匹配资产' : '暂无该类资产'}
                    </div>
                  </Col>
                ) : (
                  byType(type).map((a) => (
                    <Col xs={24} sm={12} md={8} lg={6} key={a.id}>
                      <Card
                        hoverable
                        size="small"
                        cover={
                          <div className="h-32 bg-gray-100 flex items-center justify-center text-gray-400">
                            缩略图
                          </div>
                        }
                        actions={[
                          <Button
                            type="text"
                            key="edit"
                            icon={<EditOutlined />}
                            size="small"
                          />,
                          <Button
                            type="text"
                            key="del"
                            danger
                            icon={<DeleteOutlined />}
                            size="small"
                          />,
                        ]}
                      >
                        <Card.Meta
                          title={a.name}
                          description={
                            <div className="line-clamp-2 text-gray-600 text-sm">
                              {a.description}
                            </div>
                          }
                        />
                        <div className="mt-2 flex flex-wrap gap-1">
                          {a.tags.slice(0, 3).map((t) => (
                            <Tag key={t}>{t}</Tag>
                          ))}
                        </div>
                      </Card>
                    </Col>
                  ))
                )}
              </Row>
            ),
          }))}
        />
      </Card>
    </div>
  )
}

export default AssetManager
