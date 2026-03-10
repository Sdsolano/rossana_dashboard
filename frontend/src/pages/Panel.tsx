import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

interface DayAgenda {
  date: string
  label: string
  meets: { id: number; number: number; status: string }[]
  locked: boolean
}

interface MeResponse {
  therapist: { id: number; username: string; first_name: string; last_name: string }
  days: DayAgenda[]
}

const STATUS_LABEL: Record<string, string> = {
  D: "Confirmado",
  P: "Presente",
  A: "Ausente",
  C: "Cancelado",
}

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: "D", label: "Confirmado" },
  { value: "P", label: "Presente" },
  { value: "A", label: "Ausente" },
  { value: "C", label: "Cancelado" },
]

export default function Panel() {
  const { token, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [data, setData] = useState<MeResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [savingMeetId, setSavingMeetId] = useState<number | null>(null)

  const reload = () => {
    if (!token) return
    fetch("/api/me/", { headers: { Authorization: `Token ${token}` } })
      .then((r) => {
        if (r.status === 401) {
          logout()
          navigate("/login")
          return null
        }
        return r.json()
      })
      .then((d) => {
        if (d) setData(d)
        setError(d?.detail || null)
      })
      .catch(() => setError("Error al cargar"))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!isAuthenticated || !token) {
      navigate("/login")
      return
    }
    reload()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, token, navigate, logout])

  const updateMeetStatus = (meetId: number, newStatus: string) => {
    if (!token) return
    setSavingMeetId(meetId)
    fetch(`/api/meets/${meetId}/`, {
      method: "PATCH",
      headers: {
        Authorization: `Token ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status: newStatus }),
    })
      .then((r) => r.json().then((data) => ({ status: r.status, data })))
      .then(({ status }) => {
        if (status === 200) {
          reload()
        } else {
          setError("Error al actualizar cita")
        }
      })
      .catch(() => setError("Error de conexión"))
      .finally(() => setSavingMeetId(null))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando…</p>
  if (error && !data) return <p className="p-6 text-red-600">{error}</p>
  if (!data) return null

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-gray-800">
          Panel — {data.therapist.first_name} {data.therapist.last_name}
        </h1>
        <div className="flex gap-3">
          <Link
            to="/panel/availability"
            className="px-4 py-2 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50"
          >
            Mi disponibilidad
          </Link>
          <button
            type="button"
            onClick={() => {
              logout()
              navigate("/login")
            }}
            className="px-4 py-2 text-red-600 border border-red-200 rounded font-medium hover:bg-red-50"
          >
            Cerrar sesión
          </button>
        </div>
      </div>

      <h2 className="text-lg font-medium text-gray-700 mb-3">Próximos 7 días</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.days.map((day) => (
          <div
            key={day.date}
            className={`border rounded-lg p-4 ${
              day.locked ? "bg-amber-50 border-amber-200" : "bg-white border-gray-200"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-800">{day.label}</span>
              {day.locked && (
                <span className="text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded">
                  Bloqueado
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500 mb-2">{day.date}</p>
            {day.meets.length === 0 ? (
              <p className="text-sm text-gray-400">Sin citas confirmadas</p>
            ) : (
              <ul className="text-sm text-gray-700 space-y-2">
                {day.meets.map((m) => (
                  <li key={m.id} className="flex items-center justify-between gap-2">
                    <span>
                      Cita #{m.number} —{" "}
                      <span className="text-gray-600">
                        {STATUS_LABEL[m.status] || m.status}
                      </span>
                    </span>
                    <select
                      value={m.status}
                      onChange={(e) => updateMeetStatus(m.id, e.target.value)}
                      disabled={savingMeetId === m.id}
                      className="border border-gray-300 rounded px-2 py-1 text-xs bg-white"
                    >
                      {STATUS_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
