import { useState } from 'react'
import LinkPage from './pages/LinkPage'
import StatusPage from './pages/StatusPage'
import './index.css'

export default function App() {
  const [childInfo, setChildInfo] = useState(() => {
    const s = localStorage.getItem('child_info')
    return s ? JSON.parse(s) : null
  })

  const handleLinked = (info) => {
    localStorage.setItem('child_info', JSON.stringify(info))
    setChildInfo(info)
  }

  const handleUnlink = () => {
    localStorage.removeItem('child_info')
    setChildInfo(null)
  }

  return childInfo
    ? <StatusPage childInfo={childInfo} onUnlink={handleUnlink} />
    : <LinkPage onLinked={handleLinked} />
}
