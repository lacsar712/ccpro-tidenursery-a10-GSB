import { FormEvent, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { BroodstockCage, Hatchery } from '../types'

const empty = { hatcheryId: 0, cageCode: '', capacity: 100 }

export default function BroodstockCages() {
  const [hatcheries, setHatcheries] = useState<Hatchery[]>([])
  const [rows, setRows] = useState<BroodstockCage[]>([])
  const [form, setForm] = useState(empty)
  const [error, setError] = useState('')

  async function load() {
    const [hs, cs] = await Promise.all([
      api<Hatchery[]>('/api/hatcheries'),
      api<BroodstockCage[]>('/api/broodstock-cages'),
    ])
    setHatcheries(hs)
    setRows(cs)
    if (!form.hatcheryId && hs[0]) {
      setForm((f) => ({ ...f, hatcheryId: hs[0].id }))
    }
  }

  useEffect(() => {
    load().catch((e) => setError(e.message))
  }, [])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api('/api/broodstock-cages', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      setForm((f) => ({ ...empty, hatcheryId: f.hatcheryId }))
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    }
  }

  async function stock(id: number, direction: 'in' | 'out') {
    const label = direction === 'in' ? '入笼' : '出笼'
    const raw = prompt(`请输入${label}尾数（正整数）`)
    if (raw === null) return
    const count = Number(raw)
    if (!Number.isInteger(count) || count <= 0) {
      setError(`${label}尾数必须为正整数`)
      return
    }
    setError('')
    try {
      await api(`/api/broodstock-cages/${id}/stock-${direction}`, {
        method: 'POST',
        body: JSON.stringify({ count }),
      })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : `${label}失败`)
    }
  }

  async function toggleActive(cage: BroodstockCage) {
    const action = cage.isActive ? '停用' : '启用'
    if (!confirm(`确认${action}笼位 ${cage.cageCode}？`)) return
    setError('')
    try {
      await api(`/api/broodstock-cages/${cage.id}`, {
        method: 'PUT',
        body: JSON.stringify({ isActive: !cage.isActive }),
      })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : `${action}失败`)
    }
  }

  const hatcheryName = (id: number) =>
    hatcheries.find((h) => h.id === id)?.name || `#${id}`

  return (
    <div>
      <header className="page-header">
        <h1>亲虾笼位</h1>
        <p className="muted">
          同场笼位号唯一；启用笼位有亲虾占用时，该场塘口单次投喂不得超过 2 kg
        </p>
      </header>
      {error && <div className="error">{error}</div>}

      <form className="panel form-grid" onSubmit={onSubmit}>
        <label>
          所属育苗场
          <select
            value={form.hatcheryId}
            onChange={(e) => setForm({ ...form, hatcheryId: Number(e.target.value) })}
            required
          >
            {hatcheries.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          笼位号
          <input
            value={form.cageCode}
            onChange={(e) => setForm({ ...form, cageCode: e.target.value })}
            required
          />
        </label>
        <label>
          容纳尾数
          <input
            type="number"
            step="1"
            min="1"
            value={form.capacity}
            onChange={(e) => setForm({ ...form, capacity: Number(e.target.value) })}
            required
          />
        </label>
        <button type="submit" className="btn primary">
          新增笼位
        </button>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>育苗场</th>
              <th>笼位号</th>
              <th>容纳尾数</th>
              <th>当前占用</th>
              <th>状态</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{hatcheryName(r.hatcheryId)}</td>
                <td>{r.cageCode}</td>
                <td>{r.capacity}</td>
                <td>{r.occupied}</td>
                <td>
                  <span className={`badge ${r.isActive ? 'stocked' : 'dry'}`}>
                    {r.isActive ? '启用' : '停用'}
                  </span>
                </td>
                <td>
                  <button className="btn ghost" onClick={() => stock(r.id, 'in')}>
                    入笼
                  </button>{' '}
                  <button className="btn ghost" onClick={() => stock(r.id, 'out')}>
                    出笼
                  </button>{' '}
                  <button className="btn ghost" onClick={() => toggleActive(r)}>
                    {r.isActive ? '停用' : '启用'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
